class Ball:
    def __init__(self, x, y, radius, color, velocity):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity = velocity

    def update(self, width, height):
        # Update ball position
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Bounce off walls
        if self.x <= self.radius or self.x >= width - self.radius:
            self.velocity[0] *= -1
        if self.y <= self.radius or self.y >= height - self.radius:
            self.velocity[1] *= -1

    def draw(self, sketch):
        sketch.fill(self.color)
        sketch.ellipse(self.x, self.y, self.radius * 2, self.radius * 2)