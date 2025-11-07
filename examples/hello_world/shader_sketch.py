"""Shader Hello World — loads data/tint.frag and uses it for drawing.

This sketch demonstrates setting a `PCShader` as the active shader
and drawing a full-canvas rect that the presenter should shade.
"""

from pycreative.graphics import load_shader
import pycreative as _pc

class Sketch:
    def setup(self):
        self.size(320, 240)
        self.window_title('Hello: Shader Tint')
        # load shader from data/tint.frag (relative to this sketch)
        try:
            s = load_shader('tint.frag')
            if s is None:
                return
            # set active shader via API
            try:
                self.shader(s)
            except Exception:
                pass

            # also record explicitly so presenters see the shader op
            try:
                eng = _pc._get_engine()
                g = getattr(eng, 'graphics', None)
                if g is not None:
                    try:
                        g.record('shader', shader=s)
                    except Exception:
                        pass
            except Exception:
                pass

            # If a presenter exists, ask it to ensure resources so it will
            # attempt to compile newly-registered PCShader objects now.
            try:
                eng = _pc._get_engine()
                try:
                    print('SKETCH: engine=', eng)
                except Exception:
                    pass
                pres = getattr(eng, '_presenter', None)
                try:
                    print('SKETCH: presenter=', pres)
                except Exception:
                    pass
                if pres is not None:
                    try:
                        # Try to compile the shader directly using the presenter
                        # helpers so compilation happens even after initial
                        # presenter setup. Prefer GLSL 150 variant.
                        try:
                            from pyglet import gl as _gl
                            frag_src = getattr(s, 'frag_source', '') or ''
                            # sanitize: avoid duplicating a #version line
                            if '#version' not in frag_src:
                                frag_src = '#version 150\n' + frag_src
                            vert_src = getattr(s, 'vert_source', None) or None
                            if vert_src is not None and '#version' not in vert_src:
                                vert_src = '#version 150\n' + vert_src

                            fsh = pres._compile_shader(frag_src, _gl.GL_FRAGMENT_SHADER)
                            vsh = pres._compile_shader(vert_src or '', _gl.GL_VERTEX_SHADER)
                            prog = pres._link_program(vsh, fsh)
                            try:
                                s._program = int(prog)
                                try:
                                    s._compiled_variant = '150'
                                except Exception:
                                    pass
                                try:
                                    print('SKETCH: compiled shader prog=', s._program)
                                except Exception:
                                    pass
                            except Exception:
                                pass
                        except Exception:
                            # fallback: let pres.ensure_resources try
                            try:
                                pres.ensure_resources()
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass
        # create a simple white Pillow image so we can record an image op
        try:
            from PIL import Image as _Image
            self._pil = _Image.new('RGBA', (int(self.width), int(self.height)), (255, 255, 255, 255))
        except Exception:
            self._pil = None

    def draw(self):
        # Compile the shader once after presenter exists (first draw).
        if not getattr(self, '_shader_compiled', False):
            try:
                eng = _pc._get_engine()
                pres = getattr(eng, '_presenter', None)
                if pres is not None:
                    from pyglet import gl as _gl
                    from pycreative.graphics import _REGISTERED_SHADERS
                    shaders = []
                    try:
                        shaders = list(_REGISTERED_SHADERS)
                    except Exception:
                        shaders = []
                    if shaders:
                        s = shaders[-1]
                        try:
                            frag_src = getattr(s, 'frag_source', '') or ''
                            if '#version' not in frag_src:
                                frag_src = '#version 150\n' + frag_src
                            vert_src = getattr(s, 'vert_source', '') or ''
                            if vert_src and '#version' not in vert_src:
                                vert_src = '#version 150\n' + vert_src
                            fsh = pres._compile_shader(frag_src, _gl.GL_FRAGMENT_SHADER)
                            vsh = pres._compile_shader(vert_src or '', _gl.GL_VERTEX_SHADER)
                            prog = pres._link_program(vsh, fsh)
                            s._program = int(prog)
                            try:
                                s._compiled_variant = '150'
                            except Exception:
                                pass
                            try:
                                print('DRAW: compiled shader prog=', s._program)
                            except Exception:
                                pass
                        except Exception:
                            pass
            except Exception:
                pass
            finally:
                try:
                    self._shader_compiled = True
                except Exception:
                    pass
        try:
            self.no_stroke()
        except Exception:
            pass
        # Instead of drawing a rect, draw an image so the presenter can
        # intercept the 'image' op and draw through the shader path.
        try:
            if getattr(self, '_pil', None) is not None:
                try:
                    self.image(self._pil, 0, 0, self.width, self.height)
                except Exception:
                    pass
            else:
                try:
                    self.fill(255, 255, 255)
                    self.rect(0, 0, self.width, self.height)
                except Exception:
                    try:
                        self.fill(1.0, 1.0, 1.0)
                        self.rect(0, 0, self.width, self.height)
                    except Exception:
                        pass
        except Exception:
            pass
