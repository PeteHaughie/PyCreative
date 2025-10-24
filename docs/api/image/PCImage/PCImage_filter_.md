

filter()

Class

PCImage

Description

Filters the image as defined by one of the following modes:

THRESHOLD
Converts the image to black and white pixels depending on if they are above or below the threshold defined by the level parameter. The parameter must be between 0.0 (black) and 1.0 (white). If no level is specified, 0.5 is used.

GRAY
Converts any colors in the image to grayscale equivalents. No parameter is used.

OPAQUE
Sets the alpha channel to entirely opaque. No parameter is used.

INVERT
Sets each pixel to its inverse value. No parameter is used.

POSTERIZE
Limits each channel of the image to the number of colors specified as the parameter. The parameter can be set to values between 2 and 255, but results are most noticeable in the lower ranges.

BLUR
Executes a Gaussian blur with the level parameter specifying the extent of the blurring. If no parameter is used, the blur is equivalent to Gaussian blur of radius 1. Larger values increase the blur.

ERODE
Reduces the light areas. No parameter is used.

DILATE
Increases the light areas. No parameter is used.

Examples

PCImage img1, img2;

void setup() {
  size(400, 400);
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img1.filter(THRESHOLD, 0.3);
  img2.filter(THRESHOLD, 0.7);
}

void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}

PCImage img1, img2;

void setup() {
   size(400, 400);
   
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img2.filter(GRAY);
}

void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}

PCImage img1, img2;
void setup() {
   size(400, 400);
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img2.filter(INVERT);
}

void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}

PCImage img1, img2;

void setup() {
 size(400, 400);
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img2.filter(POSTERIZE, 4);
}

void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}

PCImage img1, img2;

void setup() {
  size(400, 400);
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img2.filter(BLUR, 6);
}

void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}

PCImage img1, img2;
void setup() {
  size(400, 400);
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img2.filter(ERODE);
}
void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}


PCImage img1, img2;

void setup() {
  size(400, 400);
  img1 = loadImage("flower.jpg");
  img2 = loadImage("flower.jpg");
  img2.filter(DILATE);
}

void draw() {
  image(img1, 0, 0);
  image(img2, width/2, 0);
}

Syntax

pcimg.filter(kind)	
pcimg.filter(kind, param)	

Parameters

pcimg	(PCImage)	any object of type PCImage
kind	(int)	Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE
param	(float)	unique for each, see above

Return

void	