"""Render an SVG with Skia directly into a pygame Surface and save a PNG.

This bypasses the repo's shape parsing to verify Skia->pygame integration.
"""
from pathlib import Path
import sys

SVG_DEFAULT = Path('tests/assets/module_1.svg')
OUT_PATH = Path('tests/assets/out_snapshots/skia/skia_pygame_probe.png')


def _get_bytes_from_skia_image(img):
    try:
        data = img.encodeToData()
        if data is None:
            return None
        # try common accessors
        for name in ('toBytes', 'to_bytes'):
            fn = getattr(data, name, None)
            if fn:
                try:
                    return bytes(fn()) if callable(fn) else bytes(fn)
                except Exception:
                    continue
        try:
            return bytes(data)
        except Exception:
            return None
    except Exception:
        return None


def main(argv):
    try:
        import skia
    except Exception as e:
        print('skia not available:', e)
        return 2
    try:
        import pygame
    except Exception as e:
        print('pygame import failed:', e)
        return 2

    svg_path = Path(argv[1]) if len(argv) > 1 else SVG_DEFAULT
    if not svg_path.exists():
        print('SVG not found:', svg_path)
        return 2

    # render size
    W, H = 400, 400

    try:
        # Use MemoryStream-based constructor which is most reliable across skia-python builds
        dom = None
        try:
            mem = skia.MemoryStream(svg_path.read_bytes())
            dom = skia.SVGDOM.MakeFromStream(mem)
            print('SVGDOM.MakeFromStream succeeded, dom=', repr(dom))
        except Exception as e:
            print('SVGDOM.MakeFromStream failed', type(e).__name__, e)
            dom = None

        if dom is None:
            print('Failed to construct SVGDOM (stream); falling back to synthetic test drawing')

        try:
            if dom is not None:
                if hasattr(dom, 'setContainerSize'):
                    dom.setContainerSize(skia.Size(W, H))
                canvas = surf.getCanvas()
                canvas.clear(skia.ColorWHITE)
                dom.render(canvas)
            else:
                # fallback: draw a simple test pattern directly with Skia
                canvas = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)).getCanvas()
                canvas.clear(skia.ColorWHITE)
                p = skia.Path()
                p.addRect(skia.Rect(40, 40, W-40, H-40))
                paint = skia.Paint()
                paint.setAntiAlias(True)
                paint.setStyle(skia.Paint.kFill_Style)
                paint.setColor(skia.ColorSetARGB(255, 200, 80, 80))
                canvas.drawPath(p, paint)
                c2 = skia.Paint()
                c2.setAntiAlias(True)
                c2.setStyle(skia.Paint.kStroke_Style)
                c2.setStrokeWidth(6)
                c2.setColor(skia.ColorSetARGB(255, 0, 0, 0))
                canvas.drawCircle(W/2, H/2, min(W, H)/6, c2)
                img = canvas.getSurface().makeImageSnapshot()
        except Exception as e:
            print('rendering failed', type(e).__name__, e)
            return 2
        # img should be set by either DOM render or synthetic fallback
        try:
            img
        except NameError:
            print('No image snapshot produced')
            return 2
        raw = _get_bytes_from_skia_image(img)
        from PIL import Image
        if raw is not None:
            try:
                im = Image.open(__import__('io').BytesIO(raw)).convert('RGBA')
            except Exception:
                im = None
        else:
            # fallback to reading pixels
            try:
                buf = bytearray(W * H * 4)
                ok = surf.readPixels(info, buf)
                if ok:
                    im = Image.frombuffer('RGBA', (W, H), bytes(buf), 'raw', 'RGBA', 0, 1).convert('RGBA')
                else:
                    im = None
            except Exception:
                im = None

        if im is None:
            print('Failed to get PIL image from Skia snapshot')
            return 2

        # Blit into pygame surface
        pygame.init()
        pg_surf = pygame.Surface((W, H), flags=pygame.SRCALPHA)
        try:
            pg_img = pygame.image.fromstring(im.tobytes(), im.size, 'RGBA')
            pg_surf.blit(pg_img, (0, 0))
            OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(pg_surf, str(OUT_PATH))
            print('Saved', OUT_PATH)
        finally:
            pygame.quit()
        return 0
    except Exception as e:
        print('probe failed', type(e).__name__, e)
        return 2


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
