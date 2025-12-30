import ProgressBar from '@/components/ProgressBar'
import { useSwearsData } from '@/hooks/useSwearsData'
import './index.css'

export function App() {
	const { swearsData, maxCost } = useSwearsData()

	return (
		<div className="app">
			{swearsData && <ProgressBar {...swearsData} maxCost={maxCost} />}
		</div>
	)
}

export default App
