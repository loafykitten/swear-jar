"""Transcription module using faster-whisper for speech-to-text."""

import numpy as np
from faster_whisper import WhisperModel

MODEL_SIZE = 'base'
COMPUTE_TYPE = 'int8'
DEVICE = 'cpu'


class TranscriptionEngine:
	"""Wraps faster-whisper for speech-to-text transcription."""

	def __init__(
		self,
		model_size: str = MODEL_SIZE,
		device: str = DEVICE,
		compute_type: str = COMPUTE_TYPE,
	):
		self.model_size = model_size
		self.device = device
		self.compute_type = compute_type
		self._model: WhisperModel | None = None

	def _ensure_model_loaded(self) -> WhisperModel:
		"""Lazy load the model on first use."""
		if self._model is None:
			self._model = WhisperModel(
				self.model_size,
				device=self.device,
				compute_type=self.compute_type,
				cpu_threads=4,
				num_workers=0,
			)
		return self._model

	def transcribe(self, audio: np.ndarray, language: str = 'en') -> str:
		"""
		Transcribe audio buffer to text.

		Args:
			audio: NumPy array of float32 audio samples at 16kHz
			language: Language code (default: 'en')

		Returns:
			Transcribed text string
		"""
		model = self._ensure_model_loaded()

		audio_flat = audio.flatten().astype(np.float32)

		try:
			segments, _ = model.transcribe(
				audio_flat,
				language=language,
				vad_filter=True,
				vad_parameters={'min_silence_duration_ms': 500},
			)

			text_parts = []
			for segment in segments:
				text_parts.append(segment.text.strip())

			return ' '.join(text_parts)
		except IndexError:
			# VAD filtered all audio (no speech detected)
			return ''

	@property
	def is_loaded(self) -> bool:
		"""Check if the model is currently loaded."""
		return self._model is not None

	def unload(self) -> None:
		"""Unload the model to free memory."""
		self._model = None
