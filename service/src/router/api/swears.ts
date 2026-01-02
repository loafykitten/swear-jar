import type { BunRequest } from 'bun'

import { logger } from '@/utils/logger'
import { checkApiRateLimit } from '@/utils/rateLimits'
import { calculateSwearsCost } from '@/utils/swears'
import { validateByParam, validatePricePerSwear } from '@/utils/validation'
import { getSwears, resetSwears, updateSwears } from '../../data/swears-store'
import { defaultResponse } from '../router'

const validPaths = ['/api/swears']

const finalizeRequest = (pricePerSwear: number) => {
	const swears = getSwears()
	if (swears === undefined) {
		return {
			response: new Response('Swears data malformed on backend', {
				status: 500,
			}),
			data: undefined,
		}
	}

	const swearsData = {
		swears,
		cost: calculateSwearsCost(swears, pricePerSwear),
	}

	logger.debug(
		`Swears Data - swears: ${swearsData.swears}, pricePerSwear: ${pricePerSwear}, cost: ${swearsData.cost}`,
	)

	return {
		response: Response.json(swearsData),
		data: swearsData,
	}
}

const GET = (req: BunRequest<'/api/swears'>, swearsWorker: Worker) => {
	logger.debug('SwearsAPI (GET)')

	const url = new URL(req.url)
	const priceResult = validatePricePerSwear(url)
	if (!priceResult.success) return priceResult.error

	return finalizeRequest(priceResult.value).response
}

const POST = (req: BunRequest<'/api/swears'>, swearsWorker: Worker) => {
	logger.debug('SwearsAPI (POST)')

	const url = new URL(req.url)

	const byResult = validateByParam(url)
	if (!byResult.success) return byResult.error

	const priceResult = validatePricePerSwear(url)
	if (!priceResult.success) return priceResult.error

	const result = updateSwears(byResult.value)

	if (!result) {
		const response = 'Cannot decrement swears below zero'
		logger.warn(response)
		return new Response(response, { status: 400 })
	}

	const response = finalizeRequest(priceResult.value)
	swearsWorker.postMessage(response.data)
	return response.response
}

const DELETE = (swearsWorker: Worker) => {
	logger.debug('SwearsAPI (DELETE)')

	if (resetSwears()) {
		logger.warn('Swears reset!')
		swearsWorker.postMessage({ swears: 0, cost: 0 })
		return new Response('OK')
	} else {
		logger.error('Issue occurred during reset!')
		return new Response('Issue occurred during reset!', { status: 500 })
	}
}

export const SwearsRoutingAPI = {
	isMatch: (url: URL) => {
		return validPaths.includes(url.pathname)
	},
	processRequest: (
		req: BunRequest,
		swearsWorker: Worker,
		_url: URL,
		clientIp: string,
	) => {
		if (!checkApiRateLimit(clientIp))
			return new Response('Rate limit exceeded', { status: 429 })

		switch (req.method.toUpperCase()) {
			case 'GET':
				return GET(req, swearsWorker)
			case 'POST':
				return POST(req, swearsWorker)
			case 'DELETE':
				return DELETE(swearsWorker)
			default:
				return defaultResponse
		}
	},
}
