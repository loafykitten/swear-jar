import type { SwearsResponse } from '@/types/SwearsResponse'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useURLParams } from './useURLParams'

export const useSwearsData = () => {
	const { configParams, swearsParams } = useURLParams()
	const [swearsData, setSwearsData] = useState<SwearsResponse>()
	const wsConnection = useRef<WebSocket | undefined>(undefined)
	const hasConnected = useRef(false)

	const getSwearsData = useCallback(async () => {
		try {
			const url = new URL(
				`${window.location.protocol}//${window.location.host}/api/swears`,
			)
			url.searchParams.append(
				'pricePerSwear',
				`${swearsParams.pricePerSwear}`,
			)
			url.searchParams.append('apiKey', configParams.apiKey)

			const response = await fetch(url)
			if (!response.ok) throw new Error(`HTTP ${response.status}`)
			return response.json() as Promise<SwearsResponse>
		} catch (ex) {
			console.error(ex)
		}
	}, [configParams, swearsParams])

	const connectWs = useCallback(() => {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
		const url = new URL(`${protocol}//${window.location.host}/ws/swears`)
		url.searchParams.append(
			'pricePerSwear',
			`${swearsParams.pricePerSwear}`,
		)
		url.searchParams.append('apiKey', configParams.apiKey)

		wsConnection.current = new WebSocket(url)

		wsConnection.current.onopen = (_event: Event) => {
			console.log('Browser WS connection established')
		}

		wsConnection.current.onclose = (_event: CloseEvent) => {
			console.log('Browser WS connection closed')
		}

		wsConnection.current.onerror = (event: Event) => {
			console.error('Browser WS error:')
			console.error(JSON.stringify(event))
		}

		wsConnection.current.onmessage = (event: MessageEvent) => {
			console.log('Browser WS message received:')
			let data: SwearsResponse | undefined
			if (event.data) {
				try {
					data = JSON.parse(event.data)
				} catch (ex) {
					console.error(ex)
				}
			}

			console.log(data)
			if (data) setSwearsData(data)
		}
	}, [configParams, swearsParams])

	useEffect(() => {
		if (hasConnected.current) return
		hasConnected.current = true

		getSwearsData().then(res => {
			if (res) setSwearsData(res)
		})

		connectWs()

		return () => {
			if (wsConnection.current) {
				wsConnection.current.close()
				wsConnection.current = undefined
			}

			hasConnected.current = false
		}
	}, [])

	return { swearsData, maxCost: swearsParams.maxCost }
}
