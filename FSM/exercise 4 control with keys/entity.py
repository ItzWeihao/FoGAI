from typing import Self
import pygame
from algorithms import aStar
from nodes import Node, NodeGroup
from vector import Vector2
from constants import (
    ELSE,
    FLEE,
    SEEK,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    STOP,
    WANDER,
    WHITE,
    TILE_WIDTH,
)
from random import choice, randint


class Entity(object):
    def __init__(self, node: Node):
        self.name = None
        self.directions = {
            UP: Vector2(0, -1),
            DOWN: Vector2(0, 1),
            LEFT: Vector2(-1, 0),
            RIGHT: Vector2(1, 0),
            STOP: Vector2(),
        }
        self.direction = STOP
        self.setSpeed(100)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.node = node
        self.setPosition()
        self.target = node
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.wanderBiased

        self.states = [SEEK, FLEE, WANDER, ELSE]
        self.myState = SEEK

    def setTarget(self, target: Self):
        self.djstraTarget = target

    def setNodes(self, nodes: NodeGroup):
        self.nodes = nodes

    def setPosition(self):
        self.position = self.node.position.copy()

    def validDirection(self, direction: int):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False

    def getNewTarget(self, direction: int):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction: int):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def fleeGoal(self, directions: list[int]):
        distances = []
        for direction in directions:
            vec = (
                self.goal - self.node.position + self.directions[direction] * TILE_WIDTH
            )
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]

    def seekGoal(self, directions: list[int]):
        distances = []
        for direction in directions:
            vec = (
                self.goal - self.node.position + self.directions[direction] * TILE_WIDTH
            )
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

    def setSpeed(self, speed):
        self.speed = speed * TILE_WIDTH / 16

    def render(self, screen):
        if self.visible:
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)

    def update(self, dt):
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

    def validDirections(self) -> list[int]:
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions) -> int:
        return directions[randint(0, len(directions) - 1)]

    # EXERCISE 1
    def wanderRandom(self, directions) -> int:
        return self.randomDirection(directions)

    # EXERCISE 2
    def wanderBiased(self, directions: list[int]) -> int:
        ## NEW
        if self.direction in directions:
            if randint(0, 1) == 0:  # 50% of getting same direction
                return self.direction
            else:
                directions.remove(self.direction)
                return self.randomDirection(directions)
        else:
            return self.randomDirection(directions)

    def listDirection(self, directions):
        # pick an algorithm to make a path as a list of nodes
        pathNodes = aStar(self.node, self.djstraTarget.target)  # , heuristicDijkstra)
        # if the target node is the same as the node the ghost is standing on, alternative behaviour is needed
        if pathNodes != []:
            # get the direction from current node to the first node in the path list
            for direction in self.node.neighbors:
                if self.node.neighbors[direction] == pathNodes[0]:
                    return direction

        print("couldn't discern path, defaulting to random")
        return self.randomDirection(directions)

    # EXERCISE 3
    def FSMstateChecker(self):
        if self.myState == SEEK:
            self.directionMethod = self.goalDirectionDij
        elif self.myState == FLEE:
            self.directionMethod = self.fleeGoal
        elif self.myState == WANDER:
            self.directionMethod = self.wanderRandom
        elif self.myState == ELSE:
            self.states = choice([SEEK, FLEE, WANDER])
