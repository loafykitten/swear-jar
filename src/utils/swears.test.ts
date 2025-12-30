import { test, expect, describe } from "bun:test"
import { getPricePerSwear, calculateSwearsCost } from "./swears"

describe("getPricePerSwear", () => {
	test("returns number for valid positive string", () => {
		expect(getPricePerSwear("0.25")).toBe(0.25)
		expect(getPricePerSwear("1")).toBe(1)
		expect(getPricePerSwear("10.50")).toBe(10.5)
	})

	test("returns undefined for zero", () => {
		expect(getPricePerSwear("0")).toBeUndefined()
	})

	test("returns undefined for negative numbers", () => {
		expect(getPricePerSwear("-1")).toBeUndefined()
		expect(getPricePerSwear("-0.25")).toBeUndefined()
	})

	test("returns undefined for non-numeric strings", () => {
		expect(getPricePerSwear("abc")).toBeUndefined()
		expect(getPricePerSwear("")).toBeUndefined()
	})

	test("parses leading numbers from mixed strings", () => {
		// parseFloat behavior - parses until non-numeric char
		expect(getPricePerSwear("12abc")).toBe(12)
	})

	test("returns undefined for Infinity", () => {
		expect(getPricePerSwear("Infinity")).toBeUndefined()
	})
})

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
