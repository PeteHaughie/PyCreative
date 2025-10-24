

blend()

Class

PCImage

Description

Blends a region of pixels into the image specified by the img parameter. These copies utilize full alpha channel support and a choice of the following modes to blend the colors of source pixels (A) with the ones of pixels in the destination image (B):

BLEND - linear interpolation of colours: C = A*factor + B

ADD - additive blending with white clip: C = min(A*factor + B, 255)

SUBTRACT - subtractive blending with black clip: C = max(B - A*factor, 0)

DARKEST - only the darkest colour succeeds: C = min(A*factor, B)

LIGHTEST - only the lightest colour succeeds: C = max(A*factor, B)

DIFFERENCE - subtract colors from underlying image.

EXCLUSION - similar to DIFFERENCE, but less extreme.

MULTIPLY - Multiply the colors, result will always be darker.

SCREEN - Opposite multiply, uses inverse values of the colors.

OVERLAY - A mix of MULTIPLY and SCREEN. Multiplies dark values, and screens light values.

HARD_LIGHT - SCREEN when greater than 50% gray, MULTIPLY when lower.

SOFT_LIGHT - Mix of DARKEST and LIGHTEST. Works like OVERLAY, but not as harsh.

DODGE - Lightens light tones and increases contrast, ignores darks. Called "Color Dodge" in Illustrator and Photoshop.

BURN - Darker areas are applied, increasing contrast, ignores lights. Called "Color Burn" in Illustrator and Photoshop.

All modes use the alpha information (the highest byte) of source image pixels as the blending factor. If the source and destination regions are different sizes, the image will be automatically resized to match the destination size. If the srcImg parameter is not used, the display window is used as the source image.

As of release 0149, this function ignores image_mode().

Examples

size(400,400);

PCImage mountain = loadImage("mt-fuji.jpg");
PCImage dandelions = loadImage("dandelions.jpg"); 
mountain.blend(dandelions, 0, 0, 132, 400, 268, 0, 132, 400, ADD);

image(mountain, 0, 0);
image(dandelions, 0, 0);

size(400,400);

PCImage mountain = loadImage("mt-fuji.jpg");
PCImage dandelions = loadImage("dandelions.jpg"); 
mountain.blend(dandelions, 0, 0, 132, 400, 268, 0, 132, 400, SUBTRACT);

image(mountain, 0, 0);
image(dandelions, 0, 0);

size(400,400);

PCImage mountain = loadImage("mt-fuji.jpg");
PCImage dandelions = loadImage("dandelions.jpg"); 
mountain.blend(dandelions, 0, 0, 132, 400, 268, 0, 132, 400, DARKEST);

image(mountain, 0, 0);
image(dandelions, 0, 0);

size(400,400);

PCImage mountain = loadImage("mt-fuji.jpg");
PCImage dandelions = loadImage("dandelions.jpg"); 
mountain.blend(dandelions, 0, 0, 132, 400, 268, 0, 132, 400, LIGHTEST);

image(mountain, 0, 0);
image(dandelions, 0, 0);

Syntax

pcimg.blend(sx, sy, sw, sh, dx, dy, dw, dh, mode)	
pcimg.blend(src, sx, sy, sw, sh, dx, dy, dw, dh, mode)	

Parameters

pcimg	(PCImage)	any object of type PCImage
src	(PCImage)	an image variable referring to the source image
sx	(int)	X coordinate of the source's upper left corner
sy	(int)	Y coordinate of the source's upper left corner
sw	(int)	source image width
sh	(int)	source image height
dx	(int)	X coordinate of the destination's upper left corner
dy	(int)	Y coordinate of the destination's upper left corner
dw	(int)	destination image width
dh	(int)	destination image height
mode	(int)	Either BLEND, ADD, SUBTRACT, LIGHTEST, DARKEST, DIFFERENCE, EXCLUSION, MULTIPLY, SCREEN, OVERLAY, HARD_LIGHT, SOFT_LIGHT, DODGE, BURN

Return

void	

Related

alpha()	
PCImage::copy()	
PCImage::blend_color()	