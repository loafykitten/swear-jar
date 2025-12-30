import type { WebSocketData } from './types/WebSocketData'

import { serve } from 'bun'
import { initializeDb } from './data/db'
import { registerRoutes } from './router/router'
import { registerWebsocket } from './router/websocket'
import { logger } from './utils/logger'

initializeDb()

const swearsWorker = new Worker('./src/workers/swears.worker.ts')
const { routes, fetch } = registerRoutes(swearsWorker)

const server = serve<WebSocketData>({
	routes,
	fetch,
	websocket: registerWebsocket(swearsWorker),

	development: process.env.NODE_ENV !== 'production' && {
		// Enable browser hot reloading in development
		hmr: true,

		// Echo console logs from the browser to the server
		console: true,
	},
})

logger.log(`🚀 Server running at ${server.url}`)
