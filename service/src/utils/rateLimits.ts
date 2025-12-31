const connectionCounts = new Map<string, number>()
const requestTimestamps = new Map<string, number[]>()

const MAX_WS_CONNECTIONS_PER_IP = 2
const MAX_REQUESTS_PER_MINUTE = 30

export const checkWsRateLimit = (ip: string): boolean => {
	const count = connectionCounts.get(ip) ?? 0
	if (count >= MAX_WS_CONNECTIONS_PER_IP) return false
	connectionCounts.set(ip, count + 1)
	return true
}

export const releaseWsConnection = (ip: string) => {
	const count = connectionCounts.get(ip) ?? 1
	if (count <= 1) connectionCounts.delete(ip)
	else connectionCounts.set(ip, count - 1)
}

export const checkApiRateLimit = (ip: string): boolean => {
	const now = Date.now()
	const windowStart = now - 60000

	let timestamps = requestTimestamps.get(ip)

	if (timestamps) {
		timestamps = timestamps.filter(t => t > windowStart)

		// Clean up stale entries
		if (timestamps.length === 0) {
			requestTimestamps.delete(ip)
			timestamps = []
		}
	} else {
		timestamps = []
	}

	if (timestamps.length >= MAX_REQUESTS_PER_MINUTE) return false

	timestamps.push(now)
	requestTimestamps.set(ip, timestamps)
	return true
}
