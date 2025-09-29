# PyCreative Documentation

## Getting Started

PyCreative is a creative coding framework for Python 3.11+ built atop PyGame. It is designed for rapid prototyping of visual, audio, and interactive projects.

### Installation

1. **Create a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```sh
   pip install -e .
   # Or, for development:
   pip install -e '.[test]'
   ```
   PyGame is required and will be installed automatically.

### Running Examples

To run a sketch:
```sh
python examples/hello_sketch.py
```
Or using the CLI:
```sh
pycreative examples/hello_sketch.py
```

### Project Structure
- `src/pycreative/`: Framework source code
- `examples/`: Example sketches
- `sketches/`: User sketches
- `tests/`: Test suite

### Key Modules
- `pycreative.app`: Main loop, lifecycle hooks

### Testing
Run all tests with:
```sh
pytest tests/
```

### Conventions
- Use Python 3.11+
- Always use a `venv` virtual environment
- Type hints and docstrings required for public APIs
- PEP8, Ruff

---
For more details, see the example sketches and module READMEs.

## Guides

- Offscreen surfaces and caching: `offscreen.md`
- Shape construction (begin/vertex/end): `shapes.md`
- Pixel object: `pixels.md`
- Pixels Image object: `pixels_image.md`

## Contributing

Code contributions, pull requests, and suggestions are welcome!

- Please open an issue for bugs, feature requests, or questions.
- Submit pull requests with clear descriptions and relevant tests/examples.
- All contributions should follow the project's style and documentation conventions.

We value community feedback and collaboration to improve PyCreative.

## Minimal Example Sketch

Below is a minimal sketch that follows best practices and the format expected by `app.py`:

```python
from pycreative import Sketch

class MySketch(Sketch):
   def setup(self):
      self.size(800, 600)
      self.bg = 0

   def update(self, dt):
      pass  # Update state here

   def draw(self):
      self.clear(self.bg)
      self.ellipse(self.width/2, self.height/2, 200, 200)

if __name__ == '__main__':
   MySketch().run()
```

**Best practices:**
- Inherit from `Sketch` and implement `setup`, `update`, and `draw` methods.
- Use `self.size()` to set window size.
- Use `self.clear()` to set background color.
- Place the run logic under `if __name__ == '__main__':`.
