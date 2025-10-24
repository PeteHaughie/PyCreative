import os
import tempfile
from pathlib import Path

from PIL import Image

from core.util.loader import load_module_from_path
from core.engine.impl import Engine


def test_load_image_resolves_data_folder(tmp_path: Path):
    # Create a fake sketch file in a temporary directory
    sketch_dir = tmp_path / 'sketch'
    sketch_dir.mkdir()
    sketch_file = sketch_dir / 'sketch.py'
    sketch_file.write_text('# dummy sketch file')

    # Create data/ subfolder and a tiny PNG
    data_dir = sketch_dir / 'data'
    data_dir.mkdir()
    img_path = data_dir / 'dont.png'
    im = Image.new('RGBA', (4, 4), (10, 20, 30, 255))
    # draw a red pixel at (1,1)
    im.putpixel((1, 1), (255, 0, 0, 255))
    im.save(str(img_path))

    # Load the sketch module using loader (this mirrors CLI behaviour)
    mod = load_module_from_path(str(sketch_file))

    # Construct Engine with sketch_module set; Engine registers image APIs
    eng = Engine(sketch_module=mod, headless=True)

    # Retrieve registered load_image wrapper and call it with relative path
    fn = eng.api.get('load_image')
    assert fn is not None
    pcimg = fn('dont.png')
    # pcimg should be a PCImage-like with width/height > 0
    assert pcimg is not None
    assert getattr(pcimg, 'width', 0) > 0
    assert getattr(pcimg, 'height', 0) > 0
    # ensure a pixel we set is present
    px = pcimg.get(1, 1)
    # PCImage stores (r,g,b,a) in 0..255 integers
    assert px[0] == 255 and px[1] == 0 and px[2] == 0
