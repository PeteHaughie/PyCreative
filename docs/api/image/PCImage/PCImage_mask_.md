

mask()

Class

PCImage

Description

Masks part of an image from displaying by loading another image and using it as an alpha channel. This mask image should only contain grayscale data, but only the blue color channel is used. The mask image needs to be the same size as the image to which it is applied.

In addition to using a mask image, an integer array containing the alpha channel data can be specified directly. This method is useful for creating dynamically generated alpha masks. This array must be of the same length as the target image's pixels array and should contain only grayscale data of values between 0‑255.

Examples

PCImage photo, maskImage;

void setup() {
  size(400, 400);
  photo = loadImage("test.jpg");
  maskImage = loadImage("mask.jpg");
  photo.mask(maskImage);
}

void draw() {
  image(photo, 0, 0);
  image(photo, width/4, 0);
}

Syntax

pcimg.mask(maskArray)	
pcimg.mask(img)	

Parameters

pcimg	(PCImage)	any object of type PCImage
maskArray	(int[])	array of integers used as the alpha channel, needs to be the same length as the image's pixel array.
img	(PCImage)	image to use as the mask

Return

void	