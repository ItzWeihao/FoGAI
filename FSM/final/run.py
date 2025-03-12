import pygame

from constants import FLEE, SCREEN_SIZE, BLACK, SEEK, WANDER
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
        self.ghost = Ghost(self.nodes.getStartTempNodeGhost(), self.pacman)
        self.ghost.setTarget(self.pacman)  # type: ignore
        self.ghost.setNodes(self.nodes)
        self.pacman.setTarget(self.ghost)  # type: ignore
        self.pacman.setNodes(self.nodes)

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
                    self.ghost.myState = SEEK
                    self.ghost.FSMstateChecker()
                if event.key == pygame.K_f:
                    self.ghost.myState = FLEE
                    self.ghost.FSMstateChecker()
                if event.key == pygame.K_w:
                    self.ghost.myState = WANDER
                    self.ghost.FSMstateChecker()

                if event.key == pygame.K_q:
                    self.pacman.myState = SEEK
                    self.pacman.FSMstateChecker()
                if event.key == pygame.K_a:
                    self.pacman.myState = FLEE
                    self.pacman.FSMstateChecker()
                if event.key == pygame.K_z:
                    self.pacman.myState = WANDER
                    self.pacman.FSMstateChecker()

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
