"""Transcription module using faster-whisper for speech-to-text."""

import logging

import numpy as np
from faster_whisper import WhisperModel

log = logging.getLogger(__name__)

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
			)
		return self._model

	def transcribe(
		self, audio: np.ndarray, language: str = 'en', use_vad: bool = False
	) -> str:
		"""
		Transcribe audio buffer to text.

		Args:
			audio: NumPy array of float32 audio samples at 16kHz
			language: Language code (default: 'en')
			use_vad: Whether to use Voice Activity Detection (default: False)

		Returns:
			Transcribed text string
		"""
		model = self._ensure_model_loaded()

		audio_flat = audio.flatten().astype(np.float32)

		log.debug(f'Input audio: shape={audio_flat.shape}, dtype={audio_flat.dtype}, peak={np.max(np.abs(audio_flat)):.4f}')

		try:
			log.debug(f'Calling model.transcribe(vad_filter={use_vad}, language={language})')
			segments, info = model.transcribe(
				audio_flat,
				language=language,
				vad_filter=use_vad,
				vad_parameters={'min_silence_duration_ms': 500} if use_vad else None,
			)
			log.info(f'Transcribe returned: duration={info.duration:.2f}s, language={info.language}, prob={info.language_probability:.2f}')

			# Force generator evaluation and collect segments
			text_parts = []
			segment_count = 0
			for segment in segments:
				segment_count += 1
				log.debug(f'Segment {segment_count}: "{segment.text}" (start={segment.start:.2f}, end={segment.end:.2f})')
				text_parts.append(segment.text.strip())

			result = ' '.join(text_parts)
			log.info(f'Total segments: {segment_count}, result: "{result}"')
			return result
		except Exception as e:
			log.exception(f'Transcription exception: {e}')
			return ''

	@property
	def is_loaded(self) -> bool:
		"""Check if the model is currently loaded."""
		return self._model is not None

	def unload(self) -> None:
		"""Unload the model to free memory."""
		self._model = None
