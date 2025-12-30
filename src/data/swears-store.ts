
import { db } from './db'

class SwearsSchema {
	count: number = 0
}

export const getSwears = () => {
	using query = db.query('SELECT * FROM Swears WHERE id = 1').as(SwearsSchema)
	const data = query.get()

	return data?.count
}

const updateSwears = (by: number) => {
	const result = db.query(
      `UPDATE Swears SET count = count + ? WHERE id = 1 AND count + ? >= 0`
    ).run(by, by)

	return result.changes !== 0
}

export const incrementSwears = () => {
	return updateSwears(1)
}

export const decrementSwears = () => {
	return updateSwears(-1)
}

export const resetSwears = () => {
	const result = db.query(`UPDATE Swears SET count = 0 WHERE id = 1`).run()

	return result.changes !== 0
}
