

copy()

Description

Copies a region of pixels from one image into another. If the source and destination regions aren't the same size, it will automatically resize source pixels to fit the specified target region. No alpha information is used in the process, however if the source image has an alpha channel set, it will be copied as well.

As of release 0149, this function ignores image_mode().

Examples

size(400,400);
PCImage img = loadImage("hometown.jpg");
image(img, 0, 0, width, height);
copy(56, 176, 80, 80, 280, 200, 400, 400);
stroke(255);
noFill();
// Rectangle shows area being copied
rect(56, 176, 80, 80);

Syntax

copy()	
copy(sx, sy, sw, sh, dx, dy, dw, dh)	
copy(src, sx, sy, sw, sh, dx, dy, dw, dh)	

Parameters

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

alpha()	
blend()	