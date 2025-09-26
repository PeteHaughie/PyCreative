"""
pycreative.audio: Simple audio playback for PyCreative sketches (MVP).
"""
import pygame
from typing import Optional

class AudioPlayer:
    """
    Audio playback using pygame.mixer. All attributes are public and can be set after construction.

    Attributes:
        path: str — Path to audio file
        loop: bool — Loop playback
        volume: float — Volume (0.0 to 1.0)
        playing: bool — Is audio currently playing
        paused: bool — Is audio currently paused
        sound: pygame.mixer.Sound — Loaded sound object
        channel: pygame.mixer.Channel — Playback channel
    """
    def __init__(self, path: str, loop: bool = False, volume: float = 1.0):
        pygame.mixer.init()
        self.path = path
        self.loop = loop
        self.volume = volume
        self.playing = False
        self.paused = False
        self.sound: Optional[pygame.mixer.Sound] = None
        self.channel: Optional[pygame.mixer.Channel] = None
        try:
            self.sound = pygame.mixer.Sound(path)
            self.sound.set_volume(volume)
        except Exception as e:
            print(f"[AudioPlayer] Error loading sound: {e}")

    def play(self):
        if self.sound:
            loops = -1 if self.loop else 0
            self.channel = self.sound.play(loops=loops)
            self.playing = True
            self.paused = False

    def pause(self):
        if self.channel:
            self.channel.pause()
            self.paused = True
            self.playing = False

    def resume(self):
        if self.channel:
            self.channel.unpause()
            self.paused = False
            self.playing = True

    def stop(self):
        if self.channel:
            self.channel.stop()
            self.playing = False
            self.paused = False

    def set_volume(self, volume: float):
        self.volume = volume
        if self.sound:
            self.sound.set_volume(volume)

# Usage Example:
# player = AudioPlayer('path/to/audio.wav')
# player.loop = True
# player.play()
# player.set_volume(0.5)
# player.pause()
# player.resume()
# player.stop()
