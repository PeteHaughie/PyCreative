import pytest
from pycreative.audio import AudioPlayer
import pygame
import os

def test_audio_player_load_and_play():
    # Use a short, valid audio file for CI (replace with actual test asset)
    test_path = 'examples/data/groove.mp3'
    if not os.path.exists(test_path):
        pytest.skip('Test audio file not found')
    player = AudioPlayer(test_path)
    assert player.sound is not None, 'AudioPlayer failed to load sound'
    player.set_volume(0.2)
    assert player.volume == 0.2
    player.loop = True
    player.play()
    assert player.playing is True
    player.pause()
    assert player.paused is True
    player.resume()
    assert player.playing is True
    player.stop()
    assert player.playing is False
