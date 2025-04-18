from vector import Vector2
from constants import PACMAN, YELLOW, TILE_WIDTH
from entity import Entity


class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.goal = Vector2()
        self.directionMethod = self.goalDirection

    def setGhost(self, ghost):
        self.ghost = ghost

    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = (
                self.node.position + self.directions[direction] * TILE_WIDTH - self.goal
            )
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]

    def update(self, dt):
        self.goal = self.ghost.position
        self.position += self.directions[self.direction] * self.speed * dt

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()
