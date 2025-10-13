[docs](/docs/)→[api](/docs/api)→[environment](/docs/api/environment/)

# window_ratio()

## Description

Scale the sketch as if it fit this specific width and height. This will also scale the `mouse_x` and `mouse_y` variables (as well as `pmouse_x` and `pmouse_y`). Note that it will not have an effect on `mouse_event` objects (i.e. `event.get_x()` and `event.get_y()`) because their exact behavior may interact strangely with other libraries.

## Syntax

window_ratio(wide, high)

## Parameters

| Input | Description |
|-------|-------------|
| wide (int) | The target width to scale the sketch to |
| high (int) | The target height to scale the sketch to |

## Return

pass