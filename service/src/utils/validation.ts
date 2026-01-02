import { logger } from '@/utils/logger'

type ValidationResult<T> =
	| { success: true; value: T }
	| { success: false; error: Response }

export const validatePricePerSwear = (url: URL): ValidationResult<number> => {
	const pricePerSwear = parseFloat(
		url.searchParams.get('pricePerSwear') || '',
	)
	if (
		Number.isNaN(pricePerSwear) ||
		!Number.isFinite(pricePerSwear) ||
		pricePerSwear < 0
	) {
		const response = 'pricePerSwear is malformed in API request'
		logger.warn(response)
		return {
			success: false,
			error: new Response(response, { status: 400 }),
		}
	}
	return { success: true, value: pricePerSwear }
}

export const validateByParam = (url: URL): ValidationResult<number> => {
	const by = parseFloat(url.searchParams.get('by') || '')
	if (Number.isNaN(by) || !Number.isFinite(by) || !Number.isInteger(by)) {
		const response = 'by must be an integer'
		logger.warn(response)
		return {
			success: false,
			error: new Response(response, { status: 400 }),
		}
	}
	return { success: true, value: by }
}
