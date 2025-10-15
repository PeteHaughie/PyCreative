#!/usr/bin/env python3
"""Inspect installed skia-python for GL interop symbols.

Run this with the project venv to see which constructors/functions exist.
"""
import sys
import inspect

try:
    import skia
except Exception as e:
    print('IMPORT_ERROR', e)
    sys.exit(1)

def safe_hasattr(obj, name):
    try:
        return hasattr(obj, name)
    except Exception as e:
        return f'error: {e}'

print('skia module:', getattr(skia, '__file__', repr(skia)))
names = ['GrDirectContext', 'GrBackendTexture', 'GrGLTextureInfo', 'GrBackendRenderTarget', 'GrGLFramebufferInfo', 'GrBackendTexture', 'GrMipmapped', 'GrMipMapped']
for n in names:
    print(n, 'present?', safe_hasattr(skia, n))

# Check for MakeGL or classmethods
if safe_hasattr(skia, 'GrBackendTexture'):
    try:
        b = skia.GrBackendTexture
        print('GrBackendTexture is type:', type(b))
        # try to inspect methods
        for m in ['MakeGL', 'makeGL', 'MakeFromTexture']:
            print(' GrBackendTexture has', m, '?', safe_hasattr(b, m))
        print(' GrBackendTexture doc:', (b.__doc__ or '')[:200])
    except Exception as e:
        print('GrBackendTexture inspect error:', e)

if safe_hasattr(skia, 'GrGLTextureInfo'):
    try:
        g = skia.GrGLTextureInfo
        print('GrGLTextureInfo is type:', type(g))
        print(' GrGLTextureInfo doc:', (g.__doc__ or '')[:200])
    except Exception as e:
        print('GrGLTextureInfo inspect error:', e)

for enum_name in ('GrMipmapped', 'GrMipMapped'):
    if safe_hasattr(skia, enum_name):
        try:
            enum = getattr(skia, enum_name)
            print(enum_name, 'members:', [m for m in dir(enum) if not m.startswith('_')])
        except Exception as e:
            print(enum_name, 'inspect error:', e)

print('Done')
