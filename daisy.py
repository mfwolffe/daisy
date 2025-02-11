"""
Driver for Daisy CLI

Handles argument parsing, config loading, and multithreading
for audio playback and 'graphics' (`rich`) rendering
"""


import argparse
import threading
import logging
import time
from rich.console import Console
from config import load_config


console = Console()


# NOTE: y'all. getopt got nothing.
#
#
def parse_cli():
    """ Parse command line for daisy cli """
    parsely = argparse.ArgumentParser(description="Daisy CLI | An Ode to Heuristics ;)")

    parsely.add_argument("--config", type=str, help="Path to custom user config")
    parsely.add_argument("--volume", type=float, help="Set audio playback volume (0.0 - 1.0)")
    parsely.add_argument("--flicker-speed", type=float, help="Set HAL eye flicker speed (seconds)")
    parsely.add_argument("--voice", choices=["synth", "recording"], help="Choose voice mode (voice synthesis or the IBM 7094)")
    parsely.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parsely.parse_args()


def setup_logger(debug):
    """ init logger for daisy cli """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=level)
    