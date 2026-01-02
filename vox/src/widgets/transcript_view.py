"""Transcript view widget."""

from textual.widgets import Static


class TranscriptView(Static):
	"""Displays transcribed text."""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._text = ''

	def append_text(self, text: str) -> None:
		"""Append new transcribed text."""
		if text.strip():
			if self._text:
				self._text += ' ' + text.strip()
			else:
				self._text = text.strip()
			self.update(self._text)

	def clear_text(self) -> None:
		"""Clear all transcribed text."""
		self._text = ''
		self.update('[dim]Transcription will appear here...[/dim]')
