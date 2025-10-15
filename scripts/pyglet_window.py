#! /usr/bin/env python3

import pyglet

from pyglet import shapes

window = pyglet.window.Window(800, 600, "Pyglet Window Test")
rect = shapes.Rectangle(100, 100, 200, 150, color=(500, 225, 30), batch=None)

@window.event
def on_draw():
    window.clear()
    rect.draw()

pyglet.app.run()