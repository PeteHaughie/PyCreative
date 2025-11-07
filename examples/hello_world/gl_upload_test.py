"""GL upload + readback test sketch

This sketch creates a small Pillow RGBA image filled with red/magenta,
then draws it via `self.image(...)` so the presenter receives an `image`
command with `image_bytes` and our diagnostic helper runs (when the
env var PYCREATIVE_DEBUG_PRESENT_TEST_UPLOAD=1 is set).
"""

import ctypes
from PIL import Image

class Sketch:
    def setup(self):
        self.size(320, 240)
        self.window_title('GL upload test')
        # create a small test image (RGBA)
        self.test_w = 16
        self.test_h = 16
        img = Image.new('RGBA', (self.test_w, self.test_h), (255, 0, 255, 255))
        self._pil = img

    def draw(self):
        # draw the Pillow image to the canvas which will record image_bytes
        try:
            import pycreative as _pc
            eng = _pc._get_engine()
            try:
                raw = self._pil.tobytes()
                eng.graphics.record('test_gl_upload', image_bytes=raw, image_size=(self.test_w, self.test_h), image_mode='RGBA')
                try:
                    print('GL_UPLOAD_TEST: recorded top-level command, total_cmds=', len(getattr(eng, 'graphics').commands))
                    try:
                        print('GL_UPLOAD_TEST last_cmd=', getattr(eng, 'graphics').commands[-1])
                    except Exception:
                        pass
                except Exception:
                    pass
                # Also exercise the presenter's helper directly (if available)
                try:
                    pres = getattr(eng, '_presenter', None)
                    if pres is not None:
                        try:
                            rb = pres._test_texture_upload_and_readback(raw, self.test_w, self.test_h)
                            try:
                                print('GL_UPLOAD_TEST direct readback=', rb)
                            except Exception:
                                pass
                        except Exception as e:
                            try:
                                print('GL_UPLOAD_TEST direct helper error', e)
                            except Exception:
                                pass
                        # Now attempt a minimal custom shader draw (constant color)
                        try:
                            from pyglet import gl as _gl
                            # Simple GLSL 1.20 vertex/fragment pair that uses
                            # the same attribute names bound by the presenter.
                            vs120 = '#version 120\nattribute vec2 a_pos;attribute vec2 a_uv;varying vec2 v_uv;void main(){v_uv=a_uv;gl_Position=vec4(a_pos,0.0,1.0);}'
                            fs120 = '#version 120\nvarying vec2 v_uv;void main(){gl_FragColor=vec4(1.0,0.0,0.5,1.0);}'
                            try:
                                vert = pres._compile_shader(vs120, _gl.GL_VERTEX_SHADER)
                                frag = pres._compile_shader(fs120, _gl.GL_FRAGMENT_SHADER)
                                prog = pres._link_program(vert, frag, bind_attribs=['a_pos', 'a_uv'])
                                try:
                                    # bind program and VAO (if present) and draw
                                    prev = _gl.GLint()
                                    try:
                                        _gl.glGetIntegerv(_gl.GL_CURRENT_PROGRAM, ctypes.byref(prev))
                                    except Exception:
                                        prev = None
                                    _gl.glUseProgram(prog)
                                    try:
                                        if getattr(pres, '_fs_vao', None) is not None:
                                            try:
                                                _gl.glBindVertexArray(int(pres._fs_vao))
                                            except Exception:
                                                pass
                                        else:
                                            try:
                                                _gl.glBindBuffer(_gl.GL_ARRAY_BUFFER, int(pres._fs_vbo))
                                            except Exception:
                                                pass
                                        try:
                                            _gl.glDrawArrays(_gl.GL_TRIANGLES, 0, 6)
                                        except Exception:
                                            pass
                                    finally:
                                        try:
                                            if prev is not None:
                                                _gl.glUseProgram(int(prev))
                                            else:
                                                _gl.glUseProgram(0)
                                        except Exception:
                                            pass
                                    # read back center pixel
                                    try:
                                        w = int(getattr(pres, 'width', 0) or 0)
                                        h = int(getattr(pres, 'height', 0) or 0)
                                        if w and h:
                                            cx = w // 2
                                            cy = h // 2
                                            rb = (_gl.GLubyte * 4)()
                                            try:
                                                _gl.glPixelStorei(_gl.GL_PACK_ALIGNMENT, 1)
                                            except Exception:
                                                pass
                                            try:
                                                _gl.glReadPixels(cx, cy, 1, 1, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, ctypes.byref(rb))
                                                try:
                                                    print('GL_UPLOAD_TEST shader draw readback=', int(rb[0]), int(rb[1]), int(rb[2]), int(rb[3]))
                                                except Exception:
                                                    pass
                                            finally:
                                                try:
                                                    _gl.glPixelStorei(_gl.GL_PACK_ALIGNMENT, 4)
                                                except Exception:
                                                    pass
                                except Exception:
                                    pass
                            except Exception:
                                pass
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception:
                # fallback to normal image recording
                try:
                    self.image(self._pil, 0, 0, self.width, self.height)
                except Exception:
                    pass
        except Exception:
            try:
                self.image(self._pil, 0, 0, self.width, self.height)
            except Exception:
                pass

