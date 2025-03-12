import pygame

from constants import SCREEN_SIZE, BLACK
from pacman import Pacman
from nodes import NodeGroup
from ghosts import Ghost


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
        self.clock = pygame.time.Clock()
        self.background = pygame.surface.Surface(SCREEN_SIZE).convert()
        self.background.fill(BLACK)
        self.nodes = NodeGroup("maze1.txt")
        self.pacman = Pacman(self.nodes.getStartTempNodePacMan())
        self.ghost = Ghost(self.nodes.getStartTempNodeGhost(), self.nodes, self.pacman)
        self.pacman.setGhost(self.ghost)

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.pacman.update(dt)
        self.ghost.update(dt)
        self.checkEvents()
        self.render()

    # EXERCISE 4
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    # implement and delete the "continue" command
                    continue
                if event.key == pygame.K_f:
                    # implement and delete the "continue" command
                    continue
                if event.key == pygame.K_w:
                    # implement and delete the "continue" command
                    continue

    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen)
        self.pacman.render(self.screen)
        self.ghost.render(self.screen)
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    while True:
        game.update()
