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

    # NOTE: eye states with ansi styling
    #       this 'graphic' is not permanent
    #       (it's quite rudimentary - ●)
    #       but so is Hal's eye; just a pin of light.
    #       it's fine. matt's fine.
    #
    # TODO: @mfwolffe better graphic and effect
    # 
    frames = [
        "[bold red]●[/bold red]",
        "[red]●[/red]",
        "[dim red]●[/dim red]",
        " ",
    ]

    for _ in range(DEFAULT_CONFIG.get("flicker_duration", 50)):
        flicer_time = flicker_speed if flicker_speed else random.uniform(0.05, 0.2)

        # NOTE: picks a (weighted) random flicker frame/eye state
        #       (brighter more likely), then updates the 
        #       rendered eye in place in the conosle, and
        #       and finally waits
        #
        frame = random.choices(frames, weights=[4, 3, 2, 1])[0]
        console.print(Text(frame, justify="center"), end="\r")
        time.sleep(flicer_time)

    # NOTE: ensures 'hal shutdown' by overwriting 
    #       last frame
    #
    console.print(Text(" ", justify="center"))
