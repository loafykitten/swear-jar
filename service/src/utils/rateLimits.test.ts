import { test, expect, describe, beforeEach } from "bun:test"
import { checkWsRateLimit, releaseWsConnection, checkApiRateLimit } from "./rateLimits"

describe("checkWsRateLimit", () => {
	test("allows first connection", () => {
		const ip = `ws-test-${crypto.randomUUID()}`
		expect(checkWsRateLimit(ip)).toBe(true)
	})

	test("allows second connection from same IP", () => {
		const ip = `ws-test-${crypto.randomUUID()}`
		expect(checkWsRateLimit(ip)).toBe(true)
		expect(checkWsRateLimit(ip)).toBe(true)
	})

	test("blocks third connection from same IP", () => {
		const ip = `ws-test-${crypto.randomUUID()}`
		expect(checkWsRateLimit(ip)).toBe(true)
		expect(checkWsRateLimit(ip)).toBe(true)
		expect(checkWsRateLimit(ip)).toBe(false)
	})
})

describe("releaseWsConnection", () => {
	test("allows new connection after release", () => {
		const ip = `release-test-${crypto.randomUUID()}`
		checkWsRateLimit(ip)
		checkWsRateLimit(ip)
		expect(checkWsRateLimit(ip)).toBe(false) // at limit

		releaseWsConnection(ip)
		expect(checkWsRateLimit(ip)).toBe(true) // slot freed
	})
})

describe("checkApiRateLimit", () => {
	test("allows requests under limit", () => {
		const ip = `api-test-${crypto.randomUUID()}`
		for (let i = 0; i < 30; i++) {
			expect(checkApiRateLimit(ip)).toBe(true)
		}
	})

	test("blocks requests at limit", () => {
		const ip = `api-limit-${crypto.randomUUID()}`
		for (let i = 0; i < 30; i++) {
			checkApiRateLimit(ip)
		}
		expect(checkApiRateLimit(ip)).toBe(false)
	})
})
