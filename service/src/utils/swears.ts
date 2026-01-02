export const getPricePerSwear = (param: string) => {
	const value = parseFloat(param)
	console.log(value)
	if (Number.isNaN(value) || !Number.isFinite(value) || value < 0) {
		return undefined
	}
	return value
}

export const calculateSwearsCost = (swears: number, pricePerSwear: number) => {
	return Math.round(swears * pricePerSwear * 100) / 100
}
