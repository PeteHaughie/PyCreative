import os
import tempfile
from core.engine import impl as engine_impl
from core.engine import snapshot as snapshot_mod


def test_snapshot_backend_called(tmp_path):
    eng = engine_impl.Engine(sketch_module=None, headless=True)
    eng.width = 123
    eng.height = 77

    called = {}

    def backend(path, w, h, engine_obj):
        called['path'] = path
        called['w'] = w
        called['h'] = h
        called['engine'] = engine_obj
        # write a tiny file so caller can verify write
        with open(path, 'wb') as f:
            f.write(b'FAKEPNG')

    eng.snapshot_backend = backend
    target = str(tmp_path / 'out-####.png')

    # call the snapshot helper which should use the backend
    snapshot_mod.save_frame(eng, target)

    assert 'path' in called
    assert called['w'] == 123
    assert called['h'] == 77
    assert os.path.exists(called['path'])


class DummyPresenter:
    def __init__(self, img_bytes=None):
        self.surface = None
        self._img_bytes = img_bytes

    def create_skia_surface(self):
        # return an object with makeImageSnapshot -> image -> encodeToData -> toBytes
        class FakeData:
            def __init__(self, b):
                self._b = b

            def toBytes(self):
                return self._b

        class FakeImage:
            def __init__(self, b):
                self._b = b

            def encodeToData(self):
                return FakeData(self._b)

        class FakeSurface:
            def __init__(self, b):
                self._b = b

            def makeImageSnapshot(self):
                return FakeImage(self._b)

        return FakeSurface(self._img_bytes)


def test_pending_save_frame_queued_when_in_draw_and_presenter_exists():
    eng = engine_impl.Engine(sketch_module=None, headless=False)
    # attach a dummy presenter
    eng._presenter = DummyPresenter()
    # simulate being inside draw
    eng._in_draw = True
    # ensure no pending initially
    assert getattr(eng, '_pending_save_frames', None) is None
    snapshot_mod.save_frame(eng, 'queued-####.png')
    pending = getattr(eng, '_pending_save_frames', None)
    assert pending is not None and len(pending) == 1
    assert pending[0]['op'] == 'save_frame'


def test_presenter_immediate_snapshot_uses_presenter_surface(tmp_path):
    eng = engine_impl.Engine(sketch_module=None, headless=False)
    # fake image bytes (PNG header) to be returned by fake surface
    fake_png = b"\x89PNG\r\n\x1a\nFAKE"
    eng._presenter = DummyPresenter(img_bytes=fake_png)
    eng.width = 50
    eng.height = 40
    target = str(tmp_path / 'presenter_immediate.png')

    # Not in draw(), so save_frame should try immediate snapshot via presenter's surface
    snapshot_mod.save_frame(eng, target)

    # file should exist and contain our fake bytes
    assert os.path.exists(target)
    with open(target, 'rb') as f:
        data = f.read()
    assert data.startswith(b"\x89PNG")
