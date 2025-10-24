

resize()

Class

PCImage

Description

Resize the image to a new width and height. To make the image scale proportionally, use 0 as the value for the wide or high parameter. For instance, to make the width of an image 150 pixels, and change the height using the same proportion, use resize(150, 0).

Even though a PGraphics is technically a PCImage, it is not possible to rescale the image data found in a PGraphics. (It's simply not possible to do this consistently across renderers: technically infeasible with P3D, or what would it even do with PDF?) If you want to resize PGraphics content, first get a copy of its image data using the get() method, and call resize() on the PCImage that is returned.

Examples

PCImage flower = loadImage("flower.jpg");
size(400,400);
image(flower, 0, 0);
flower.resize(400, 200);
image(flower, 0, 0);

PCImage flower = loadImage("flower.jpg");
size(400,400);
image(flower, 0, 0);
flower.resize(0, 200);
image(flower, 0, 0);

Syntax

pcimg.resize(w, h)	

Parameters

pcimg	(PCImage)	any object of type PCImage
w	(int)	the resized image width
h	(int)	the resized image height

Return

void	

Related

PCImage::get()	