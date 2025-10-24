

load_pixels()
Class
PCImage
Description
Loads the pixel data of the current display window into the pixels[] array. This function must always be called before reading from or writing to pixels[]. Subsequent changes to the display window will not be reflected in pixels until load_pixels() is called again.

Examples
 Copy
PCImage myImage;
int halfImage;

void setup() {
  size(400, 400);
  halfImage = width * height/2;
  myImage = loadImage("wood.jpg");
  myImage.load_pixels();
  for (int i = 0; i < halfImage; i++) {
    myImage.pixels[i+halfImage] = myImage.pixels[i];
  }
  myImage.update_pixels();
}

void draw() {
  image(myImage, 0, 0);
}

Image output for example 1
Syntax
pcimg.load_pixels()	
Parameters
pcimg	(PCImage)	any object of type PCImage
Return
void	