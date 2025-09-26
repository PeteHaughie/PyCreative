# PyCreative Media API (pycreative.media)

## Overview
The `pycreative.media.MediaPlayer` class provides simple video and audio playback for sketches, supporting live-coding and idiomatic attribute-based configuration. It is designed for artists, educators, and rapid prototypers.

## Quickstart Example
```python
from pycreative.media import MediaPlayer

player = MediaPlayer('path/to/video.mp4')
player.loop = True
player.video_fps = 24.0
player.play()

# In your sketch's draw method:
frame = player.resize(width, height)
if frame:
    screen.blit(frame, (0, 0))
```

## Attributes
- `media_path: str` — Path to the media file
- `cap: cv2.VideoCapture` — OpenCV video capture object
- `frame: pygame.Surface | None` — Current video frame (None if not available)
- `running: bool` — Playback running state
- `thread: threading.Thread | None` — Background decode thread
- `loop: bool` — Loop playback (settable)
- `native_fps: float` — FPS from media file
- `video_fps: float` — Target playback FPS (settable)
- `paused: bool` — Playback paused state (readable)

## Methods
- `play()` — Start playback (spawns decode thread)
- `pause()` — Pause playback
- `resume()` — Resume playback
- `stop()` — Stop playback and release resources
- `resize(w, h)` — Return current frame scaled to `(w, h)`
- `get_frame()` — Get current frame (unscaled)

## Usage Patterns
- Set attributes after construction for live-coding:
  ```python
  player = MediaPlayer(path)
  player.loop = True
  player.video_fps = 30.0
  player.play()
  ```
- Control playback in response to input:
  ```python
  if mouse.left_down:
      if player.paused:
          player.resume()
      else:
          player.pause()
  ```

## Notes
- MediaPlayer is designed for video files (mp4, avi, etc.) and can be extended for audio.
- All attributes are public and can be set or read at any time.
- For advanced use, you can access the OpenCV `cap` object directly.

## Troubleshooting
- If playback does not start, check that the media file exists and is supported by OpenCV.
- For best results, use video files with standard codecs (H.264, etc.).
- If you need frame-accurate control, set `video_fps` to match your sketch's frame rate.

## API Reference
See the source in `src/pycreative/media.py` for full details and docstrings.
