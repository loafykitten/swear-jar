import { styleText, type InspectColor } from 'node:util'

const generatePrefix = (prefixColor: InspectColor) => {
	const timestamp = new Intl.DateTimeFormat('en-US', {
		timeZone: 'America/Chicago',
		timeStyle: 'medium',
	}).format(new Date())

	return styleText(prefixColor, `[${timestamp}]`)
}

const innerLog = (info: string, prefixColor: InspectColor) =>
	console.log(`${generatePrefix(prefixColor)} ${info}`)

export const logger = {
	log: (info: string) => innerLog(info, 'green'),
	error: (info: string) => innerLog(info, 'red'),
	warn: (info: string) => innerLog(info, 'yellow'),
}
