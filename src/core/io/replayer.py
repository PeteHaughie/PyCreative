"""Offscreen replayer for recorded GraphicsBuffer commands.

This module provides a minimal rasteriser using Pillow so tests and
developers can visualise recorded commands without opening a GL window.
"""
from __future__ import annotations

from typing import Any

from PIL import Image, ImageDraw


def replay_to_image(engine: Any, path: str) -> None:
    """Replay engine.graphics.commands to a PNG saved at `path`.

    Supports basic ops: 'background', 'rect', 'line'. Colors are expected
    as (r,g,b) tuples in 0-255 range. Coordinates are treated as top-left
    origin (to match sketch API).
    """
    w = int(getattr(engine, 'width', 200))
    h = int(getattr(engine, 'height', 200))
    img = Image.new('RGBA', (w, h), (200, 200, 200, 255))
    draw = ImageDraw.Draw(img)

    for cmd in getattr(engine.graphics, 'commands', []):
        op = cmd.get('op')
        args = cmd.get('args', {})
        if op == 'background':
            r = int(args.get('r', 200))
            g = int(args.get('g', 200))
            b = int(args.get('b', 200))
            draw.rectangle([(0, 0), (w, h)], fill=(r, g, b, 255))
        elif op == 'rect':
            x = int(args.get('x', 0))
            y = int(args.get('y', 0))
            rw = int(args.get('w', 0))
            rh = int(args.get('h', 0))
            fill = args.get('fill')
            stroke = args.get('stroke')
            sw = int(args.get('stroke_weight', 1) or 1)
            if fill is not None:
                if isinstance(fill, (tuple, list)):
                    draw.rectangle([(x, y), (x + rw, y + rh)], fill=tuple(fill) + (255,))
                else:
                    v = int(fill)
                    draw.rectangle([(x, y), (x + rw, y + rh)], fill=(v, v, v, 255))
            if stroke is not None and sw > 0:
                if isinstance(stroke, (tuple, list)):
                    color = tuple(stroke)
                else:
                    color = (int(stroke), int(stroke), int(stroke))
                # draw outline with stroke width by drawing multiple rectangles
                for i in range(sw):
                    draw.rectangle([(x + i, y + i), (x + rw - i, y + rh - i)], outline=color)
        elif op == 'line':
            x1 = int(args.get('x1', 0))
            y1 = int(args.get('y1', 0))
            x2 = int(args.get('x2', 0))
            y2 = int(args.get('y2', 0))
            stroke = args.get('stroke', (0, 0, 0))
            sw = int(args.get('stroke_weight', 1) or 1)
            color = tuple(stroke) if isinstance(stroke, (tuple, list)) else (int(stroke),) * 3
            draw.line([(x1, y1), (x2, y2)], fill=color, width=sw)

    img.save(path)
