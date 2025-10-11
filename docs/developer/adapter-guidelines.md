Adapter guidelines

This document clarifies the responsibilities and expectations for adapters and
the renderer so contributors don't duplicate logic or create subtle coupling.

Principles
- Single responsibility: adapters integrate with external libraries and expose
  a small, well-documented surface (e.g., draw_circle(surface, x, y, r, **kwargs)).
- No duplicated drawing logic: drawing algorithms belong in adapters. The
  renderer should only dispatch descriptor types to adapter methods.
- Ownership: the module that creates or allocates a resource (surface,
  texture) owns its lifecycle unless documentation states otherwise.

Recommended adapter API shape
- `create_display_surface(width, height) -> surface`
- `attach_skia_to_pygame(pygame_surface, adapter=None) -> skia_surface`
- Drawing methods on adapters should be simple, e.g.:
  - `draw_circle(surface, x, y, r, color, stroke)`
  - `draw_rect(surface, x, y, w, h, color, stroke)`

Renderer responsibility
- Provide a dispatch mapping of descriptor type -> adapter method.
- Accept an adapter instance at construction time; never import adapters
  at module import time.

Example
```
class Renderer:
    def __init__(self, adapter):
        self._adapter = adapter
        self._dispatch = {
            'circle': adapter.draw_circle,
            'rect': adapter.draw_rect,
        }

    def render(self, descriptors):
        for d in descriptors:
            fn = self._dispatch[d['type']]
            fn(**d['args'])
```
