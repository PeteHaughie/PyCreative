

update_pixels()

Class

PCImage

Description

Updates the display window with the data in the pixels[] array. Use in conjunction with load_pixels(). If you're only reading pixels from the array, there's no need to call update_pixels() — updating is only necessary to apply changes.

Examples

PCImage myImage;
int halfImage;

void setup() {
  size(400, 400);
  halfImage = width * height/2;
  myImage = loadImage("shells.jpg");
  myImage.load_pixels();
  for (int i = 0; i < halfImage; i++) {
    myImage.pixels[i+halfImage] = myImage.pixels[i];
  }
  myImage.update_pixels();
}

void draw() {
  image(myImage, 0, 0);
}

Syntax

pcimg.update_pixels()	
pcimg.updatePixels(x, y, w, h)	

Parameters

pcimg	(PCImage)	any object of type PCImage
x	(int)	x-coordinate of the upper-left corner
y	(int)	y-coordinate of the upper-left corner
w	(int)	width
h	(int)	height

Return

void	