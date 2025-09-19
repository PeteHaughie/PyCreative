"""
Example usage of pycreative.graphics.Surface drawing helpers.
"""
import pygame
from pycreative import Surface

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    surf = Surface(screen)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 30))
        surf.rect(50, 50, 200, 100, color=(255, 0, 0))
        surf.ellipse(320, 240, 120, 80, color=(0, 255, 0))
        surf.line((100, 400), (540, 400), color=(255, 255, 0), width=5)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
