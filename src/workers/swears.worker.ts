import { logger } from '@/utils/logger'

declare var self: Worker

self.onmessage = (event: MessageEvent) => {
	logger.log(`Swears Worker: ${JSON.stringify(event.data)}`)
	self.postMessage(event.data)
}
