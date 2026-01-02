"""Configuration persistence for Vox settings."""

import json
from pathlib import Path
from typing import TypedDict

CONFIG_DIR = Path.home() / '.config' / 'vox'
CONFIG_FILE = CONFIG_DIR / 'settings.json'


class VoxConfig(TypedDict, total=False):
	"""Configuration schema."""

	device_id: int | None
	device_name: str | None
	device_channels: dict[str, int]  # Key: str(device_id), Value: channel index
	base_url: str | None
	api_key: str | None


def load_config() -> VoxConfig:
	"""Load configuration from disk."""
	if not CONFIG_FILE.exists():
		return {}
	try:
		with open(CONFIG_FILE, 'r') as f:
			return json.load(f)
	except (json.JSONDecodeError, IOError):
		return {}


def save_config(config: VoxConfig) -> None:
	"""Save configuration to disk."""
	CONFIG_DIR.mkdir(parents=True, exist_ok=True)
	with open(CONFIG_FILE, 'w') as f:
		json.dump(config, f, indent=2)


def get_saved_device() -> tuple[int | None, str | None]:
	"""Get saved device ID and name."""
	config = load_config()
	return config.get('device_id'), config.get('device_name')


def save_device(device_id: int | None, device_name: str) -> None:
	"""Save selected device."""
	config = load_config()
	config['device_id'] = device_id
	config['device_name'] = device_name
	save_config(config)


def get_device_channel(device_id: int) -> int:
	"""Get saved channel for a device (defaults to 0)."""
	config = load_config()
	channels = config.get('device_channels', {})
	return channels.get(str(device_id), 0)


def save_device_channel(device_id: int, channel: int) -> None:
	"""Save channel preference for a device."""
	config = load_config()
	if 'device_channels' not in config:
		config['device_channels'] = {}
	config['device_channels'][str(device_id)] = channel
	save_config(config)


def get_api_config() -> tuple[str | None, str | None]:
	"""Get saved API configuration.

	Returns:
		Tuple of (base_url, api_key). Either may be None if not set.
	"""
	config = load_config()
	return config.get('base_url'), config.get('api_key')


def save_api_config(base_url: str, api_key: str) -> None:
	"""Save API configuration.

	Args:
		base_url: Base URL for the swear-jar service
		api_key: API key for authentication
	"""
	config = load_config()
	config['base_url'] = base_url
	config['api_key'] = api_key
	save_config(config)
