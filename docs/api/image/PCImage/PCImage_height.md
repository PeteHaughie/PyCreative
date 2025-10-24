

height

Description

The height of the image in units of pixels.

Examples
PCImage photo;

void setup() {
  size(400, 400);
  photo = loadImage("mt-horai.jpg");
}

void draw() {
  image(photo, 0, 0);
}

Syntax

pcimg.height	

Parameters

pcimg	