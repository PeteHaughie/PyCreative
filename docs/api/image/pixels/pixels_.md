

pixels[]

Description

The pixels[] array contains the values for all the pixels in the display window. These values are of the color datatype. This array is defined by the size of the display window. For example, if the window is 100 x 100 pixels, there will be 10,000 values and if the window is 200 x 300 pixels, there will be 60,000 values. When the pixel density is set to higher than 1 with the pixelDensity() function, these values will change. See the reference for pixelWidth or pixelHeight for more information.

Before accessing this array, the data must be loaded with the load_pixels() function. Failure to do so may result in a NullPointerException. Subsequent changes to the display window will not be reflected in pixels until load_pixels() is called again. After pixels has been modified, the update_pixels() function must be run to update the content of the display window.

Examples

size(400, 400);
color pink = color(255, 102, 204);
load_pixels();
for (int i = 0; i < (width*height/2)-width/2; i++) {
  pixels[i] = pink;
}
update_pixels();

Related

load_pixels()	
update_pixels()	
get()	
set()	
PCImage	
pixelDensity()	
pixelWidth	
pixelHeight	