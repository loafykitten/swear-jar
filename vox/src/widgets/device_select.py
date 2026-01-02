"""Device selection modal screen."""

from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select


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
				self.dismiss(cast(int | None, value))

	def action_cancel(self) -> None:
		self.dismiss(None)
