import { test, expect, describe } from "bun:test"
import { calculateSwearsCost } from "./swears"

describe("calculateSwearsCost", () => {
	test("calculates correct cost", () => {
		expect(calculateSwearsCost(5, 0.25)).toBe(1.25)
		expect(calculateSwearsCost(10, 1)).toBe(10)
		expect(calculateSwearsCost(3, 0.50)).toBe(1.5)
	})

	test("rounds to 2 decimal places", () => {
		expect(calculateSwearsCost(3, 0.33)).toBe(0.99)
		expect(calculateSwearsCost(7, 0.07)).toBe(0.49)
	})

	test("handles zero swears", () => {
		expect(calculateSwearsCost(0, 0.25)).toBe(0)
	})
})
