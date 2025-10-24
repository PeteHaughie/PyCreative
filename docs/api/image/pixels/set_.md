

set()

Description

Changes the color of any pixel or writes an image directly into the display window.

The x and y parameters specify the pixel to change and the color parameter specifies the color value. The color parameter is affected by the current color mode (the default is RGB values from 0 to 255). When setting an image, the x and y parameters define the coordinates for the upper-left corner of the image, regardless of the current image_mode().

Setting the color of a single pixel with set(x, y) is easy, but not as fast as putting the data directly into pixels[]. The equivalent statement to set(x, y, #000000) using pixels[] is pixels[y*width+x] = #000000. See the reference for pixels[] for more information.

Examples

size(400,400);
color black = color(0);
set(120, 80, black);
set(340, 80, black);
set(340, 300, black);
set(120, 300, black);

size(400,400);

for (int i = 120; i < width-60; i++) {
  for (int j = 80; j < height-100; j++) {
    color c = color(j, i, 0);    
    set(i, j, c);
  }
}

size(400,400);
PCImage myImage = loadImage("flower.jpg");
set(0, 0, myImage);
line(0, 0, width, height);
line(0, height, width, 0);

Syntax

set(x, y, c)	
set(x, y, img)	

Parameters

x	(int)	x-coordinate of the pixel
y	(int)	y-coordinate of the pixel
c	(int)	any value of the color datatype
img	(PCImage)	image to copy into the original image

Return

void	

Related

get()	
pixels	
copy()	