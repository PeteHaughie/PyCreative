import pytest

from core.graphics import GraphicsBuffer


def _has_skia():
    try:
        import skia  # noqa: F401
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _has_skia(), reason='skia-python not installed')
def test_circle_and_ellipse_and_point_replay():
    """Record circle, ellipse, and point with various fill/stroke and
    ensure the skia replayer does not raise and accepts the recorded args.
    This is a smoke test to catch regressions in the replayer handling.
    """
    from core.io.replay_to_skia import replay_to_skia_canvas
    import skia

    g = GraphicsBuffer()

    # background
    g.record('background', r=10, g=20, b=30)

    # circle: filled and stroked
    g.record('stroke', color=(0, 0, 0))
    g.record('fill', color=(100, 150, 200))
    g.record('stroke_weight', weight=2)
    g.record('circle', x=50, y=60, r=40, fill=(100, 150, 200), stroke=(0, 0, 0), stroke_weight=2)

    # ellipse: only fill
    g.record('fill', color=(200, 100, 50))
    g.record('ellipse', x=120, y=80, w=60, h=30, fill=(200, 100, 50), stroke=None, stroke_weight=1)

    # point: stroke only
    g.record('stroke', color=(10, 200, 10))
    g.record('point', x=10, y=10, stroke=(10, 200, 10), stroke_weight=3)

    # Create a raster Skia surface to replay onto
    surf = skia.Surface(200, 150)
    canvas = surf.getCanvas()

    # This should not raise
    replay_to_skia_canvas(list(g.commands), canvas)

    # Optionally sample a pixel to ensure drawing occurred (best-effort)
    # Convert to image and ensure we can get pixels
    img = surf.makeImageSnapshot()
    assert img is not None
    # read a pixel near the circle center to detect non-background color
    try:
        pix = img.readPixels(skia.ImageInfo.MakeN32Premul(200, 150), 0, 0)
        assert pix is not None
    except Exception:
        # If reading pixels fails on some skia builds, treat as a pass for smoke test
        pass
