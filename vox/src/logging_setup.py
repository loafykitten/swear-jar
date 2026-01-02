"""Logging configuration for Vox."""

import logging
import os

# Suppress tokenizers parallelism warning
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Configure file logging
logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s [%(levelname)s] %(message)s',
	handlers=[
		logging.FileHandler('vox_debug.log', mode='w'),
	],
)


def get_logger(name: str) -> logging.Logger:
	"""Get a logger instance for the given module name."""
	return logging.getLogger(name)
