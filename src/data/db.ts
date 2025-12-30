import { logger } from '@/utils/logger'
import { Database } from 'bun:sqlite'

const isTest = process.env.NODE_ENV === 'test'
const dbPath = isTest ? ':memory:' : 'swears-db.sqlite'

export const db = new Database(dbPath)

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
	logger.debug('Running database initializations...')

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
	else logger.debug('Skipped initialization!')
}
