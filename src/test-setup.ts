// Set test environment before any imports
process.env.NODE_ENV = 'test'

import { initializeDb } from './data/db'

// Initialize test database
initializeDb()
