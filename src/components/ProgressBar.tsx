import { useMemo } from 'react'

type Props = {
	swears: number
	cost: number
	maxCost: number
}

const costFormat = Intl.NumberFormat('en-US', {
	style: 'currency',
	currency: 'USD',
})

export default function ProgressBar({ swears, cost, maxCost }: Props) {
	const actualCost = costFormat.format(cost)
	const capCost = costFormat.format(maxCost)

	const progressValue = useMemo(() => {
		const value = (cost / maxCost) * 100
		return value <= 100 ? value : 100
	}, [cost, maxCost])

	return (
		<div
			className="progress-bar"
			role="progressbar"
			aria-valuenow={cost}
			aria-valuemin={0}
			aria-valuemax={maxCost}
			aria-label="Swear jar progress"
		>
			<div
				className="progress-bar-fill"
				style={{ width: `${progressValue}%` }}
			></div>
			<div className="progress-bar-label">
				<p className="swear-count">Swears this month: {swears}</p>

				{cost <= maxCost ? (
					<p className="swear-cost">Charity gets: {actualCost}</p>
				) : (
					<p className="swear-cost">
						Charity gets: {capCost} ({actualCost})
					</p>
				)}
			</div>
		</div>
	)
}
