"""
Audio controller for daisy cli

handles threaded audio playback, whether via voice synthesis (default)
or recording fallback (IBM 7094 daisy 'rendition' ;))
Applies degradation effects to simulate HAL's "death" (shutdown) as in the film
"""

import pygame
import pyttsx3
import time
import logging
import random
import io
from pydub import AudioSegment
from pydub.playback import play
from config import AUDIO_FILE



def apply_low_pass(audio, cutoff_freq):
    """
      Applies a low-pass filter to simulate HAL's muffled shutdown

      The lower the `cutoff_freq`, the more muffled and distant HAL’s voice sounds.
      examples:
          500   (Hz) -> no effect
          3000  (Hz) -> slightly muffled
          1500  (Hz) -> Noticeably muffled
          800   (Hz) -> Very muffled, depending on sample probably inaudible

    """
    return audio.low_pass_filter(cutoff_freq)

def apply_glitch_effect(audio, intensity=0.2):
    """ Randomly introduces distortion effects to mimic HAL’s failing voice """
    if random.random() < 0.2:
        logging.debug("Applying glitch effect")
        return audio.set_frame_rate(int(audio.frame_rate * (1 - intensity)))
    return audio