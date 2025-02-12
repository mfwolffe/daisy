"""
Graphics controller for daisy cli

Handles threaded ansi rendering of that iconic crimson glow
Simulates the shutting down during singing of 'daisy' with
flickering/fade

  NOTE: graphics currently makes use of a shared Console instance to the driver 
"""


import time
import random
import sys
import logging
from rich.text import Text
from config import DEFAULT_CONFIG


def blink_blink(console, flicker_speed=None):
    """
      Render HAL's eye in the terminal with flickering effect to
      emulate his shutting down at the hand of David Bowman (self defence)

      passed the shared rich console instance to use for render
    """
    if not sys.stdout.isatty():
        logging.warning("Noninteractive terminal detected. Graphical effects may not render properly")

    logging.info(f"Rendering HAL’s eye with flicker speed: {flicker_speed if flicker_speed else 'default range'}")

    