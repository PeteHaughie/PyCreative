

set()

Class

PCImage

Description

Changes the color of any pixel or writes an image directly into the display window.

The x and y parameters specify the pixel to change and the color parameter specifies the color value. The color parameter is affected by the current color mode (the default is RGB values from 0 to 255). When setting an image, the x and y parameters define the coordinates for the upper-left corner of the image, regardless of the current image_mode().

Setting the color of a single pixel with set(x, y) is easy, but not as fast as putting the data directly into pixels[]. The equivalent statement to set(x, y, #000000) using pixels[] is pixels[y*width+x] = #000000. See the reference for pixels[] for more information.

Examples

PCImage tower;

void setup() {
  size(400, 400);
  tower = loadImage("tower.jpg");
  color black = color(0);
  
  tower.set(240, 160, black); 
  tower.set(340, 160, black); 
  tower.set(340, 600, black); 
  tower.set(240, 600, black); 
}

void draw() {
  image(tower, 0, 0);
}

Syntax

pcimg.set(x, y, c)	
pcimg.set(x, y, img)	

Parameters

pcimg	(PCImage)	any object of type PCImage
x	(int)	x-coordinate of the pixel
y	(int)	y-coordinate of the pixel
c	(int)	any value of the color datatype
img	(PCImage)	image to copy into the original image

Return

void	

Related

PCImage::get()	
PCImage::pixels	
PCImage::copy()	