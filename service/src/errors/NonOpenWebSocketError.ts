export class NonOpenWebSocketError extends Error {
	constructor() {
		super(`WebSocket not open before sending`)
	}
}
