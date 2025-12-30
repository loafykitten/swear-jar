import { logger } from '@/utils/logger'
import { Database } from 'bun:sqlite'

export const db = new Database('swears-db.sqlite')

export const initializeDb = () => {
	try {
		createDb()
		seedData()
	} catch (ex) {
		logger.error(
			'FATAL: Database initialization failed - server cannot start',
		)
		console.error(ex)
		process.exit(1)
	}
}

const createDb = () => {
	logger.log('Running database initializations...')

	db.query(
		`
		CREATE TABLE IF NOT EXISTS Swears (
			id INTEGER PRIMARY KEY CHECK(id = 1),
			count INTEGER NOT NULL DEFAULT 0 CHECK(count >= 0)
		)
		`,
	).run()
}

const seedData = () => {
	const result = db
		.query(
			`INSERT INTO Swears SELECT 1, 0 WHERE NOT EXISTS (SELECT * FROM Swears)`,
		)
		.run()

	if (result.changes > 0) logger.warn('Initialized Swears table!')
	else logger.log('Skipped initialization!')
}
