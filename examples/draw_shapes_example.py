"""
Example usage of ShapeDrawer to draw basic shapes with Pygame.
"""
import pygame
import sys
sys.path.append('src')
from shapes import ShapeDrawer

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("ShapeDrawer Example")
    clock = pygame.time.Clock()
    drawer = ShapeDrawer(screen)

    running = True
    while running:    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False


            screen.fill((30, 30, 30))
            # Draw a filled rectangle
            drawer.draw_rectangle((50, 50, 200, 100), (255, 0, 0))
            # Draw a circle outline
            drawer.draw_circle((320, 240), 60, (0, 255, 0), width=3)
            # Draw a filled circle
            drawer.draw_circle((500, 100), 40, (0, 0, 255))
            # Draw a line
            drawer.draw_line((100, 400), (540, 400), (255, 255, 0), width=5)

            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
