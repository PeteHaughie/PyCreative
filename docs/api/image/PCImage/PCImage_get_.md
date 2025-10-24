


get()

Class

PCImage

Description

Reads the color of any pixel or grabs a section of an image. If no parameters are specified, the entire image is returned. Use the x and y parameters to get the value of one pixel. Get a section of the display window by specifying an additional width and height parameter. When getting an image, the x and y parameters define the coordinates for the upper-left corner of the image, regardless of the current image_mode().

If the pixel requested is outside the image window, black is returned. The numbers returned are scaled according to the current color ranges, but only RGB values are returned by this function. For example, even though you may have drawn a shape with colorMode(HSB), the numbers returned will be in RGB format.

Getting the color of a single pixel with get(x, y) is easy, but not as fast as grabbing the data directly from pixels[]. The equivalent statement to get(x, y) using pixels[] is pixels[y*width+x]. See the reference for pixels[] for more information.

Examples

PCImage sky = loadImage("tokyo-sky.jpg");;
size(400, 400);
background(sky);
noStroke();
color c = sky.get(240, 360);
fill(c);
rect(100, 100, 200, 200);

PCImage sky = loadImage("tokyo-sky.jpg");
size(400, 400);
background(sky);
PCImage newSky = sky.get(200, 0, 200, 400); 
image(newSky, 0, 0); 

Syntax

pcimg.get(x, y)	
pcimg.get(x, y, w, h)	
pcimg.get()	

Parameters

pcimg	(PCImage)	any object of type PCImage
x	(int)	x-coordinate of the pixel
y	(int)	y-coordinate of the pixel
w	(int)	width of pixel rectangle to get
h	(int)	height of pixel rectangle to get

Return

int or PCImage	

Related

PCImage::set()	
PCImage::pixels	
PCImage::copy()	