"""
Captures user microphone audio in realtime and uses speech-to-text to detect user-defined swear words and interact with the swear-jar service upon detection.
"""

# Disable tqdm and huggingface progress bars BEFORE any imports to avoid
# multiprocessing lock issues when loading models inside Textual worker threads
import os

os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['TQDM_DISABLE'] = '1'

from queue import Empty, Queue

import numpy as np
import psutil
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header
from textual.worker import get_current_worker

from api_client import SwearAPIClient
from audio import SAMPLE_RATE, AudioCapture
from cli import parse_args
from config import (
	get_api_config,
	get_device_channel,
	get_model_size,
	get_saved_device,
	save_model_size,
)
from config_screen import ConfigSaved, ConfigScreen
from halp import Halp
from logging_setup import get_logger
from processing import SAMPLES_PER_BUFFER, process_audio_buffer
from swear_detection import SwearDetector
from transcription import TranscriptionEngine
from widgets import (
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
		Binding(key='c', action='open_config', description='Config'),
	]

	is_recording = reactive(False)
	is_loading = reactive(False)
	model_ready = reactive(False)  # Starts False, set True after async load
	api_configured = reactive(False)
	selected_device_id: reactive[int | None] = reactive(None)
	selected_device_name: reactive[str] = reactive('System Default')
	audio_level: reactive[float] = reactive(0.0)
	selected_channel: reactive[int] = reactive(0)
	selected_channel_count: reactive[int] = reactive(1)
	selected_model: reactive[str] = reactive('base')

	def __init__(
		self,
		swear_detector: SwearDetector,
		api_client: SwearAPIClient | None,
		initial_base_url: str | None = None,
		initial_api_key: str | None = None,
		initial_model_size: str = 'base',
	):
		super().__init__()
		self._process = psutil.Process()
		self.audio_queue: Queue = Queue()
		self.swear_detector = swear_detector
		self.api_client = api_client
		self._base_url = initial_base_url
		self._api_key = initial_api_key
		self._api_configured = api_client is not None
		self._initial_model_size = initial_model_size

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
		self.transcription_engine: TranscriptionEngine | None = None

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
		self._update_stats()
		self.set_interval(1.0, self._update_stats)

		# Apply saved device and channel selection
		self.selected_device_id = self._initial_device_id
		self.selected_device_name = self._initial_device_name
		self.selected_channel = self._initial_channel
		self.selected_channel_count = self._initial_channel_count

		# Set API configured state
		self.api_configured = self._api_configured

		# Set initial model and start async loading
		self.selected_model = self._initial_model_size
		self.notify(f'Loading {self._initial_model_size} model...')
		self._load_initial_model()

		# Show loaded word count
		self.notify(f'Loaded {self.swear_detector.word_count} swear words.')

	def _update_level(self, level: float) -> None:
		"""Update audio level (called from audio thread)."""
		self.audio_level = level

	def _update_stats(self) -> None:
		"""Update CPU/memory stats for this process in header subtitle."""
		cpu = self._process.cpu_percent()
		mem_bytes = self._process.memory_info().rss
		if mem_bytes >= 1024**3:
			mem_str = f'{mem_bytes / (1024**3):.1f} GB'
		else:
			mem_str = f'{mem_bytes / (1024**2):.1f} MB'
		self.sub_title = f'CPU: {cpu:.1f}% | MEM: {mem_str}'

	def _append_transcript(self, text: str) -> None:
		"""Append text to transcript (called from main thread via call_from_thread)."""
		self.query_one('#transcript', TranscriptView).append_text(text)

	def _process_swears(self, text: str) -> None:
		"""Detect and report swears in transcribed text."""
		count, detected = self.swear_detector.detect(text)
		if count > 0 and self.api_client:
			self.api_client.report_swears(count)
			log.info(f'Reported {count} swear(s): {detected}')

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
		if not self.api_configured:
			self.notify(
				'API not configured. Set base URL and API key.', severity='warning'
			)
			self.action_open_config()
			return
		if self.is_recording:
			self.stop_recording()
		else:
			self.start_recording()

	def action_open_config(self) -> None:
		"""Open configuration screen with fresh instance."""
		self.push_screen(ConfigScreen())

	def on_config_saved(self, event: ConfigSaved) -> None:
		"""Handle configuration save from ConfigScreen."""
		# Update device state
		self.selected_device_id = event.device_id
		self.selected_device_name = event.device_name
		self.selected_channel = event.channel
		self.selected_channel_count = event.channel_count

		# Reload model if changed
		if event.model != self.selected_model:
			was_recording = self.is_recording
			if was_recording:
				self.stop_recording()
			self.model_ready = False
			self.notify(f'Loading {event.model} model...')
			self._reload_model(event.model, was_recording)

		# Update API client if changed
		if event.base_url and event.api_key:
			self._base_url = event.base_url
			self._api_key = event.api_key
			self.api_client = SwearAPIClient(event.base_url, event.api_key)
			self.api_configured = True

		# Restart audio capture if recording and device changed
		if self.is_recording:
			self.audio_capture.stop()
			self.audio_capture.start(
				device_id=event.device_id, channel=event.channel
			)

		self.notify('Configuration saved')

	@work(thread=True, exclusive=True, group='model_reload')
	def _load_initial_model(self) -> None:
		"""Load the initial transcription model in a background thread."""
		# Monkey-patch tqdm to avoid multiprocessing lock issues in worker threads
		import contextlib

		import tqdm.std

		tqdm.std.TqdmDefaultWriteLock = contextlib.nullcontext  # type: ignore[attr-defined]

		try:
			self.transcription_engine = TranscriptionEngine(
				model_size=self._initial_model_size
			)
			self.transcription_engine._ensure_model_loaded()
			self.call_from_thread(self._on_initial_model_loaded)
		except Exception as e:
			log.exception(f'Failed to load model: {e}')
			self.call_from_thread(
				self.notify, f'Failed to load model: {e}', severity='error'
			)
			self.call_from_thread(self._on_model_load_failed)

	def _on_initial_model_loaded(self) -> None:
		"""Called when initial model loading completes."""
		self.model_ready = True
		self.notify(f'Model {self._initial_model_size} ready')

	def _on_model_load_failed(self) -> None:
		"""Called when model loading fails - prompt user to configure."""
		self.push_screen(ConfigScreen())

	@work(thread=True, exclusive=True, group='model_reload')
	def _reload_model(self, new_model: str, resume_recording: bool) -> None:
		"""Reload the transcription model in a background thread."""
		# Monkey-patch tqdm to avoid multiprocessing lock issues in worker threads
		import contextlib

		import tqdm.std

		tqdm.std.TqdmDefaultWriteLock = contextlib.nullcontext  # type: ignore[attr-defined]

		try:
			# Unload current model if exists
			if self.transcription_engine is not None:
				self.transcription_engine.unload()

			# Create and load new model
			self.transcription_engine = TranscriptionEngine(model_size=new_model)
			self.transcription_engine._ensure_model_loaded()

			# Update state on main thread
			self.call_from_thread(self._on_model_loaded, new_model, resume_recording)
		except Exception as e:
			log.exception(f'Failed to load model: {e}')
			self.call_from_thread(
				self.notify, f'Failed to load model: {e}', severity='error'
			)
			self.call_from_thread(setattr, self, 'model_ready', True)

	def _on_model_loaded(self, new_model: str, resume_recording: bool) -> None:
		"""Called when model loading completes."""
		self.selected_model = new_model
		self.model_ready = True
		save_model_size(new_model)
		self.notify(f'Model changed to {new_model}')

		if resume_recording:
			self.start_recording()

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

	def action_quit(self) -> None:
		"""Handle quit action - stop audio before exiting."""
		if self.is_recording:
			self.stop_recording()
		self.exit()

	@work(thread=True, exclusive=True, group='transcription')
	def _run_transcription_worker(self) -> None:
		"""Background worker that processes audio and transcribes it."""
		# Engine is guaranteed to exist because recording requires model_ready=True
		assert self.transcription_engine is not None, 'Engine must be loaded'
		engine = self.transcription_engine

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
					text = process_audio_buffer(audio_buffer, engine)
					if text.strip():
						self.call_from_thread(self._append_transcript, text)
						self.call_from_thread(self._process_swears, text)
					audio_buffer = []
					total_samples = 0

			except Empty:
				continue

		log.info(f'Transcription worker ending. Chunks received: {chunks_received}')

		# Process any remaining audio in buffer
		if audio_buffer and total_samples > SAMPLE_RATE * 0.5:
			log.info(f'Final flush: {total_samples} samples')
			text = process_audio_buffer(audio_buffer, engine)
			if text.strip():
				self.call_from_thread(self._append_transcript, text)
				self.call_from_thread(self._process_swears, text)


if __name__ == '__main__':
	args = parse_args()

	swear_detector = SwearDetector(args.word_list)

	# Load from config, CLI overrides
	saved_base_url, saved_api_key = get_api_config()
	base_url = args.base_url or saved_base_url
	api_key = args.api_key or saved_api_key

	# Create api_client only if both are set
	api_client = None
	if base_url and api_key:
		api_client = SwearAPIClient(base_url, api_key)
		print('API client configured.')
	else:
		print('API not configured. Press [c] to configure.')

	# Load model size from config, CLI overrides
	saved_model_size = get_model_size()
	model_size = args.model_size or saved_model_size

	print(f'Starting app (model {model_size} will load in background)...')

	VoxAnalysis(
		swear_detector,
		api_client,
		initial_base_url=base_url,
		initial_api_key=api_key,
		initial_model_size=model_size,
	).run()
