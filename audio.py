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


LYRICS = [
    "Daisy, Daisy, give me your answer, do...",
    "I'm half crazy, all for the love of you...",
    "It won't be a stylish marriage...",
    "I can't afford a carriage...",
    "But you'll look sweet upon the seat...",
    "Of a bicycle built for two..."
]

LINES = len(LYRICS)


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


# NOTE: not sure how it'll fare performance wise with
#       the voice synthesis
#
#
def process_raw(audio, decay_factor):
    """
      Applies low-pass filtering and distortions to help
      with simulation of progressive voice degradation

      The larger the decay_factor (a float 0.0 - 1.0), the HAL sounds degraded, and,
      closer to shutdown :( (or should it be :) ?)
    """
    low_pass_end   = 800
    low_pass_start = 3000


    # NOTE: apply decay factor to frequency range
    #       @ decay = 0.0 -> 3000 (HZ), ie, clear, normal voice
    #        ...
    #       @ decay = 1.0 -> 800  (Hz), ie, should be barely recognizable
    #
    cutoff_freq = int(low_pass_start - (low_pass_start - low_pass_end) * (1 - decay_factor))
    logging.debug(f"Applying low-pass filter: {cutoff_freq} Hz")
    audio = apply_low_pass(audio, cutoff_freq)

    audio = apply_glitch_effect(audio, intensity=decay_factor)

    return audio


def daisy_daisy(volume=1.0, voice="synth"):
    """ Handles playbackk of daisy bell, whether voice synthesis or prerecorded """
    logging.info(f"Playing 'Daisy Bell' with {voice} mode at volume {volume}")

    # NOTE: making this modular will required a bit of consideration, and I'm
    #       not sold this approach is best (when is any approach, esp. one I choose, best, after all?)
    #       since one is audio generated on the fly and the other is pre-recorded
    #
    if voice == "recording":
        try:
            pygame.mixer.music.set_volume(volume)

            audio = AudioSegment.from_file(AUDIO_FILE, format="mp3")

            for i in range(LINES):
                decay_factor = i / LINES
                processed = process_raw(audio, decay_factor)
                play(processed)

        # NOTE: to prevent exit & thread terminating early
        #       switched from `pass` to sleeping to avoid busy wait
        # TODONT: @mfwolffe testing on the waiting
        # NOTE: with the opted approach to produce a degradation the
        #       guarding below is no longer necessary
        # while pygame.mixer.music.get_busy():
        #     time.sleep(0.1)
        # NOTE: pygame is also only being used now for volume 
        #       (maybe drop it altogether idk), so exception handling
        #       needed reapproaching
        # except pygame.error as e:
        except FileNotFoundError:
            logging.error(f"Audio file not found: {AUDIO_FILE}")
            return
        except PermissionError:
            logging.error(f"Permission denied: cannot read {AUDIO_FILE}")
            return
        except Exception as e:
            logging.error(f"Unexpected error during playback: {e}")
            return
        
    # NOTE: this approach requires some commenting on
    #       The io ops introduced should not actually cause 
    #       large slowdowns, as ByteIO() avoids disk writes
    #
    #       unless pyttsx3's save_to_file is excessively slow,
    #       it shouldn't be a concern
    #
    # TODO: @mfwolffe pay attention to hangs in voice synth
    #                 and test against io operations
    #
    elif voice == "synth":
        engine = pyttsx3.init()
        engine.setProperty("volume", volume)

        min_rate  = 40
        base_rate = 100

        # TODO: @mfwolffe apply processing
        #
        # NOTE: shoutout to Robert, and not for bagels or explaining CMYK
        #       color spaces (acmY? :iykyk). That guy is an apparition.
        #       Oliver though, that one, shoutout to him for showing me enumerate()
        #       and other python shorthands back during square 1 (the recapitulation, that is)
        #
        for i, line in enumerate(LYRICS):
            decay_factor = i / LINES

            slowed_rate = int(base_rate - (base_rate - min_rate) * (1 - decay_factor))
            engine.setProperty("rate", slowed_rate)

            # see note above for loop header 
            audio_io = io.BytesIO()
            engine.save_to_file(line, audio_io)
            engine.runAndWait()

            audio_io.seek(0)
            audio = AudioSegment.from_file(audio_io, format="wav")

            processed = process_raw(audio, decay_factor)
            play(processed)

            time.sleep(0.5 * (1 - decay_factor))
