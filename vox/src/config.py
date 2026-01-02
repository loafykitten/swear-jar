"""Configuration persistence for Vox settings."""

import json
from pathlib import Path
from typing import TypedDict, cast

CONFIG_DIR = Path.home() / '.config' / 'vox'
CONFIG_FILE = CONFIG_DIR / 'settings.json'


class VoxConfig(TypedDict, total=False):
	"""Configuration schema."""

	device_id: int | None
	device_name: str | None
	device_channels: dict[str, int]  # Key: str(device_id), Value: channel index
	base_url: str | None
	api_key: str | None
	model_size: str | None


# Module-level cache to avoid repeated disk I/O
_config_cache: VoxConfig | None = None


def load_config() -> VoxConfig:
	"""Load configuration from disk (cached after first load)."""
	global _config_cache
	if _config_cache is not None:
		return _config_cache

	if not CONFIG_FILE.exists():
		_config_cache = {}
		return _config_cache
	try:
		with open(CONFIG_FILE, 'r') as f:
			loaded = json.load(f)
			config: VoxConfig = cast(VoxConfig, loaded) if isinstance(loaded, dict) else {}
			_config_cache = config
			return config
	except (json.JSONDecodeError, IOError):
		config: VoxConfig = {}
		_config_cache = config
		return config


def save_config(config: VoxConfig) -> None:
	"""Save configuration to disk and update cache."""
	global _config_cache
	CONFIG_DIR.mkdir(parents=True, exist_ok=True)
	with open(CONFIG_FILE, 'w') as f:
		json.dump(config, f, indent=2)
	_config_cache = config


def invalidate_config_cache() -> None:
	"""Invalidate the config cache to force reload from disk."""
	global _config_cache
	_config_cache = None


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


def get_model_size() -> str:
	"""Get saved model size (defaults to 'base')."""
	config = load_config()
	return config.get('model_size') or 'base'


def save_model_size(size: str) -> None:
	"""Save model size preference."""
	config = load_config()
	config['model_size'] = size
	save_config(config)
