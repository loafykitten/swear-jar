"""Transcript view widget."""

from collections import deque

from textual.widgets import Static


class TranscriptView(Static):
	"""Displays transcribed text with automatic line limiting."""

	DEFAULT_MAX_LINES = 10

	def __init__(self, *args, max_lines: int = DEFAULT_MAX_LINES, **kwargs):
		super().__init__(*args, **kwargs)
		self._lines: deque[str] = deque(maxlen=max_lines)

	def append_text(self, text: str) -> None:
		"""Append new transcribed text as a new line."""
		stripped = text.strip()
		if stripped:
			self._lines.append(stripped)
			self.update('\n'.join(self._lines))

	def clear_text(self) -> None:
		"""Clear all transcribed text."""
		self._lines.clear()
		self.update('[dim]Transcription will appear here...[/dim]')
