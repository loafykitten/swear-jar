"""Audio processing utilities for transcription."""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
	from transcription import TranscriptionEngine

from audio import SAMPLE_RATE
from logging_setup import get_logger

log = get_logger(__name__)

# Buffer configuration
BUFFER_DURATION_SECONDS = 3.0
SAMPLES_PER_BUFFER = int(SAMPLE_RATE * BUFFER_DURATION_SECONDS)


def normalize_audio(audio_data: np.ndarray, target_peak: float = 0.9) -> np.ndarray:
	"""Normalize audio to target peak level.

	Args:
		audio_data: Input audio samples.
		target_peak: Target peak amplitude (0.0 to 1.0).

	Returns:
		Normalized audio data.
	"""
	peak = float(np.max(np.abs(audio_data)))
	if peak > 0.001:
		normalized = audio_data * (target_peak / peak)
		log.info(f'Normalized audio: peak {peak:.4f} -> {target_peak}')
		return normalized
	return audio_data


def process_audio_buffer(
	audio_buffer: list[np.ndarray],
	transcription_engine: 'TranscriptionEngine',
) -> str:
	"""Process accumulated audio buffer and return transcription.

	Args:
		audio_buffer: List of audio chunks to concatenate and process.
		transcription_engine: Engine to perform transcription.

	Returns:
		Transcribed text, or empty string on error.
	"""
	if not audio_buffer:
		return ''

	audio_data = np.concatenate(audio_buffer)

	# Audio diagnostics
	audio_min = float(np.min(audio_data))
	audio_max = float(np.max(audio_data))
	audio_rms = float(np.sqrt(np.mean(audio_data**2)))
	log.info(
		f'Audio buffer: {len(audio_data)} samples, '
		f'min={audio_min:.4f}, max={audio_max:.4f}, rms={audio_rms:.4f}'
	)

	# Normalize before transcription
	audio_data = normalize_audio(audio_data)

	try:
		log.info('Calling transcription engine...')
		text = transcription_engine.transcribe(audio_data)
		log.info(f'Transcription result: "{text}" (len={len(text)})')
		return text
	except Exception as e:
		log.exception(f'Transcription error: {e}')
		return ''
