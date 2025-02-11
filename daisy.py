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



