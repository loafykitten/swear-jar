"""Audio level visualization widgets."""

from textual.reactive import reactive
from textual.widgets import Static


class AudioLevelBar(Static):
	"""Visual audio level indicator using Unicode blocks."""

	level = reactive(0.0)

	def render(self) -> str:
		"""Render the level bar."""
		bar_width = 20
		filled = int(self.level * bar_width)
		empty = bar_width - filled

		# Color based on level
		if self.level > 0.8:
			color = 'red'
		elif self.level > 0.5:
			color = 'yellow'
		else:
			color = 'green'

		bar = '\u2588' * filled + '\u2591' * empty
		return f'[{color}]{bar}[/{color}]'

	def watch_level(self, new_level: float) -> None:
		"""Trigger re-render when level changes."""
		self.refresh()


class DeviceDisplay(Static):
	"""Shows currently selected microphone device and channel."""

	device_name = reactive('System Default')
	channel = reactive(0)
	channel_count = reactive(1)

	def render(self) -> str:
		base = f'[dim]Mic:[/dim] {self.device_name}'
		# Only show channel if device has multiple channels
		if self.channel_count > 1:
			base += f' [dim](Ch {self.channel + 1})[/dim]'
		return base

	def watch_device_name(self, name: str) -> None:
		"""Trigger re-render when device name changes."""
		self.refresh()

	def watch_channel(self, channel: int) -> None:
		"""Trigger re-render when channel changes."""
		self.refresh()

	def watch_channel_count(self, count: int) -> None:
		"""Trigger re-render when channel count changes."""
		self.refresh()
