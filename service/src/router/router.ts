import type { BunRequest, Server } from 'bun'

import type { WebSocketData } from '@/types/WebSocketData'
import { logger } from '@/utils/logger'
import index from '../app/index.html'
import { SwearsRoutingAPI } from './api/swears'
import { SwearsRoutingWS } from './ws/swears'

export const registerRoutes = (swearsWorker: Worker) => {
	return {
		routes: {
			'/swears': index,
		},
		fetch(req: BunRequest, server: Server<WebSocketData>) {
			const clientIp = server.requestIP(req)?.address ?? 'unknown'
			const url = new URL(req.url)

			const apiKey =
				url.searchParams.get('apiKey') ??
				req.headers.get('API-KEY') ??
				''

			if (apiKey !== process.env.API_KEY) {
				logger.warn('Unauthorized access attempt')
				return new Response('Unauthorized', { status: 401 })
			}

			if (SwearsRoutingAPI.isMatch(url)) {
				return SwearsRoutingAPI.processRequest(
					req,
					swearsWorker,
					url,
					clientIp,
				)
			}

			if (SwearsRoutingWS.isMatch(url)) {
				return SwearsRoutingWS.processRequest(
					req,
					server,
					url,
					clientIp,
				)
			}

			return defaultResponse
		},
	}
}

export const defaultResponse = new Response('What da fuk r u doin?? o.O', {
	status: 404,
})
