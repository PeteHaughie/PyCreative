from core.image.pcimage import PCImage
from core.io.replay_to_skia import replay_to_skia_canvas


def test_global_tint_op_applies(tmp_path):
    try:
        import skia
    except Exception:
        return

    from PIL import Image
    src = Image.new('RGBA', (16, 16), (200, 50, 50, 255))
    pc = PCImage(src)

    surface = skia.Surface(64, 64)
    canvas = surface.getCanvas()

    cmds = [
        {'op': 'background', 'args': {'r': 20, 'g': 20, 'b': 20}},
        {'op': 'tint', 'args': {'color': (0, 255, 0, 128)}},
        {'op': 'image', 'args': {'image': pc, 'x': 8, 'y': 8}},
    ]

    replay_to_skia_canvas(cmds, canvas)
    img = surface.makeImageSnapshot()
    assert img is not None
    out = tmp_path / 'global_tint.png'
    img.save(str(out))
    assert out.exists()
