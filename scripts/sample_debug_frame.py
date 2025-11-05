from PIL import Image
import sys

path = '/tmp/pycreative_debug_frame.png'
try:
    img = Image.open(path).convert('RGBA')
except Exception as e:
    print('ERROR: could not open', path, e)
    sys.exit(2)

w,h = img.size
print('image_size=', (w,h))

# logical canvas assumed 200x200
logical_w, logical_h = 200,200
scale_x = w / logical_w
scale_y = h / logical_h
print('scale_x, scale_y =', scale_x, scale_y)

coords_logical = [(1,1),(99,99),(100,100),(199,199)]
print('\nSampling (logical coords -> mapped pixel coords -> RGBA)')
for lx,ly in coords_logical:
    px = int(round(lx * scale_x))
    py = int(round(ly * scale_y))
    # clamp
    px = min(max(px,0), w-1)
    py = min(max(py,0), h-1)
    print(f'logical ({lx},{ly}) -> pixel ({px},{py}) =', img.getpixel((px,py)))

print('\nSampling raw pixel coords (1,1),(99,99),(100,100),(199,199)')
coords_raw = [(1,1),(99,99),(100,100),(199,199)]
for px,py in coords_raw:
    if px < w and py < h:
        print(f'raw ({px},{py}) =', img.getpixel((px,py)))
    else:
        print(f'raw ({px},{py}) out of bounds for image size {w}x{h}')

print('\nSampling backing-quadrant centers and center-boundary')
backing_checks = [
    (100,100),  # upper-left quadrant center (backing space)
    (300,100),  # upper-right
    (100,300),  # lower-left
    (300,300),  # lower-right
    (199,199),  # just before center
    (200,200),  # center
    (201,201),  # just after center
]
for px,py in backing_checks:
    if 0 <= px < w and 0 <= py < h:
        print(f'backing ({px},{py}) =', img.getpixel((px,py)))
    else:
        print(f'backing ({px},{py}) out of bounds')
