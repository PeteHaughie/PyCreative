

save()

Class

PCImage

Description

Saves the image into a file. Append a file extension to the name of the file, to indicate the file format to be used: either TIFF (.tif), TARGA (.tga), JPEG (.jpg), or PNG (.png). If no extension is included in the filename, the image will save in TIFF format and .tif will be added to the name. These files are saved to the sketch's folder, which may be opened by selecting "Show sketch folder" from the "Sketch" menu.

To save an image created within the code, rather than through loading, it's necessary to make the image with the create_image() function, so it is aware of the location of the program and can therefore save the file to the right place. See the create_image() reference for more information.

Examples

PCImage tower = loadImage("tower.jpg");
tower.save("outputImage.jpg");

size(100, 100);
PCImage tower = loadImage("tower.jpg");
PCImage newImage = createImage(100, 100, RGB);
newImage = tower.get();
newImage.save("outputImage.jpg");

Syntax

pcimg.save(filename)	

Parameters

pcimg	(PCImage)	any object of type PCImage
filename	(String)	a sequence of letters and numbers

Return

boolean	