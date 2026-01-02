"""Swear word detection module."""

import re
from pathlib import Path

from logging_setup import get_logger

log = get_logger(__name__)


class SwearDetector:
	"""Detects swear words in text using a configurable word list."""

	def __init__(self, word_list_path: str | Path):
		"""Initialize detector with a word list file.

		Args:
			word_list_path: Path to text file with one swear word per line.

		Raises:
			FileNotFoundError: If word list file does not exist.
		"""
		self.word_list_path = Path(word_list_path)
		self._swear_words: set[str] = set()
		self._load_word_list()

	def _load_word_list(self) -> None:
		"""Load swear words from file."""
		if not self.word_list_path.exists():
			raise FileNotFoundError(
				f'Word list file not found: {self.word_list_path}'
			)

		with open(self.word_list_path, 'r', encoding='utf-8') as f:
			for line in f:
				word = line.strip().lower()
				if word and not word.startswith('#'):
					self._swear_words.add(word)

		log.info(
			f'Loaded {len(self._swear_words)} swear words from {self.word_list_path}'
		)

	def detect(self, text: str) -> tuple[int, list[str]]:
		"""Detect swear words in text.

		Args:
			text: Text to scan for swear words.

		Returns:
			Tuple of (total_count, list_of_detected_words).
			If "damn" appears twice, count=2 and list contains "damn" twice.
		"""
		if not text:
			return 0, []

		text_lower = text.lower()
		detected: list[str] = []

		for swear_word in self._swear_words:
			pattern = r'\b' + re.escape(swear_word) + r'\b'
			matches = re.findall(pattern, text_lower)
			detected.extend(matches)

		if detected:
			log.info(f'Detected {len(detected)} swear(s) in text: {detected}')

		return len(detected), detected

	@property
	def word_count(self) -> int:
		"""Return number of loaded swear words."""
		return len(self._swear_words)
