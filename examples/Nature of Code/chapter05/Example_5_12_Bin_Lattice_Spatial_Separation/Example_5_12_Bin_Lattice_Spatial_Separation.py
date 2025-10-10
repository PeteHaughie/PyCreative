"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_12_Bin_Lattice_Spatial_Separation/Example_5_12_Bin_Lattice_Spatial_Separation.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Demonstration of Craig Reynolds' "Flocking" behavior
// See: http://www.red3d.com/cwr/
// Rules: Cohesion, Separation, Alignment

// Click mouse to add boids into the system
"""

from pycreative.app import Sketch
from Flock import Flock
from Boid import Boid


class Example_5_12_Bin_Lattice_Spatial_Separation(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.12: Bin Lattice Spatial Separation")
        self.flock = Flock()

        self.resolution = 40  # adjust as necessary
        self.cols = int(self.width // self.resolution)
        self.rows = int(self.height // self.resolution)
        self.make_3d_array(self.cols, self.rows)

        # Add an initial set of boids into the system
        for _ in range(100):
            boid = Boid(self, int(self.random(self.width)), int(self.random(self.height)))
            self.flock.add_boid(boid)

    def make_3d_array(self, cols: int, rows: int):
        # Create exact rows x cols grid
        self.grid: list[list[list[Boid]]] = [[[] for _ in range(cols)] for _ in range(rows)]
    
    def update(self, dt: float):
        self.set_title(f"Example 5.12: Bin Lattice Spatial Separation (Boids: {len(self.flock.boids)})")

    def draw(self):
        self.clear((255, 255, 255))

        # Reset grid at the beginning of each frame
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j].clear()

        # Place each boid into the appropriate cell in the grid
        for boid in self.flock.boids:
            col = int(boid.position.x // self.resolution)
            row = int(boid.position.y // self.resolution)
            col = max(0, min(col, self.cols - 1))
            row = max(0, min(row, self.rows - 1))
            self.grid[row][col].append(boid)

        # Draw the grid
        self.stroke(200)
        self.stroke_weight(1)

        # Draw vertical lines
        for i in range(self.cols + 1):
            x = i * self.resolution
            self.line(x, 0, x, self.height)

        # Draw horizontal lines
        for j in range(self.rows + 1):
            y = j * self.resolution
            self.line(0, y, self.width, y)

        # Highlight the 3x3 neighborhood the mouse is over
        mouse_col = int((self.mouse_x or 0) // self.resolution)
        mouse_row = int((self.mouse_y or 0) // self.resolution)
        self.no_stroke()
        self.fill(255, 50, 50, 100)  # Semi-transparent red
        for i in range(-1, 2):
            for j in range(-1, 2):
                col = mouse_col + i
                row = mouse_row + j
                # Check if the cell is within the grid
                if 0 <= col < self.cols and 0 <= row < self.rows:
                    self.rect(col * self.resolution, row * self.resolution, self.resolution, self.resolution)
        self.flock.run()

    def mouse_dragged(self):
        self.flock.add_boid(Boid(self, self.mouse_x or 0, self.mouse_y or 0))
