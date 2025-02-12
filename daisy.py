"""
Driver for Daisy CLI

Handles argument parsing, config loading, and multithreading
for audio playback and 'graphics' (`rich`) rendering
"""


import time
import pygame
import logging
import argparse
import threading
from audio import daisy_daisy
from config import load_config
from graphics import blink_blink
from rich.console import Console


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


def main():
    args = parse_cli()
    setup_logger(args.debug)

    config   = load_config(args.config)
    voice    = args.voice if args.voice else config["voice"]
    volume   = args.volume if args.volume is not None else config["volume"]
    flk_spd = args.flicker_speed if args.flicker_speed is not None else config["flicker_speed"]

    logging.info(f"Using config - Volume: {volume}, Flicker Speed: {flk_spd}, Voice: {voice}")

    # NOTE: I did not realize before that after this call 
    #       SDL audio backend state is updated, and the context
    #       is process-wide
    #       As such, initialize before threads forked
    #
    pygame.mixer.init()

    # NOTE: thread task targets are placeholders for now
    #       That said, most everything is done ...elsewhere
    # TODO: @mfwolffe write them ;)
    #
    audio_thread = threading.Thread(target=daisy_daisy, args=(volume, voice))
    graphics_thread = threading.Thread(target=blink_blink, args=(console, flk_spd))


    # NOTE: embrasingly parallel, so not much synchronization
    #       protection needed?
    # TODO: @mfwolffe handling for thread errors in their
    #                 respective files 
    audio_thread.start()
    graphics_thread.start()

    audio_thread.join()
    graphics_thread.join()

    console.print("HAL has shut down.", style="dim")


if __name__ == "__main__":
    main()


