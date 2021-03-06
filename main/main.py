import os

import pygame

from routes.menu import Menu


def main():
    pygame.init()
    win_size = (1000, 700)
    win = pygame.display.set_mode(win_size)

    if not os.path.exists("boards/builder_boards"):
        os.mkdir("boards/builder_boards")

    route = Menu(win_size)

    clock = pygame.time.Clock()
    while True:
        clock.tick(120)

        route.draw(win)

        route = route.update_state()

        pygame.display.update()
