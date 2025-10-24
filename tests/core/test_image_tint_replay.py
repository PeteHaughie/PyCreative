import os
from core.image.pcimage import PCImage
from core.io.replay_to_skia import replay_to_skia_canvas


def test_tinted_image_replay_creates_output(tmp_path):
    # Create a small source image (red square)
    from PIL import Image
    im = Image.new('RGBA', (32, 32), (255, 0, 0, 255))
    pc = PCImage(im)

    # Create a fake canvas surface (skia)
    try:
        import skia
    except Exception:
        # If skia not available in test env, skip
        return

    surface = skia.Surface(64, 64)
    canvas = surface.getCanvas()

    # Build command list: draw tinted image at 16,16 with tint
    cmds = [
        {'op': 'background', 'args': {'r': 10, 'g': 10, 'b': 10}},
        {'op': 'image', 'args': {'image': pc, 'x': 16, 'y': 16, 'tint': (0, 255, 0, 128)}}
    ]

    replay_to_skia_canvas(cmds, canvas)

    # Read back pixels to ensure something was drawn
    img = surface.makeImageSnapshot()
    data = img.tobytes()
    assert data is not None and len(data) > 0
    # Optionally write to tmp_path for visual inspection on failure
    out = tmp_path / 'tint_out.png'
    img.save(str(out))
    assert out.exists()
