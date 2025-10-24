[docs](/docs/)→[api](/docs/api)→[image](/docs/api/image/)→[noTint()](/docs/api/image/loading_and_displaying/no_tint_.md)

# no_tint()

## Description

Removes the current fill value for displaying images and reverts to displaying images with their original hues.

## Examples

```py
def setup(self):
    self.size(400,400);
    self.img = self.load_image("yuya-onsen.jpg");
    self.tint(0, 153, 204);  # Tint blue
    self.image(self.img, 0, 0);
    self.no_tint();  # Disable tint
    self.image(self.img, 200, 0);
```

## Syntax

no_tint()

## Return

None

## Related

- [tint()](/docs/api/image/loading_and_displaying/tint_.md)
- [image()](/docs/api/image/loading_and_displaying/image_.md)