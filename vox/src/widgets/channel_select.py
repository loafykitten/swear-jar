"""Channel selection modal screen."""

from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select


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
				self.dismiss(cast(int, value))

	def action_cancel(self) -> None:
		self.dismiss(None)
