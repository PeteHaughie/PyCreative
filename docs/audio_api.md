# PyCreative Audio API (pycreative.audio)

## Overview
The `pycreative.audio.AudioPlayer` class provides simple audio playback for sketches, supporting idiomatic, attribute-based configuration. It is designed for artists, educators, and rapid prototypers.

## Quickstart Example
```python
from pycreative.audio import AudioPlayer

player = AudioPlayer('examples/data/groove.mp3')
player.loop = True
player.set_volume(0.7)
player.play()

# To pause/resume:
player.pause()
player.resume()

# To stop:
player.stop()
```

## Attributes
- `path: str` — Path to audio file
- `loop: bool` — Loop playback (settable)
- `volume: float` — Volume (0.0 to 1.0, settable)
- `playing: bool` — Is audio currently playing
- `paused: bool` — Is audio currently paused
- `sound: pygame.mixer.Sound | None` — Loaded sound object
- `channel: pygame.mixer.Channel | None` — Playback channel

## Methods
- `play()` — Start playback
- `pause()` — Pause playback
- `resume()` — Resume playback
- `stop()` — Stop playback
- `set_volume(volume: float)` — Set volume

## Usage Patterns
- Set attributes after construction for live-coding:
  ```python
  player = AudioPlayer(path)
  player.loop = True
  player.set_volume(0.5)
  player.play()
  ```
- Control playback in response to input:
  ```python
  if mouse.left_down:
      if player.playing:
          player.pause()
      else:
          player.resume()
  ```

## Notes
- AudioPlayer uses PyGame's mixer, so supported formats are WAV, MP3, OGG, etc.
- All attributes are public and can be set or read at any time.
- For advanced use, you can access the PyGame `Sound` and `Channel` objects directly.

## Troubleshooting
- If playback does not start, check that the audio file exists and is supported by PyGame.
- For best results, use audio files with standard codecs.
- If you need to change volume or loop state at runtime, set the attribute and call `play()` or `set_volume()` as needed.

## API Reference
See the source in `src/pycreative/audio.py` for full details and docstrings.
