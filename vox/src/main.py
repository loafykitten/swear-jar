"""
Captures user microphone audio in realtime and uses speech-to-text to detect user-defined swear words and interact with the swear-jar service upon detection.
"""

# Import logging_setup first to configure logging before other modules
from logging_setup import get_logger

from queue import Empty, Queue

import numpy as np
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header
from textual.worker import get_current_worker

from audio import SAMPLE_RATE, AudioCapture
from config import (
	get_device_channel,
	get_saved_device,
	save_device,
	save_device_channel,
)
from halp import Halp
from processing import SAMPLES_PER_BUFFER, process_audio_buffer
from transcription import TranscriptionEngine
from widgets import (
	ChannelSelectScreen,
	DeviceSelectScreen,
	StatusPanel,
	TranscriptView,
)

log = get_logger(__name__)


class VoxAnalysis(App):
	CSS_PATH = ['vox.tcss']
	SCREENS = {'halp': Halp}
	BINDINGS = [
		Binding(key='q', action='quit', description='Quit'),
		Binding(
			key='question_mark',
			action='push_screen("halp")',
			description='Help',
			key_display='?',
		),
		Binding(key='space', action='toggle_recording', description='Record'),
		Binding(key='r', action='clear_transcript', description='Clear'),
		Binding(key='m', action='select_microphone', description='Mic'),
	]

	is_recording = reactive(False)
	is_loading = reactive(False)
	model_ready = reactive(True)
	selected_device_id: reactive[int | None] = reactive(None)
	selected_device_name: reactive[str] = reactive('System Default')
	audio_level: reactive[float] = reactive(0.0)
	selected_channel: reactive[int] = reactive(0)
	selected_channel_count: reactive[int] = reactive(1)

	def __init__(self, transcription_engine: TranscriptionEngine):
		super().__init__()
		self.audio_queue: Queue = Queue()

		# Load saved device preference
		saved_id, saved_name = get_saved_device()
		self._initial_device_id = saved_id
		self._initial_device_name = saved_name or 'System Default'

		# Validate saved device still exists
		if saved_id is not None and not AudioCapture.validate_device(saved_id):
			self._initial_device_id = None
			self._initial_device_name = 'System Default'

		# Load saved channel preference for the device
		if self._initial_device_id is not None:
			self._initial_channel = get_device_channel(self._initial_device_id)
			self._initial_channel_count = AudioCapture.get_device_channels(
				self._initial_device_id
			)
			# Validate channel is within range
			if self._initial_channel >= self._initial_channel_count:
				self._initial_channel = 0
		else:
			self._initial_channel = 0
			self._initial_channel_count = 1

		self.audio_capture = AudioCapture(
			self.audio_queue,
			on_error=lambda msg: self.call_from_thread(self.notify, msg),
			on_level=lambda lvl: self.call_from_thread(self._update_level, lvl),
		)
		self.transcription_engine = transcription_engine

	def compose(self) -> ComposeResult:
		yield Header()
		yield Container(
			Vertical(
				StatusPanel(id='status'),
				TranscriptView(
					'[dim]Transcription will appear here...[/dim]', id='transcript'
				),
				id='main-content',
			),
		)
		yield Footer()

	def on_mount(self) -> None:
		self.title = 'Swear Jar'
		self.sub_title = '(Vox Analysis)'

		# Apply saved device and channel selection
		self.selected_device_id = self._initial_device_id
		self.selected_device_name = self._initial_device_name
		self.selected_channel = self._initial_channel
		self.selected_channel_count = self._initial_channel_count

	def _update_level(self, level: float) -> None:
		"""Update audio level (called from audio thread)."""
		self.audio_level = level

	def _append_transcript(self, text: str) -> None:
		"""Append text to transcript (called from main thread via call_from_thread)."""
		self.query_one('#transcript', TranscriptView).append_text(text)

	def watch_is_recording(self, recording: bool) -> None:
		"""Update UI when recording state changes."""
		self.query_one('#status', StatusPanel).recording = recording

	def watch_is_loading(self, loading: bool) -> None:
		"""Update UI when loading state changes."""
		self.query_one('#status', StatusPanel).loading = loading

	def watch_model_ready(self, ready: bool) -> None:
		"""Update UI when model ready state changes."""
		self.query_one('#status', StatusPanel).model_ready = ready

	def watch_audio_level(self, level: float) -> None:
		"""Propagate level to status panel."""
		self.query_one('#status', StatusPanel).audio_level = level

	def watch_selected_device_name(self, name: str) -> None:
		"""Update device display in status panel."""
		self.query_one('#status', StatusPanel).device_name = name

	def watch_selected_channel(self, channel: int) -> None:
		"""Update channel display in status panel."""
		self.query_one('#status', StatusPanel).channel = channel

	def watch_selected_channel_count(self, count: int) -> None:
		"""Update channel count display in status panel."""
		self.query_one('#status', StatusPanel).channel_count = count

	def action_toggle_recording(self) -> None:
		"""Toggle audio recording on/off."""
		if not self.model_ready:
			self.notify('Model is still loading...', severity='warning')
			return
		if self.is_recording:
			self.stop_recording()
		else:
			self.start_recording()

	def action_clear_transcript(self) -> None:
		"""Clear the transcript display."""
		self.query_one('#transcript', TranscriptView).clear_text()

	def action_select_microphone(self) -> None:
		"""Open device selection modal."""
		devices = AudioCapture.list_devices()

		def on_channel_selected(
			channel: int | None,
			device_id: int | None,
			device_name: str,
			channel_count: int,
		) -> None:
			"""Handle channel selection result."""
			if channel is None:
				# User cancelled channel selection - keep device, use default channel
				channel = 0

			# Update state
			self.selected_device_id = device_id
			self.selected_device_name = device_name
			self.selected_channel = channel
			self.selected_channel_count = channel_count

			# Persist selection
			save_device(device_id, device_name)
			if device_id is not None:
				save_device_channel(device_id, channel)

			# Restart capture if recording
			if self.is_recording:
				self.audio_capture.stop()
				self.audio_capture.start(device_id=device_id, channel=channel)

			channel_info = f' (Ch {channel + 1})' if channel_count > 1 else ''
			self.notify(f'Selected: {device_name}{channel_info}')

		def on_device_selected(result: int | None) -> None:
			"""Handle device selection result."""
			# None means user cancelled - do nothing
			if result is None and self.selected_device_id is not None:
				return

			device_id = result
			device_name = 'System Default'
			channel_count = 1

			if device_id is not None:
				# Find device info
				for d in devices:
					if d['id'] == device_id:
						device_name = d['name']
						channel_count = d['channels']
						break

			# If multi-channel device, show channel selection
			if channel_count > 1:
				saved_channel = get_device_channel(device_id) if device_id else 0
				# Validate saved channel is within range
				if saved_channel >= channel_count:
					saved_channel = 0
				self.push_screen(
					ChannelSelectScreen(device_name, channel_count, saved_channel),
					lambda ch: on_channel_selected(
						ch, device_id, device_name, channel_count
					),
				)
			else:
				# Single channel - proceed directly
				on_channel_selected(0, device_id, device_name, channel_count)

		self.push_screen(
			DeviceSelectScreen(devices, self.selected_device_id),
			on_device_selected,
		)

	def start_recording(self) -> None:
		"""Start audio capture and transcription."""
		self.is_recording = True
		self.audio_capture.start(
			device_id=self.selected_device_id,
			channel=self.selected_channel,
		)
		self._run_transcription_worker()

	def stop_recording(self) -> None:
		"""Stop audio capture."""
		self.is_recording = False
		self.audio_capture.stop()

	@work(thread=True, exclusive=True, group='transcription')
	def _run_transcription_worker(self) -> None:
		"""Background worker that processes audio and transcribes it."""
		worker = get_current_worker()
		audio_buffer: list[np.ndarray] = []
		total_samples = 0
		chunks_received = 0

		log.info('Transcription worker started')

		while not worker.is_cancelled and self.is_recording:
			try:
				chunk = self.audio_queue.get(timeout=0.1)
				audio_buffer.append(chunk)
				total_samples += len(chunk)
				chunks_received += 1

				if total_samples >= SAMPLES_PER_BUFFER:
					text = process_audio_buffer(audio_buffer, self.transcription_engine)
					if text.strip():
						self.call_from_thread(self._append_transcript, text)
					audio_buffer = []
					total_samples = 0

			except Empty:
				continue

		log.info(f'Transcription worker ending. Chunks received: {chunks_received}')

		# Process any remaining audio in buffer
		if audio_buffer and total_samples > SAMPLE_RATE * 0.5:
			log.info(f'Final flush: {total_samples} samples')
			text = process_audio_buffer(audio_buffer, self.transcription_engine)
			if text.strip():
				self.call_from_thread(self._append_transcript, text)


if __name__ == '__main__':
	print('Loading Whisper model...')
	engine = TranscriptionEngine()
	engine._ensure_model_loaded()
	print('Model loaded. Starting app...')
	VoxAnalysis(engine).run()
