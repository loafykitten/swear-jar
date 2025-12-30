import type { RouteValidationResult } from '@/types/RouteValidationResult'
import type { WebSocketData } from '@/types/WebSocketData'
import { logger } from '@/utils/logger'
import { checkWsRateLimit } from '@/utils/rateLimits'
import { getPricePerSwear } from '@/utils/swears'
import type { BunRequest, Server } from 'bun'

const validPaths = ['/ws/swears']
const requiredParams = ['pricePerSwear']

const isValid = (url: URL): RouteValidationResult => {
	for (const param of requiredParams) {
		const value = url.searchParams.get(param) as string
		switch (param) {
			case 'pricePerSwear':
				if (getPricePerSwear(value) === undefined)
					return { param, isValid: false }
				break
		}
	}

	return { isValid: true }
}

export const SwearsRoutingWS = {
	isMatch: (url: URL) => {
		if (!validPaths.includes(url.pathname)) return false

		for (const param of requiredParams) {
			if (!url.searchParams.has(param)) return false
		}

		return true
	},
	processRequest: (
		req: BunRequest,
		server: Server<WebSocketData>,
		url: URL,
		clientIp: string,
	): Response | undefined => {
		const result = isValid(url)
		if (!result.isValid) {
			const response = `${result.param} is malformed in API request`

			logger.log(response)
			return new Response(response, {
				status: 400,
			})
		}

		if (!checkWsRateLimit(clientIp)) {
			return new Response('Too many connections', { status: 429 })
		}

		const pricePerSwear = getPricePerSwear(
			url.searchParams.get('pricePerSwear') as string,
		) as number

		const data: WebSocketData = { pricePerSwear, clientIp }
		if (server.upgrade(req, { data })) return

		return new Response('Upgrade failed', { status: 500 })
	},
}
