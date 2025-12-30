import { useState } from 'react'

type ConfigParams = {
	apiKey: string
	isAnimated: boolean
}

type SwearsParams = {
	pricePerSwear: number
	maxCost: number
}

export const useURLParams = () => {
	const params = new URLSearchParams(window.location.search)

	const [configParams] = useState<ConfigParams>(() => {
		return {
			apiKey: params.get('apiKey') ?? '',
			isAnimated: params.get('isAnimated') === 'true',
		}
	})

	const [swearsParams] = useState<SwearsParams>(() => {
		const price = parseFloat(params.get('pricePerSwear') ?? '')
		const max = parseInt(params.get('maxCost') ?? '')
		return {
			pricePerSwear: isNaN(price) ? 0.25 : price,
			maxCost: isNaN(max) ? 100 : max,
		}
	})

	return {
		configParams,
		swearsParams,
	}
}
