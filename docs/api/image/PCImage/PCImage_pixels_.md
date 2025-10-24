

pixels[]

Description

The pixels[] array contains the values for all the pixels in the image. These values are of the color datatype. This array is the size of the image, meaning if the image is 100 x 100 pixels, there will be 10,000 values and if the window is 200 x 300 pixels, there will be 60,000 values.

Before accessing this array, the data must be loaded with the load_pixels() method. Failure to do so may result in a NullPointerException. After the array data has been modified, the update_pixels() method must be run to update the content of the display window.

Examples

PCImage tower;

void setup() {
  size(400, 400);
  tower = loadImage("tower.jpg");
  int dimension = tower.width * tower.height;
  tower.load_pixels();
  for (int i = 0; i < dimension; i += 4) { 
    tower.pixels[i] = color(0, 0, 0); 
  } 
  tower.update_pixels();
}

void draw() {
  image(tower, 0, 0);
}

Syntax

pcimg.pixels[]	
Parameters
pcimg	