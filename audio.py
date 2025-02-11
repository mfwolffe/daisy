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

# NOTE: not sure how it'll fare performance wise with
#       the voice synthesis
#
#
def process_raw(audio, decay_factor):
    """
      Applies low-pass filtering and distortions to help
      with simulation of progressive voice degradation

      The larger the decay_factor, the HAL sounds degraded, and,
      closer to shutdown :( (or should it be :) ?)
    """
    low_pass_end   = 800
    low_pass_start = 3000


    # NOTE: apply decay factor to frequency range
    #       @ decay = 0.0 -> 3000 (HZ), ie, clear, normal voice
    #        ...
    #       @ decay = 1.0 -> 800 (Hz), ie, should be barely recognizable
    #
    cutoff_freq = int(low_pass_start - (low_pass_start - low_pass_end) * (1 - decay_factor))
    logging.debug(f"Applying low-pass filter: {cutoff_freq} Hz")
    audio = apply_low_pass(audio, cutoff_freq)

    audio = apply_glitch_effect(audio, intensity=decay_factor)

    return audio


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
    """ 
        Randomly introduces distortion effects to mimic HAL’s failing voice 

        Does so by reducing sample rate to yield glitch effects, causing HAL to 
        exude instability
        Higher values of `intensity` create larger corruptions

        examples:
            0.0 -> No effect
            0.1 -> Mild, occasional glitch
            0.3 -> Frequent distortion
            0.7 -> severe degradation
            1.0 -> heavy corruption; likely incomprehensible
    """
    if random.random() < 0.2:
        logging.debug("Applying glitch effect")
        return audio.set_frame_rate(int(audio.frame_rate * (1 - intensity)))
    return audio


def daisy_daisy(volume=1.0, voice="synth"):
    """ Handles playbackk of daisy bell, whether voice synthesis or prerecorded """
    logging.info(f"Playing 'Daisy Bell' with {voice} mode at volume {volume}")

    # NOTE: the effects are not applied atm in either format; 
    #       making this modular will require a bit of consideration
    #       since one is audio generated on the fly and the other is pre-
    #       recorded
    #
    if voice == "recording":
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(AUDIO_FILE)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()

            # NOTE: to prevent exit & thread terminating early
            #       switched from `pass` to sleeping to avoid busy wait
            # TODO: @mfwolffe testing on the waiting
            #
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
        except pygame.error as e:
            logging.error(f"audio playback failure: {e}")
            return
    elif voice == "synth":
        engine = pyttsx3.init()
        engine.setProperty("volume", volume)

        lyrics = [
            "Daisy, Daisy, give me your answer, do...",
            "I'm half crazy, all for the love of you...",
            "It won't be a stylish marriage...",
            "I can't afford a carriage...",
            "But you'll look sweet upon the seat...",
            "Of a bicycle built for two..."
        ]

        for line in lyrics:
            engine.say(line)
            engine.runAndWait()