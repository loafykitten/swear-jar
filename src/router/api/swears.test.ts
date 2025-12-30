import { test, expect, describe, beforeEach, mock } from "bun:test"
import { SwearsRoutingAPI } from "./swears"
import { resetSwears } from "../../data/swears-store"

// Mock worker
const mockWorker = {
	postMessage: mock(() => {}),
} as unknown as Worker

const createRequest = (method: string, params: Record<string, string> = {}) => {
	const url = new URL("http://localhost:3000/api/swears")
	for (const [key, value] of Object.entries(params)) {
		url.searchParams.set(key, value)
	}
	return new Request(url.toString(), { method })
}

describe("SwearsRoutingAPI", () => {
	beforeEach(() => {
		resetSwears()
		mockWorker.postMessage = mock(() => {})
	})

	test("isMatch returns true for /api/swears", () => {
		const url = new URL("http://localhost:3000/api/swears")
		expect(SwearsRoutingAPI.isMatch(url)).toBe(true)
	})

	test("isMatch returns false for other paths", () => {
		const url = new URL("http://localhost:3000/api/other")
		expect(SwearsRoutingAPI.isMatch(url)).toBe(false)
	})

	describe("GET /api/swears", () => {
		test("returns swears and cost with valid params", async () => {
			const req = createRequest("GET", { pricePerSwear: "0.25" })
			const url = new URL(req.url)
			const clientIp = `test-get-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(response.status).toBe(200)

			const data = await response.json()
			expect(data.swears).toBe(0)
			expect(data.cost).toBe(0)
		})

		test("returns 400 for missing pricePerSwear", () => {
			const req = createRequest("GET", {})
			const url = new URL(req.url)
			const clientIp = `test-get-400-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(response.status).toBe(400)
		})

		test("returns 400 for invalid pricePerSwear", () => {
			const req = createRequest("GET", { pricePerSwear: "abc" })
			const url = new URL(req.url)
			const clientIp = `test-get-invalid-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(response.status).toBe(400)
		})
	})

	describe("POST /api/swears", () => {
		test("increments count with updateType=increment", async () => {
			const req = createRequest("POST", { updateType: "increment", pricePerSwear: "0.25" })
			const url = new URL(req.url)
			const clientIp = `test-post-inc-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(response.status).toBe(200)

			const data = await response.json()
			expect(data.swears).toBe(1)
			expect(data.cost).toBe(0.25)
		})

		test("decrements count with updateType=decrement", async () => {
			// First increment to 1
			const req1 = createRequest("POST", { updateType: "increment", pricePerSwear: "0.25" })
			SwearsRoutingAPI.processRequest(req1, mockWorker, new URL(req1.url), `test-dec-1-${crypto.randomUUID()}`)

			// Then decrement
			const req2 = createRequest("POST", { updateType: "decrement", pricePerSwear: "0.25" })
			const url = new URL(req2.url)
			const clientIp = `test-post-dec-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req2, mockWorker, url, clientIp)
			expect(response.status).toBe(200)

			const data = await response.json()
			expect(data.swears).toBe(0)
		})

		test("returns 400 for invalid updateType", () => {
			const req = createRequest("POST", { updateType: "invalid", pricePerSwear: "0.25" })
			const url = new URL(req.url)
			const clientIp = `test-post-invalid-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(response.status).toBe(400)
		})

		test("notifies worker on update", () => {
			const req = createRequest("POST", { updateType: "increment", pricePerSwear: "0.25" })
			const url = new URL(req.url)
			const clientIp = `test-post-worker-${crypto.randomUUID()}`

			SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(mockWorker.postMessage).toHaveBeenCalled()
		})

		test("returns 400 and does not mutate state for invalid pricePerSwear", async () => {
			// First add a swear
			const setupReq = createRequest("POST", { updateType: "increment", pricePerSwear: "0.25" })
			SwearsRoutingAPI.processRequest(setupReq, mockWorker, new URL(setupReq.url), `setup-${crypto.randomUUID()}`)

			// Get current count
			const getReq1 = createRequest("GET", { pricePerSwear: "0.25" })
			const before = await SwearsRoutingAPI.processRequest(getReq1, mockWorker, new URL(getReq1.url), `get1-${crypto.randomUUID()}`).json()

			// Try POST with invalid price
			const req = createRequest("POST", { updateType: "increment", pricePerSwear: "invalid" })
			const response = SwearsRoutingAPI.processRequest(req, mockWorker, new URL(req.url), `test-${crypto.randomUUID()}`)
			expect(response.status).toBe(400)

			// Verify count unchanged
			const getReq2 = createRequest("GET", { pricePerSwear: "0.25" })
			const after = await SwearsRoutingAPI.processRequest(getReq2, mockWorker, new URL(getReq2.url), `get2-${crypto.randomUUID()}`).json()
			expect(after.swears).toBe(before.swears)
		})
	})

	describe("DELETE /api/swears", () => {
		test("resets count to 0", async () => {
			// First add some swears
			const req1 = createRequest("POST", { updateType: "increment", pricePerSwear: "0.25" })
			SwearsRoutingAPI.processRequest(req1, mockWorker, new URL(req1.url), `test-del-setup-${crypto.randomUUID()}`)

			// Then reset
			const req = createRequest("DELETE")
			const url = new URL(req.url)
			const clientIp = `test-delete-${crypto.randomUUID()}`

			const response = SwearsRoutingAPI.processRequest(req, mockWorker, url, clientIp)
			expect(response.status).toBe(200)

			// Verify count is 0
			const getReq = createRequest("GET", { pricePerSwear: "0.25" })
			const getResponse = SwearsRoutingAPI.processRequest(getReq, mockWorker, new URL(getReq.url), `test-del-verify-${crypto.randomUUID()}`)
			const data = await getResponse.json()
			expect(data.swears).toBe(0)
		})
	})

	describe("Rate limiting", () => {
		test("returns 429 when rate limit exceeded", () => {
			const clientIp = `rate-limit-test-${crypto.randomUUID()}`

			// Make 30 requests (the limit)
			for (let i = 0; i < 30; i++) {
				const req = createRequest("GET", { pricePerSwear: "0.25" })
				SwearsRoutingAPI.processRequest(req, mockWorker, new URL(req.url), clientIp)
			}

			// 31st request should be rate limited
			const req = createRequest("GET", { pricePerSwear: "0.25" })
			const response = SwearsRoutingAPI.processRequest(req, mockWorker, new URL(req.url), clientIp)
			expect(response.status).toBe(429)
		})
	})
})
