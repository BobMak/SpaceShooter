# add previous directory to path
import pygame

from Ships.ShipGen import Generator
# import State
# from Core.Assets import ship_2

if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((350, 350))

    generator = Generator()
    # res = generator.generate()
    ship = generator.generateShipSurf()
    for _ in range(10):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display.blit(ship, (0, 0))
        # display.blit(ship_2, (0, 0))
        # ship.draw_rotating()
        pygame.display.update()
        pygame.display.flip()
        pygame.time.delay(100)
    pygame.quit()