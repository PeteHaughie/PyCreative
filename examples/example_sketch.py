"""
Example sketch for PyGameSynth
"""

def run():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Example Sketch")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        screen.fill((50, 50, 50))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    run()
