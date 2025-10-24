

copy()

Class

PCImage

Description

Copies a region of pixels from one image into another. If the source and destination regions aren't the same size, it will automatically resize source pixels to fit the specified target region. No alpha information is used in the process, however if the source image has an alpha channel set, it will be copied as well.

As of release 0149, this function ignores image_mode().

Examples

PCImage flowers;

void setup() {
  size(400, 400);
  flowers = loadImage("flowers.jpg");
  int x = width/2;
  flowers.copy(x, 0, x, height, 0, 0, x, height);
}

void draw() {
  image(flowers, 0, 0);
}

Syntax

pcimg.copy()	
pcimg.copy(sx, sy, sw, sh, dx, dy, dw, dh)	
pcimg.copy(src, sx, sy, sw, sh, dx, dy, dw, dh)	

Parameters

pcimg	(PCImage)	any object of type PCImage
sx	(int)	X coordinate of the source's upper left corner
sy	(int)	Y coordinate of the source's upper left corner
sw	(int)	source image width
sh	(int)	source image height
dx	(int)	X coordinate of the destination's upper left corner
dy	(int)	Y coordinate of the destination's upper left corner
dw	(int)	destination image width
dh	(int)	destination image height
src	(PCImage)	an image variable referring to the source image.

Return

void or PCImage	

Related

PGraphics::alpha()	
PCImage::blend()	