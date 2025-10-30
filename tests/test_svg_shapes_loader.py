import textwrap
from pathlib import Path

from pycreative.shape.loader import load_svg


MODULE_3 = textwrap.dedent('''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 50 50" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">
    <g transform="matrix(1,0,0,1,21.29,21.29)">
        <circle cx="0.329" cy="0.329" r="20.079"/>
        <circle cx="4.882" cy="4.882" r="22.288" style="fill-opacity:0.2;"/>
    </g>
</svg>
''')

MODULE_7 = textwrap.dedent('''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 100 100" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">
    <g transform="matrix(1,0,0,1,0.1665,0.5)">
        <circle cx="49.833" cy="49.5" r="49.334"/>
        <circle cx="53.168" cy="49.5" r="46" style="fill:white;"/>
        <circle cx="56.5" cy="49.5" r="42.666"/>
        <circle cx="60.5" cy="49.5" r="38.666" style="fill:white;"/>
        <circle cx="64.334" cy="49.5" r="34.833"/>
        <circle cx="68.334" cy="49.5" r="30.833" style="fill:white;"/>
        <circle cx="72.334" cy="49.5" r="26.833"/>
        <circle cx="77" cy="49.5" r="22.166" style="fill:white;"/>
        <circle cx="81.168" cy="49.5" r="18"/>
        <circle cx="85.5" cy="49.5" r="13.667" style="fill:white;"/>
        <circle cx="89.25" cy="49.5" r="9.917"/>
        <circle cx="93.668" cy="49.5" r="5.5" style="fill:white;"/>
    </g>
</svg>
''')

MODULE_4 = textwrap.dedent('''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 97 91" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">
    <g id="Artboard1" transform="matrix(1,0,0,1,23,20)">
        <rect x="-23" y="-20" width="97" height="91" style="fill:none;"/>
        <g transform="matrix(1,0,0,1,-213.628,-1.881)">
            <path d="M259.528,27.279L285.617,70.354L242.645,27.381L285.617,-15.592L259.528,27.279Z" style="fill-rule:nonzero;"/>
            <g transform="matrix(0.7071,0.7071,-0.7071,0.7071,83.3973,-146.379)">
                <rect x="200.187" y="9.271" width="36.422" height="36.423" style="fill-opacity:0.2;"/>
            </g>
        </g>
    </g>
</svg>
''')


def _write_and_load(tmp_path: Path, name: str, content: str):
    p = tmp_path / f"{name}.svg"
    p.write_text(content, encoding='utf-8')
    shape = load_svg(str(p))
    return shape


def test_module_3_and_7_produce_paths(tmp_path: Path):
    s3 = _write_and_load(tmp_path, 'module_3', MODULE_3)
    assert s3 is not None
    assert hasattr(s3, 'skia_paths')
    assert len(s3.skia_paths) >= 1

    s7 = _write_and_load(tmp_path, 'module_7', MODULE_7)
    assert s7 is not None
    assert hasattr(s7, 'skia_paths')
    assert len(s7.skia_paths) >= 1


def test_module_4_path_transformed_into_view(tmp_path: Path):
    s4 = _write_and_load(tmp_path, 'module_4', MODULE_4)
    assert s4 is not None
    assert hasattr(s4, 'skia_paths')
    assert len(s4.skia_paths) >= 1
    # At least one path should have non-empty bounds
    ok = False
    for p in s4.skia_paths:
        try:
            b = p.computeTightBounds()
            w = b.right() - b.left()
            h = b.bottom() - b.top()
            if w > 0 and h > 0:
                ok = True
                # bounds should be inside a reasonable area (not huge offscreen)
                assert -1000 < b.left() < 2000
                assert -1000 < b.top() < 2000
                break
        except Exception:
            continue
    assert ok
