"""
pycreative.capture: Webcam/UVC device capture class for PyCreative.
"""
import cv2
import threading
import numpy as np
import pygame
from typing import Optional

class Capture:
    """
    Capture frames from a webcam or UVC-compliant device using OpenCV.

    Args:
        device_index (int): Index of the video device (default 0).
        width (int): Desired frame width (optional).
        height (int): Desired frame height (optional).

    Attributes:
        cap: cv2.VideoCapture
        frame: pygame.Surface | None
        running: bool
        thread: threading.Thread | None
        width: int
        height: int

    Usage:
        cam = Capture(0)
        cam.start()
        ...
        frame = cam.get_frame()
        cam.stop()
    """
    def __init__(self, device_index: int = 0, width: Optional[int] = None, height: Optional[int] = None):
        self.cap = cv2.VideoCapture(device_index)
        if width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        else:
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        if height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame = None
        self.running = False
        self.thread = None


    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surf = pygame.surfarray.make_surface(np.rot90(frame))
                self.frame = surf
            else:
                self.frame = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.cap.release()
        self.frame = None

    def get_frame(self) -> Optional[pygame.Surface]:
        return self.frame

    def is_opened(self) -> bool:
        return self.cap.isOpened()

    def __del__(self):
        self.stop()

# Utility: List available UVC devices
def list_devices(max_devices: int = 10):
    print("[Capture] Scanning for available UVC devices...")
    found = []
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[Capture] Device {i}: AVAILABLE")
            found.append(i)
        else:
            print(f"[Capture] Device {i}: not found")
        cap.release()
    if not found:
        print("[Capture] No UVC devices found.")
    return found


# Usage Example:
# cam = Capture(0)
# cam.start()
# ...
# frame = cam.get_frame()
# cam.stop()
