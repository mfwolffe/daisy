"""
Config handler for daisy
While the project is entirely a joke, I'm planning to package
As such, things should be FHS compliant
"""


import os
import yaml
import logging

SYSTEM_CONFIG_PATH = "/etc/daisy/config.yaml"
USER_CONFIG_PATH   = os.path.expanduser("~/.config/daisy/config.yaml")


# NOTE: fallback to local assets path in dev
#
#
LOCAL_AUDIO   = "assets/daisy.mp3"
DEFAULT_AUDIO = "/usr/share/daisy/daisy.mp3"
AUDIO_FILE    = DEFAULT_AUDIO if os.path.exists(DEFAULT_AUDIO) else LOCAL_AUDIO


DEFAULT_CONFIG = {
  # TODO @mfwolffe deb install or rules needs this path def
  #
  #
  "audio_file": "/usr/share/daisy/audio/daisy.mp3",
  "volume": 1.0,
  "flicker_speed": None,
  # NOTE: voice synthesis is default mode;
  #       fallback is recording of the IBM 7094
  #
  "voice": "synth",
}


def load_config(config_path=None):
    """Load YAML config, fall back to defaults if missing."""

    if config_path:
        logging.info(f"Loading custom config from {config_path}")
        paths_to_try = [config_path]
    else:
        paths_to_try = [USER_CONFIG_PATH, SYSTEM_CONFIG_PATH]

    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logging.error(f"Failed to load config from {path}: {e}")

    logging.warning("No valid config found. Using defaults.")
    return DEFAULT_CONFIG
