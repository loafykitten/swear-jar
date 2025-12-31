import { BadWorkerDataError, NonOpenWebSocketError } from '@/errors'
import type { WebSocketData } from '@/types/WebSocketData'
import { logger } from '@/utils/logger'
import { releaseWsConnection } from '@/utils/rateLimits'
import { calculateSwearsCost } from '@/utils/swears'
import type { ServerWebSocket } from 'bun'

const onMessage = (
	ws: Bun.ServerWebSocket<WebSocketData>,
	message: string | Buffer<ArrayBuffer>,
) => {
	logger.error(
		`Sending data is an unintended use of the server, disconnecting client`,
	)
	ws.close()
}

const onOpen = (ws: Bun.ServerWebSocket<WebSocketData>) => {
	logger.log(
		`WS connection established, calculating swears at ${ws.data.pricePerSwear}`,
	)
}

const onClose = (
	ws: Bun.ServerWebSocket<WebSocketData>,
	code: number,
	reason: string,
) => {
	logger.debug(`WS connection closed - code: ${code}, reason: ${reason}`)
}

const onDrain = (ws: Bun.ServerWebSocket<WebSocketData>) => {
	logger.warn('WS connection drained')
}

const onWorkerMessage = (
	event: MessageEvent,
	ws: ServerWebSocket<WebSocketData>,
) => {
	logger.debug(`Websocket Thread (Worker msg recv)`)

	try {
		if (event.data.swears === undefined)
			throw new BadWorkerDataError(event.data)
		if (ws.readyState !== WebSocket.OPEN) throw new NonOpenWebSocketError()

		ws.send(
			JSON.stringify({
				swears: event.data.swears,
				cost: calculateSwearsCost(
					event.data.swears,
					ws.data.pricePerSwear,
				),
			}),
		)
	} catch (ex) {
		if (ex instanceof BadWorkerDataError)
			logger.error('FATAL: onWorkerMessage received bad data')
		else if (ex instanceof NonOpenWebSocketError)
			logger.error('FATAL: onWorkerMessage ws was not open for sending')
		else logger.error('FATAL: Unknown error occurred')

		console.error(ex)
		process.exit(1)
	}
}

export const registerWebsocket = (
	swearsWorker: Worker,
): Bun.WebSocketHandler<WebSocketData> => {
	const handlers = new WeakMap<
		ServerWebSocket<WebSocketData>,
		(event: MessageEvent) => void
	>()

	return {
		idleTimeout: 30,
		sendPings: true,
		message: onMessage,
		open: ws => {
			onOpen(ws)
			const handler = (event: MessageEvent) => onWorkerMessage(event, ws)
			handlers.set(ws, handler)
			swearsWorker.addEventListener('message', handler)
		},
		close: (ws, code, reason) => {
			releaseWsConnection(ws.data.clientIp)
			onClose(ws, code, reason)

			const handler = handlers.get(ws)
			if (handler) {
				swearsWorker.removeEventListener('message', handler)
				handlers.delete(ws)
			}
		},
		drain: onDrain,
	}
}
