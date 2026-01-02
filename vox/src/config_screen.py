"""Unified configuration screen for Vox settings."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Rule, Select

from audio import AudioCapture
from config import (
	get_api_config,
	get_device_channel,
	get_model_size,
	get_saved_device,
	save_api_config,
	save_device,
	save_device_channel,
)

# Model options: (display_name, model_key)
MODEL_OPTIONS: list[tuple[str, str]] = [
	('tiny    ~200 MB  (least accurate)', 'tiny'),
	('base    ~500 MB  (moderate accuracy)', 'base'),
	('small   ~900 MB  (good accuracy)', 'small'),
	('medium  ~2 GB    (high accuracy)', 'medium'),
	('large   ~4 GB    (most accurate)', 'large'),
]


class ConfigSaved(Message):
	"""Message sent when configuration is saved."""

	def __init__(
		self,
		device_id: int | None,
		device_name: str,
		channel: int,
		channel_count: int,
		model: str,
		base_url: str,
		api_key: str,
	):
		super().__init__()
		self.device_id = device_id
		self.device_name = device_name
		self.channel = channel
		self.channel_count = channel_count
		self.model = model
		self.base_url = base_url
		self.api_key = api_key


class ConfigScreen(Screen):
	"""Unified configuration screen with all settings."""

	BINDINGS = [
		Binding(key='q', action='quit', description='Quit'),
		Binding(key='c', action='app.pop_screen', description='Return'),
		Binding(key='escape', action='app.pop_screen', description='Return'),
	]

	CSS = """
	ConfigScreen {
		align: center top;
	}

	#config-container {
		width: 100%;
		max-width: 80;
		height: 100%;
		padding: 1 2;
	}

	.section-title {
		text-style: bold;
		color: $accent;
		margin-top: 1;
		margin-bottom: 1;
	}

	.field-label {
		margin-top: 1;
		margin-bottom: 0;
		color: $text-muted;
	}

	.config-select, .config-input {
		width: 100%;
		margin-bottom: 1;
	}

	#button-row {
		align: center middle;
		margin-top: 2;
	}

	#button-row Button {
		margin: 0 1;
	}

	Rule {
		margin: 1 0;
	}
	"""

	def __init__(self):
		super().__init__()
		# Flag to suppress change handlers during initial hydration
		self._hydrating = False
		# Set defaults - actual values loaded in on_mount
		self.current_device_id: int | None = None
		self.current_device_name = 'System Default'
		self.devices: list[dict] = []
		self.current_channel = 0
		self.current_channel_count = 1
		self.current_model = 'base'
		self.current_base_url = ''
		self.current_api_key = ''

	def _get_channel_options(self) -> list[tuple[str, int]]:
		"""Generate channel options based on current channel count."""
		return [(f'Channel {i + 1}', i) for i in range(self.current_channel_count)]

	def compose(self) -> ComposeResult:
		yield Header()

		with VerticalScroll(id='config-container'):
			# === MICROPHONE SECTION ===
			yield Label('Microphone Settings', classes='section-title')

			yield Label('Device:', classes='field-label')
			device_options: list[tuple[str, int | None]] = [('System Default', None)]
			device_options.extend((d['name'], d['id']) for d in self.devices)
			yield Select(
				device_options,
				value=self.current_device_id,
				id='device-select',
				classes='config-select',
				allow_blank=False,
			)

			yield Label('Channel:', classes='field-label')
			yield Select(
				self._get_channel_options(),
				value=self.current_channel,
				id='channel-select',
				classes='config-select',
				allow_blank=False,
			)

			yield Rule()

			# === MODEL SECTION ===
			yield Label('Whisper Model', classes='section-title')

			yield Label('Model Size:', classes='field-label')
			yield Select(
				MODEL_OPTIONS,
				value=self.current_model,
				id='model-select',
				classes='config-select',
				allow_blank=False,
			)

			yield Rule()

			# === API SECTION ===
			yield Label('API Configuration', classes='section-title')

			yield Label('Base URL:', classes='field-label')
			yield Input(
				value=self.current_base_url,
				placeholder='http://localhost:3000',
				id='base-url-input',
				classes='config-input',
			)

			yield Label('API Key:', classes='field-label')
			yield Input(
				value=self.current_api_key,
				placeholder='Enter your API key',
				id='api-key-input',
				classes='config-input',
				password=True,
			)

			yield Rule()

			# === BUTTONS ===
			with Horizontal(id='button-row'):
				yield Button('Cancel', variant='default', id='cancel-btn')
				yield Button('Save', variant='primary', id='save-btn')

		yield Footer()

	def on_mount(self) -> None:
		self.title = 'Swear Jar'
		self.sub_title = '(Configuration)'

	def on_show(self) -> None:
		"""Refresh config values each time screen is shown."""
		self._load_config()
		self.call_after_refresh(self._apply_config_to_widgets)

	def _load_config(self) -> None:
		"""Load current config values into instance variables."""
		# Load device config
		self.current_device_id, self.current_device_name = get_saved_device()
		self.current_device_name = self.current_device_name or 'System Default'

		# Get devices list
		self.devices = AudioCapture.list_devices()

		# Load channel config
		if self.current_device_id is not None:
			self.current_channel = get_device_channel(self.current_device_id)
			self.current_channel_count = AudioCapture.get_device_channels(
				self.current_device_id
			)
			if self.current_channel >= self.current_channel_count:
				self.current_channel = 0
		else:
			self.current_channel = 0
			self.current_channel_count = 1

		# Load model config
		self.current_model = get_model_size()

		# Load API config
		base_url, api_key = get_api_config()
		self.current_base_url = base_url or ''
		self.current_api_key = api_key or ''

	def _apply_config_to_widgets(self) -> None:
		"""Apply loaded config values to widgets.

		Widget Hydration with Textual's Select Widget
		---------------------------------------------
		Textual's Select.set_options() resets the widget's value to None asynchronously
		after the method returns. This means we cannot set options and value in the same
		synchronous call - the value would be immediately overwritten.

		The solution uses a cascade of 50ms timers to defer value assignment until
		after Textual's internal state updates have completed:

		1. set_options() called for all Select widgets
		2. Wait 50ms -> _set_select_values(): Set device and model values
		3. Wait 50ms -> _set_channel_value(): Set channel value and show widget

		The second delay is needed because setting the device value triggers
		on_select_changed -> _on_device_changed, which calls set_options() on the
		channel select, creating another async reset.

		The _hydrating flag prevents change handlers from firing during this process,
		avoiding unwanted side effects and infinite loops.
		"""
		# Suppress change handlers during hydration
		self._hydrating = True
		# Update device select options
		device_select = self.query_one('#device-select', Select)
		device_options: list[tuple[str, int | None]] = [('System Default', None)]
		device_options.extend((d['name'], d['id']) for d in self.devices)
		device_select.set_options(device_options)

		# Update channel select options (hide during hydration to prevent flash)
		channel_select = self.query_one('#channel-select', Select)
		channel_select.display = False
		channel_select.set_options(self._get_channel_options())

		# Update API inputs (these work immediately)
		self.query_one('#base-url-input', Input).value = self.current_base_url
		self.query_one('#api-key-input', Input).value = self.current_api_key

		# Defer Select value assignment - set_options() resets values asynchronously
		self.set_timer(0.05, self._set_select_values)

	def _set_select_values(self) -> None:
		"""Set select values after set_options() has fully processed (step 2 of hydration)."""
		self.query_one('#device-select', Select).value = self.current_device_id
		self.query_one('#model-select', Select).value = self.current_model
		# Defer channel assignment - device change triggers more set_options() calls
		self.set_timer(0.05, self._set_channel_value)

	def _set_channel_value(self) -> None:
		"""Set channel value after all cascading events have settled (step 3 of hydration)."""
		channel_select = self.query_one('#channel-select', Select)
		channel_select.value = self.current_channel
		channel_select.display = True  # Show after correct value is set
		# Re-enable change handlers after hydration complete
		self._hydrating = False

	def on_select_changed(self, event: Select.Changed) -> None:
		"""Handle select widget changes."""
		if self._hydrating:
			return  # Skip during initial hydration
		if event.select.id == 'device-select':
			self._on_device_changed(event.value)

	def _on_device_changed(self, device_id: int | None) -> None:
		"""Update channel options when device changes."""
		if device_id is None:
			self.current_channel_count = 1
		else:
			self.current_channel_count = AudioCapture.get_device_channels(device_id)

		# Update channel select options
		channel_select = self.query_one('#channel-select', Select)
		channel_select.set_options(self._get_channel_options())

		# Reset to channel 0 if current channel is out of range
		current_channel = channel_select.value
		if isinstance(current_channel, int) and current_channel >= self.current_channel_count:
			channel_select.value = 0

	def on_button_pressed(self, event: Button.Pressed) -> None:
		"""Handle button presses."""
		if event.button.id == 'cancel-btn':
			self.app.pop_screen()
		elif event.button.id == 'save-btn':
			self._save_config()

	def _save_config(self) -> None:
		"""Save all configuration and notify app."""
		# Get values from widgets
		device_select = self.query_one('#device-select', Select)
		channel_select = self.query_one('#channel-select', Select)
		model_select = self.query_one('#model-select', Select)
		base_url_input = self.query_one('#base-url-input', Input)
		api_key_input = self.query_one('#api-key-input', Input)

		# Extract values
		device_id = device_select.value if device_select.value != Select.BLANK else None
		channel = channel_select.value if channel_select.value != Select.BLANK else 0
		model = str(model_select.value) if model_select.value != Select.BLANK else 'base'
		base_url = base_url_input.value.strip()
		api_key = api_key_input.value.strip()

		# Determine device name
		device_name = 'System Default'
		if device_id is not None:
			for d in self.devices:
				if d['id'] == device_id:
					device_name = d['name']
					break

		# Save device config
		save_device(device_id, device_name)
		if device_id is not None and isinstance(channel, int):
			save_device_channel(device_id, channel)

		# Save API config (if both provided)
		if base_url and api_key:
			save_api_config(base_url, api_key)

		# Post message to app with config changes
		self.post_message(
			ConfigSaved(
				device_id=device_id,
				device_name=device_name,
				channel=channel if isinstance(channel, int) else 0,
				channel_count=self.current_channel_count,
				model=model,
				base_url=base_url,
				api_key=api_key,
			)
		)

		self.app.pop_screen()
