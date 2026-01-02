export const calculateSwearsCost = (swears: number, pricePerSwear: number) => {
	return Math.round(swears * pricePerSwear * 100) / 100
}
