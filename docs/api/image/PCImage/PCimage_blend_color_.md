

blend_color()

Class

PCImage

Description

Blends two color values together based on the blending mode given as the MODE parameter. The possible modes are described in the reference for the blend() function.

Syntax

pcimg.blendColor(c1, c2, mode)	

Parameters

pcimg	(PCImage)	any object of type PCImage
c1	(int)	the first color to blend
c2	(int)	the second color to blend
mode	(int)	either BLEND, ADD, SUBTRACT, DARKEST, LIGHTEST, DIFFERENCE, EXCLUSION, MULTIPLY, SCREEN, OVERLAY, HARD_LIGHT, SOFT_LIGHT, DODGE, or BURN

Return

int	

Related

PCImage::blend()	
color()	