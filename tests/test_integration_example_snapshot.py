import os
import io
from PIL import Image, ImageDraw, ImageStat
import types
from core.engine import impl as engine_impl
from core.engine import snapshot as snapshot_mod


class FakePresenter:
    def __init__(self, w, h):
        self._w = w
        self._h = h
        # create PNG bytes with a red rect on black background
        im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
        draw = ImageDraw.Draw(im)
        draw.rectangle([w//4, h//4, w*3//4 - 1, h*3//4 - 1], fill=(255, 0, 0, 255))
        bio = io.BytesIO()
        im.save(bio, format='PNG')
        self._png = bio.getvalue()

    def create_skia_surface(self):
        # return fake surface whose makeImageSnapshot().encodeToData().toBytes() returns our PNG
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

        return FakeSurface(self._png)


# A tiny sketch module (module-like with Sketch class) that records drawing using engine APIs
class TinySketchModule(types.SimpleNamespace):
    class Sketch:
        def setup(self):
            # Request a small canvas
            self.size(40, 30)

        def draw(self):
            # draw something using API attached to instance
            self.background(0)
            self.no_stroke()
            self.fill(255, 0, 0)
            self.rect(self.width/4, self.height/4, self.width/2, self.height/2)


def test_integration_engine_presenter_snapshot(tmp_path):
    module = TinySketchModule()
    # create engine with the module; non-headless so save_frame prefers presenter
    eng = engine_impl.Engine(sketch_module=module, headless=False)
    # attach our fake presenter that will return a PNG
    eng._presenter = FakePresenter(eng.width, eng.height)

    # run sketch setup/draw (simulate engine loop)
    try:
        if hasattr(eng.sketch, 'setup'):
            eng.sketch.setup()
        if hasattr(eng.sketch, 'draw'):
            eng.sketch.draw()
    except Exception:
        # ensure test surfaces don't crash; fail loudly
        raise

    out = str(tmp_path / 'integration-0000.png')
    # call snapshot.save_frame outside draw() so immediate presenter snapshot is used
    snapshot_mod.save_frame(eng, out)

    assert os.path.exists(out)
    im = Image.open(out).convert('RGBA')
    st = ImageStat.Stat(im)
    # mean red channel should be greater than zero because FakePresenter drew a red rect
    mean_r = st.mean[0]
    assert mean_r > 0, f"expected red content in snapshot, got mean_r={mean_r}"
