import ProgressBar from '@/components/ProgressBar'
import { useSwearsData } from '@/hooks/useSwearsData'
import { useURLParams } from '@/hooks/useURLParams'
import './index.css'

export function App() {
	const { swearsData, maxCost } = useSwearsData()
	const { configParams } = useURLParams()

	return (
		<div className="app">
			{swearsData && (
				<ProgressBar
					{...swearsData}
					maxCost={maxCost}
					configParams={configParams}
				/>
			)}
		</div>
	)
}

export default App
