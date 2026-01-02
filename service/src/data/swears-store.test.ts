import { test, expect, describe, beforeEach } from "bun:test"
import { getSwears, updateSwears, resetSwears } from "./swears-store"

describe("swears-store", () => {
	beforeEach(() => {
		// Reset to known state before each test
		resetSwears()
	})

	test("getSwears returns current count", () => {
		expect(getSwears()).toBe(0)
	})

	test("updateSwears increases count with positive value", () => {
		expect(updateSwears(1)).toBe(true)
		expect(getSwears()).toBe(1)

		expect(updateSwears(1)).toBe(true)
		expect(getSwears()).toBe(2)

		expect(updateSwears(3)).toBe(true)
		expect(getSwears()).toBe(5)
	})

	test("updateSwears decreases count with negative value", () => {
		updateSwears(2)
		expect(getSwears()).toBe(2)

		expect(updateSwears(-1)).toBe(true)
		expect(getSwears()).toBe(1)
	})

	test("updateSwears doesn't go below 0", () => {
		expect(getSwears()).toBe(0)
		expect(updateSwears(-1)).toBe(false)
		expect(getSwears()).toBe(0)
	})

	test("resetSwears sets count to 0", () => {
		updateSwears(3)
		expect(getSwears()).toBe(3)

		expect(resetSwears()).toBe(true)
		expect(getSwears()).toBe(0)
	})
})
