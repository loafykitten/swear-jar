"""Status panel widget."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from widgets.audio_level_bar import AudioLevelBar, DeviceDisplay


class StatusPanel(Static):
	"""Combined status panel with recording state, device info, and level meter."""

	recording = reactive(False)
	loading = reactive(True)
	model_ready = reactive(False)
	device_name = reactive('System Default')
	audio_level = reactive(0.0)
	channel = reactive(0)
	channel_count = reactive(1)

	def compose(self) -> ComposeResult:
		yield Static(id='status-text')
		yield DeviceDisplay(id='device-display')
		yield AudioLevelBar(id='level-bar')

	def on_mount(self) -> None:
		self._update_status_text()

	def watch_recording(self, recording: bool) -> None:
		self._update_status_text()
		level_bar = self.query_one('#level-bar', AudioLevelBar)
		level_bar.display = recording

	def watch_loading(self, loading: bool) -> None:
		self._update_status_text()

	def watch_model_ready(self, ready: bool) -> None:
		self._update_status_text()

	def watch_device_name(self, name: str) -> None:
		self.query_one('#device-display', DeviceDisplay).device_name = name

	def watch_audio_level(self, level: float) -> None:
		self.query_one('#level-bar', AudioLevelBar).level = level

	def watch_channel(self, channel: int) -> None:
		self.query_one('#device-display', DeviceDisplay).channel = channel

	def watch_channel_count(self, count: int) -> None:
		self.query_one('#device-display', DeviceDisplay).channel_count = count

	def _update_status_text(self) -> None:
		status = self.query_one('#status-text', Static)
		if self.loading:
			status.update('[yellow]Loading model...[/yellow]')
		elif self.recording:
			status.update('[red bold]Recording[/red bold]')
		elif self.model_ready:
			status.update('[green]Ready[/green] [dim]- Press Space to record[/dim]')
		else:
			status.update('[dim]Press Space to start recording[/dim]')
