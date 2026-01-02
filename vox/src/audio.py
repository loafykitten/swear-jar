"""Audio capture module using sounddevice for microphone input."""

from queue import Queue
from typing import Any, Callable, cast

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'float32'
BLOCKSIZE = 1024


class AudioCapture:
	"""Captures audio from microphone using sounddevice."""

	def __init__(
		self,
		audio_queue: Queue,
		on_error: Callable[[str], None] | None = None,
		on_level: Callable[[float], None] | None = None,
	):
		self.audio_queue = audio_queue
		self.on_error = on_error
		self.on_level = on_level
		self.stream: sd.InputStream | None = None
		self._running = False
		self._device_id: int | None = None
		self._channel: int = 0
		self._num_channels: int = 1

	def _audio_callback(
		self,
		indata: np.ndarray,
		frames: int,
		time_info: dict,
		status: sd.CallbackFlags,
	) -> None:
		"""Called by sounddevice for each audio block."""
		if status and self.on_error:
			self.on_error(f'Audio status: {status}')

		# Extract selected channel if capturing multi-channel audio
		if self._num_channels > 1:
			audio_data = indata[:, self._channel].copy()
		else:
			audio_data = indata.copy()

		self.audio_queue.put(audio_data)

		# Calculate RMS level and emit via callback
		if self.on_level:
			rms = np.sqrt(np.mean(audio_data**2))
			# Convert to dB scale for perceptually accurate metering
			# Reference: 0 dB = max level (1.0), -60 dB = silence
			if rms > 0:
				db = 20 * np.log10(rms)
				# Map -60dB to 0dB onto 0.0 to 1.0
				level = max(0.0, min(1.0, (db + 60) / 60))
			else:
				level = 0.0
			self.on_level(level)

	def start(self, device_id: int | None = None, channel: int = 0) -> None:
		"""Start capturing audio from specified microphone and channel."""
		if self._running:
			return

		self._device_id = device_id
		self._channel = channel

		# Determine how many channels to capture
		if device_id is not None and channel > 0:
			# Need to capture all channels up to and including the selected one
			device_channels = self.get_device_channels(device_id)
			self._num_channels = min(device_channels, channel + 1)
		else:
			self._num_channels = CHANNELS

		# Debug: print device info
		if device_id is not None:
			device_info = cast(dict[str, Any], sd.query_devices(device_id))
			print(f'[AUDIO] Device: {device_info["name"]}')
			print(f'[AUDIO] Native sample rate: {device_info["default_samplerate"]}Hz')
			print(f'[AUDIO] Max input channels: {device_info["max_input_channels"]}')
			print(f'[AUDIO] Requesting: {SAMPLE_RATE}Hz, {self._num_channels} ch, channel {channel}')

		self.stream = sd.InputStream(
			samplerate=SAMPLE_RATE,
			channels=self._num_channels,
			dtype=DTYPE,
			callback=self._audio_callback,
			blocksize=BLOCKSIZE,
			device=device_id,
		)
		self.stream.start()
		self._running = True
		print(f'[AUDIO] Stream started: actual sample rate = {self.stream.samplerate}Hz')

	def stop(self) -> None:
		"""Stop capturing audio."""
		if not self._running:
			return

		if self.stream:
			self.stream.stop()
			self.stream.close()
			self.stream = None
		self._running = False

	@property
	def is_running(self) -> bool:
		"""Check if audio capture is currently active."""
		return self._running

	@staticmethod
	def list_devices() -> list[dict]:
		"""List available audio input devices."""
		devices = sd.query_devices()
		input_devices = []
		for i, dev in enumerate(devices):
			device = cast(dict[str, Any], dev)
			if device['max_input_channels'] > 0:
				input_devices.append({
					'id': i,
					'name': device['name'],
					'channels': device['max_input_channels'],
					'sample_rate': device['default_samplerate'],
				})
		return input_devices

	@staticmethod
	def validate_device(device_id: int) -> bool:
		"""Check if a device ID is valid and has input channels."""
		try:
			device = cast(dict[str, Any], sd.query_devices(device_id))
			return device['max_input_channels'] > 0
		except (sd.PortAudioError, IndexError):
			return False

	@staticmethod
	def get_device_channels(device_id: int) -> int:
		"""Get the number of input channels for a device."""
		try:
			device = cast(dict[str, Any], sd.query_devices(device_id))
			return device['max_input_channels']
		except (sd.PortAudioError, IndexError):
			return 1
