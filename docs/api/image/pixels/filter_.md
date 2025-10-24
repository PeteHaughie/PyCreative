

filter()

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
 Copy
PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(THRESHOLD);

PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(GRAY);

PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(INVERT);

PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(POSTERIZE, 4);

PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(BLUR, 6);

PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(ERODE);

PCImage img;
img = loadImage("flower.jpg");
image(img, 0, 0);
filter(DILATE);

PShader blur;
PCImage img;

void setup() {
  size(400, 400, P2D);
  blur = loadShader("blur.glsl");
  img = loadImage("flower.jpg");
  image(img, 0, 0); 
}

void draw() {
  filter(blur); // Blurs more each time through draw()
}

Syntax

filter(shader)	
filter(kind)	
filter(kind, param)	

Parameters

shader	(PShader)	the fragment shader to apply
kind	(int)	Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE
param	(float)	unique for each, see above

Return

void	