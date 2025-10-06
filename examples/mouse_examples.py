"""Mouse interaction examples combined.

This single example demonstrates Processing-style mouse hooks supported by
PyCreative: mouse_pressed, mouse_released, mouse_moved and mouse_dragged.

- Drag (click and hold + move) the mouse to change the rectangle fill value.
- Move the mouse (no button) to update the crosshair position.
- Click to spawn bouncing circles (movers); release stops spawning.

Run with:
    pycreative examples/mouse_examples.py

This file intentionally avoids heavy dependencies and uses only the public
`Sketch` API so it works as a reference for beginners and educators.
"""

from random import uniform
from pycreative.app import Sketch


class MouseExamples(Sketch):
    def setup(self):
        self.size(640, 360)
        self.cross = (None, None)  # last mouse_moved position
        # Single mover instance (or None)
        self.mover = None
        # HUD rectangle that can be dragged around to demonstrate drag behavior
        self.hud = {"x": float(self.width - 40), "y": 10.0, "w": 30.0, "h": 100.0}
        self._hud_dragging = False
        self._hud_drag_offset = (0.0, 0.0)

    # --- drawing ---
    def draw(self):
        # white background
        self.background((255, 255, 255))

        # rectangle whose fill is changed while dragging
        mx = self.mouse_x if self.mouse_x is not None and self.mouse_x != 0 else 1
        my = self.mouse_y if self.mouse_y is not None and self.mouse_y != 0 else 1
        sum_mx_my = (self.mouse_x if self.mouse_x is not None else 0) + (self.mouse_y if self.mouse_y is not None else 0)
        sum_mx_my = sum_mx_my if sum_mx_my != 0 else 1
        map_x = int(self.map(mx, 0, self.width, 1, 255))
        map_y = int(self.map(my, 0, self.height, 1, 255))
        map_sum = int(self.map(sum_mx_my, 0, self.width + self.height, 1, 255))
        self.fill((map_x, map_y, map_sum))
        self.rect(25, 25, 50, 50)

        # crosshair showing current mouse position (if available)
        mx = self.mouse_x
        my = self.mouse_y
        if mx is not None and my is not None:
            self.stroke((0, 0, 0))
            self.line(mx - 10, my, mx + 10, my)
            self.line(mx, my - 10, mx, my + 10)

        # draw single mover if present
        if self.mover is not None:
            m = self.mover
            self.fill((150, 200, 255))
            self.ellipse(m['x'], m['y'], m['r'] * 2, m['r'] * 2)

        # HUD: draggable rectangle that shows whether a mover exists
        self.no_stroke()
        # background of HUD
        self.fill((200, 200, 200))
        self.rect(self.hud['x'], self.hud['y'], self.hud['w'], self.hud['h'])

    # --- simple physics for movers ---
    def update(self, dt: float = 0) -> None:
        # update single mover physics
        if self.mover is not None:
            m = self.mover
            m['x'] += m['vx']
            m['y'] += m['vy']
            # gravity
            m['vy'] += 0.2
            # bounce
            if m['x'] < m['r']:
                m['x'] = m['r']
                m['vx'] *= -0.9
            if m['x'] > self.width - m['r']:
                m['x'] = self.width - m['r']
                m['vx'] *= -0.9
            if m['y'] > self.height - m['r']:
                m['y'] = self.height - m['r']
                m['vy'] *= -0.9

    # --- mouse hooks ---
    def mouse_dragged(self):
        # If dragging the HUD rectangle, move it; otherwise modify the value
        if self._hud_dragging:
            mx = self.mouse_x or 0
            my = self.mouse_y or 0
            nx = float(mx) - self._hud_drag_offset[0]
            ny = float(my) - self._hud_drag_offset[1]
            # clamp within window
            nx = max(0.0, min(self.width - self.hud['w'], nx))
            ny = max(0.0, min(self.height - self.hud['h'], ny))
            self.hud['x'] = nx
            self.hud['y'] = ny

    def mouse_moved(self):
        # update crosshair to the event-driven mouse position
        self.cross = (self.mouse_x, self.mouse_y)

    def mouse_pressed(self):
        # If click inside HUD, start dragging it
        mx = self.mouse_x or 0
        my = self.mouse_y or 0
        hx, hy, hw, hh = self.hud['x'], self.hud['y'], self.hud['w'], self.hud['h']
        if mx >= hx and mx <= hx + hw and my >= hy and my <= hy + hh:
            self._hud_dragging = True
            self._hud_drag_offset = (float(mx) - hx, float(my) - hy)
            return

        # Otherwise create or reset the single mover at mouse location
        x = mx or (self.width // 2)
        y = my or (self.height // 2)
        self.mover = {
            'x': float(x),
            'y': float(y),
            'vx': uniform(-2, 2),
            'vy': uniform(-2, 0),
            'r': uniform(6, 18),
        }

    def mouse_released(self):
        # stop HUD dragging if active
        if self._hud_dragging:
            self._hud_dragging = False
            return
        # optionally clear the mover on release (keep it for demo; do nothing)
        self.mover = None


if __name__ == '__main__':
    MouseExamples().run()
