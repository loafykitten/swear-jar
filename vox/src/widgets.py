"""Custom Textual widgets for Vox."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, Static


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


class DeviceSelectScreen(ModalScreen[int | None]):
	"""Modal screen for selecting audio input device."""

	BINDINGS = [
		('escape', 'cancel', 'Cancel'),
	]

	CSS = """
	DeviceSelectScreen {
		align: center middle;
	}

	#device-dialog {
		width: 60;
		height: auto;
		max-height: 80%;
		border: thick $primary;
		background: $surface;
		padding: 1 2;
	}

	#dialog-title {
		width: 100%;
		text-align: center;
		text-style: bold;
		margin-bottom: 1;
	}

	#device-select {
		width: 100%;
		margin: 1 0;
	}

	#button-row {
		align: center middle;
		margin-top: 1;
	}

	#button-row Button {
		margin: 0 1;
	}
	"""

	def __init__(
		self,
		devices: list[dict],
		current_device_id: int | None = None,
	):
		super().__init__()
		self.devices = devices
		self.current_device_id = current_device_id

	def compose(self) -> ComposeResult:
		options: list[tuple[str, int | None]] = [('System Default', None)]
		options.extend((d['name'], d['id']) for d in self.devices)

		initial_value = self.current_device_id

		with Vertical(id='device-dialog'):
			yield Label('Select Microphone', id='dialog-title')
			yield Select(
				options,
				value=initial_value,
				id='device-select',
				allow_blank=False,
			)
			with Horizontal(id='button-row'):
				yield Button('Cancel', variant='default', id='cancel-btn')
				yield Button('Select', variant='primary', id='select-btn')

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == 'cancel-btn':
			self.dismiss(None)
		elif event.button.id == 'select-btn':
			select = self.query_one('#device-select', Select)
			value = select.value
			if value == Select.BLANK:
				self.dismiss(None)
			else:
				self.dismiss(value)

	def action_cancel(self) -> None:
		self.dismiss(None)


class ChannelSelectScreen(ModalScreen[int | None]):
	"""Modal screen for selecting audio input channel."""

	BINDINGS = [
		('escape', 'cancel', 'Cancel'),
	]

	CSS = """
	ChannelSelectScreen {
		align: center middle;
	}

	#channel-dialog {
		width: 50;
		height: auto;
		max-height: 60%;
		border: thick $primary;
		background: $surface;
		padding: 1 2;
	}

	#channel-title {
		width: 100%;
		text-align: center;
		text-style: bold;
		margin-bottom: 1;
	}

	#channel-select {
		width: 100%;
		margin: 1 0;
	}

	#channel-button-row {
		align: center middle;
		margin-top: 1;
	}

	#channel-button-row Button {
		margin: 0 1;
	}
	"""

	def __init__(
		self,
		device_name: str,
		num_channels: int,
		current_channel: int = 0,
	):
		super().__init__()
		self.device_name = device_name
		self.num_channels = num_channels
		self.current_channel = current_channel

	def compose(self) -> ComposeResult:
		# Create channel options (1-indexed for display, 0-indexed for value)
		options: list[tuple[str, int]] = [
			(f'Channel {i + 1}', i) for i in range(self.num_channels)
		]

		with Vertical(id='channel-dialog'):
			yield Label('Select Input Channel', id='channel-title')
			yield Label(f'[dim]{self.device_name}[/dim]')
			yield Select(
				options,
				value=self.current_channel,
				id='channel-select',
				allow_blank=False,
			)
			with Horizontal(id='channel-button-row'):
				yield Button('Cancel', variant='default', id='channel-cancel-btn')
				yield Button('Select', variant='primary', id='channel-select-btn')

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == 'channel-cancel-btn':
			self.dismiss(None)
		elif event.button.id == 'channel-select-btn':
			select = self.query_one('#channel-select', Select)
			value = select.value
			if value == Select.BLANK:
				self.dismiss(0)  # Default to channel 0
			else:
				self.dismiss(value)

	def action_cancel(self) -> None:
		self.dismiss(None)
