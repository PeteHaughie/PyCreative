"""
pycreative.media: Audio/Video playback module using ffmpeg for MVP.
"""
import threading
import cv2
import pygame
import numpy as np
import time
from typing import Optional


class MediaPlayer:
    """
    Video/audio playback using OpenCV and pygame. All attributes are public and can be set after construction.

    Attributes:
        media_path: str — Path to media file
        cap: cv2.VideoCapture — OpenCV video capture object
        frame: pygame.Surface | None — Current video frame
        running: bool — Playback running state
        thread: threading.Thread | None — Decode thread
        loop: bool — Loop playback
        native_fps: float — FPS from media file
        video_fps: float — Target playback FPS
        paused: bool — Playback paused state
        _frame_interval: float — Frame interval (seconds)
        _last_frame_time: float — Last frame timestamp

    Usage:
        player = MediaPlayer(path)
        player.loop = True
        player.video_fps = 24.0
        player.play()
    """
    def resize(self, w: int, h: int):
        """
        Return the current frame scaled to (w, h) using pygame.transform.scale.
        """
        if self.frame is not None:
            return pygame.transform.scale(self.frame, (w, h))
        return None

    def __init__(self, media_path: str, loop: bool = False, video_fps: 'Optional[float]' = None):
        self.media_path = media_path
        self.cap = cv2.VideoCapture(media_path)
        self.frame = None
        self.running = False
        self.thread = None
        self.loop = loop
        self.native_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.video_fps = video_fps if video_fps is not None else self.native_fps
        self._frame_interval = 1.0 / self.video_fps
        self._last_frame_time = 0.0
        self.paused = False

    def _decode_loop(self):
        while self.running:
            if self.paused:
                time.sleep(0.05)
                continue
            now = time.time()
            if now - self._last_frame_time < self._frame_interval:
                time.sleep(max(0, self._frame_interval - (now - self._last_frame_time)))
                continue
            self._last_frame_time = time.time()
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surf = pygame.surfarray.make_surface(np.rot90(frame))
                self.frame = surf
            else:
                if self.loop:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                self.frame = None
                self.running = False

    def play(self):
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Media file not found or cannot be opened: {self.media_path}")
        if self.thread and self.thread.is_alive():
            # Only resume if paused
            if self.paused:
                self.resume()
            return
        self.running = True
        self.paused = False
        self.thread = threading.Thread(target=self._decode_loop, daemon=True)
        self.thread.start()
    
    def pause(self):
        self.paused = True
        print(f"[MediaPlayer] paused set to True. paused={self.paused}")

    def resume(self):
        print(f"[MediaPlayer] resume() called. running={self.running}, paused={self.paused}, thread_alive={self.thread.is_alive() if self.thread else None}")
        self.paused = False
        print(f"[MediaPlayer] paused set to False. paused={self.paused}")
        self._last_frame_time = time.time()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.cap.release()
        self.frame = None

    def get_frame(self):
        return self.frame


# Usage Example:
# player = MediaPlayer("path/to/media.mp3")
# player.play()
# ...
# player.stop()
