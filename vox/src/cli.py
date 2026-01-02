"""CLI argument parsing for Vox."""

import argparse
from dataclasses import dataclass
from pathlib import Path


MODEL_SIZES = ['tiny', 'base', 'small', 'medium', 'large']


@dataclass
class VoxArgs:
	"""Parsed CLI arguments for Vox."""

	base_url: str | None
	api_key: str | None
	word_list: Path
	model_size: str | None


def get_default_word_list() -> Path:
	"""Get default word list path relative to vox directory."""
	src_dir = Path(__file__).parent
	vox_dir = src_dir.parent
	return vox_dir / 'swear_words.txt'


def parse_args() -> VoxArgs:
	"""Parse command line arguments.

	Returns:
		VoxArgs dataclass with parsed values.

	Raises:
		SystemExit: If required arguments are missing or invalid.
	"""
	parser = argparse.ArgumentParser(
		prog='vox',
		description='Speech-to-text TUI with swear word detection',
	)

	parser.add_argument(
		'-u',
		'--base-url',
		type=str,
		default=None,
		help='Base URL for swear-jar service (overrides saved config)',
	)

	parser.add_argument(
		'-k',
		'--api-key',
		type=str,
		default=None,
		help='API key for authentication (overrides saved config)',
	)

	parser.add_argument(
		'-w',
		'--word-list',
		type=Path,
		default=None,
		help='Path to swear words file (default: vox/swear_words.txt)',
	)

	parser.add_argument(
		'-m',
		'--model-size',
		type=str,
		choices=MODEL_SIZES,
		default=None,
		help='Whisper model size (overrides saved config)',
	)

	args = parser.parse_args()

	word_list = args.word_list if args.word_list else get_default_word_list()

	if not word_list.exists():
		parser.error(f'Word list file not found: {word_list}')

	return VoxArgs(
		base_url=args.base_url,
		api_key=args.api_key,
		word_list=word_list,
		model_size=args.model_size,
	)
