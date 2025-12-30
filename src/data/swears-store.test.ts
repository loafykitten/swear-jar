import { test, expect, describe, beforeEach } from "bun:test"
import { getSwears, incrementSwears, decrementSwears, resetSwears } from "./swears-store"

describe("swears-store", () => {
	beforeEach(() => {
		// Reset to known state before each test
		resetSwears()
	})

	test("getSwears returns current count", () => {
		expect(getSwears()).toBe(0)
	})

	test("incrementSwears increases count by 1", () => {
		expect(incrementSwears()).toBe(true)
		expect(getSwears()).toBe(1)

		expect(incrementSwears()).toBe(true)
		expect(getSwears()).toBe(2)
	})

	test("decrementSwears decreases count by 1", () => {
		incrementSwears()
		incrementSwears()
		expect(getSwears()).toBe(2)

		expect(decrementSwears()).toBe(true)
		expect(getSwears()).toBe(1)
	})

	test("decrementSwears doesn't go below 0", () => {
		expect(getSwears()).toBe(0)
		expect(decrementSwears()).toBe(false)
		expect(getSwears()).toBe(0)
	})

	test("resetSwears sets count to 0", () => {
		incrementSwears()
		incrementSwears()
		incrementSwears()
		expect(getSwears()).toBe(3)

		expect(resetSwears()).toBe(true)
		expect(getSwears()).toBe(0)
	})
})
