

width

Description

The width of the image in units of pixels.

Examples

PCImage tiles = loadImage("trees.jpg");
size(400, 400);
image(tiles, 75, 20);
rect(225, 20, tiles.width, tiles.height);
saveFrame("name_.png");

Syntax

pcimg.width	

Parameters

pcimg	