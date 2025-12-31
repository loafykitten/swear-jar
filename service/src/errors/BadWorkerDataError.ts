export class BadWorkerDataError extends Error {
	constructor(data: any) {
		super(`Bad event.data: ${JSON.stringify(data)}`)
	}
}
