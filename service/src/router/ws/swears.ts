import type { WebSocketData } from '@/types/WebSocketData'
import { checkWsRateLimit } from '@/utils/rateLimits'
import { validatePricePerSwear } from '@/utils/validation'
import type { BunRequest, Server } from 'bun'

const validPaths = ['/ws/swears']

export const SwearsRoutingWS = {
	isMatch: (url: URL) => {
		if (!validPaths.includes(url.pathname)) return false
		return url.searchParams.has('pricePerSwear')
	},
	processRequest: (
		req: BunRequest,
		server: Server<WebSocketData>,
		url: URL,
		clientIp: string,
	): Response | undefined => {
		const priceResult = validatePricePerSwear(url)
		if (!priceResult.success) return priceResult.error

		if (!checkWsRateLimit(clientIp)) {
			return new Response('Too many connections', { status: 429 })
		}

		const data: WebSocketData = { pricePerSwear: priceResult.value, clientIp }
		if (server.upgrade(req, { data })) return

		return new Response('Upgrade failed', { status: 500 })
	},
}
