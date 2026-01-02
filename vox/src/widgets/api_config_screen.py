"""API configuration modal screen."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class ApiConfigScreen(ModalScreen[tuple[str, str] | None]):
	"""Modal screen for configuring API settings."""

	BINDINGS = [
		('escape', 'cancel', 'Cancel'),
	]

	CSS = """
	ApiConfigScreen {
		align: center middle;
	}

	#api-dialog {
		width: 70;
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

	.input-label {
		margin-top: 1;
		margin-bottom: 0;
	}

	.config-input {
		width: 100%;
		margin-bottom: 1;
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
		current_base_url: str | None = None,
		current_api_key: str | None = None,
	):
		super().__init__()
		self.current_base_url = current_base_url or ''
		self.current_api_key = current_api_key or ''

	def compose(self) -> ComposeResult:
		with Vertical(id='api-dialog'):
			yield Label('API Configuration', id='dialog-title')

			yield Label('Base URL:', classes='input-label')
			yield Input(
				value=self.current_base_url,
				placeholder='http://localhost:3000',
				id='base-url-input',
				classes='config-input',
			)

			yield Label('API Key:', classes='input-label')
			yield Input(
				value=self.current_api_key,
				placeholder='Enter your API key',
				id='api-key-input',
				classes='config-input',
				password=True,
			)

			with Horizontal(id='button-row'):
				yield Button('Cancel', variant='default', id='cancel-btn')
				yield Button('Save', variant='primary', id='save-btn')

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == 'cancel-btn':
			self.dismiss(None)
		elif event.button.id == 'save-btn':
			base_url = self.query_one('#base-url-input', Input).value.strip()
			api_key = self.query_one('#api-key-input', Input).value.strip()

			if not base_url:
				self.notify('Base URL is required', severity='error')
				return
			if not api_key:
				self.notify('API Key is required', severity='error')
				return

			self.dismiss((base_url, api_key))

	def action_cancel(self) -> None:
		self.dismiss(None)
