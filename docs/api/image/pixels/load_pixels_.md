

load_pixels()

Description

Loads the pixel data of the current display window into the pixels[] array. This function must always be called before reading from or writing to pixels[]. Subsequent changes to the display window will not be reflected in pixels until load_pixels() is called again.

Examples

size(400,400);
int halfImage = width*height/2;
PCImage myImage = loadImage("mt-fuji.jpg");
image(myImage, 0, 0);

load_pixels();
for (int i = 0; i < halfImage; i++) {
  pixels[i+halfImage] = pixels[i];
}
update_pixels();

Syntax

load_pixels()	

Return

void	

Related

pixels	
update_pixels()	