import type { SwearsResponse } from '@/types/SwearsResponse'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useURLParams } from './useURLParams'

export const useSwearsData = () => {
	const { configParams, swearsParams } = useURLParams()
	const [swearsData, setSwearsData] = useState<SwearsResponse>()
	const [error, setError] = useState<string>()
	const wsConnection = useRef<WebSocket | undefined>(undefined)

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
			setError(undefined)
			return response.json() as Promise<SwearsResponse>
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Fetch failed'
			setError(message)
			return undefined
		}
	}, [configParams, swearsParams])

	const connectWs = useCallback(() => {
		// Close existing connection before reconnecting
		if (wsConnection.current) {
			wsConnection.current.close()
			wsConnection.current = undefined
		}

		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
		const url = new URL(`${protocol}//${window.location.host}/ws/swears`)
		url.searchParams.append(
			'pricePerSwear',
			`${swearsParams.pricePerSwear}`,
		)
		url.searchParams.append('apiKey', configParams.apiKey)

		wsConnection.current = new WebSocket(url)

		wsConnection.current.onopen = () => {
			setError(undefined)
		}

		wsConnection.current.onclose = () => {}

		wsConnection.current.onerror = () => {
			setError('WebSocket connection error')
		}

		wsConnection.current.onmessage = (event: MessageEvent) => {
			let data: SwearsResponse | undefined
			if (event.data) {
				try {
					data = JSON.parse(event.data)
				} catch {
					// Ignore malformed messages
				}
			}
			if (data) setSwearsData(data)
		}
	}, [configParams, swearsParams])

	// Reconnect when params change
	useEffect(() => {
		getSwearsData().then(res => {
			if (res) setSwearsData(res)
		})

		connectWs()

		return () => {
			if (wsConnection.current) {
				wsConnection.current.close()
				wsConnection.current = undefined
			}
		}
	}, [getSwearsData, connectWs])

	return { swearsData, maxCost: swearsParams.maxCost, error }
}
