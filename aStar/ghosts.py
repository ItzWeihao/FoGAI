import pygame
from pygame.locals import *
from algorithms import aStar
from vector import Vector2
from constants import *
from entity import Entity

from random import choice


class Ghost(Entity):
    def __init__(self, node, nodes, pacman=None):
        Entity.__init__(self, node)
        self.name = GHOST
        self.points = 200
        self.goal = Vector2()
        self.directionMethod = self.listDirection
        self.pacman = pacman
        self.nodes = nodes
        self.speed = 80

    def update(self, dt):
        self.goal = self.pacman.position
        Entity.update(self, dt)

    # Ghost can get stuck when having to reverse its direction
    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                # if key != self.direction * -1:
                directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def listDirection(self, directions):
        # pick an algorithm to make a path as a list of nodes
        pathNodes = aStar(self.node, self.pacman.target)  # , heuristicDijkstra)
        # if the target node is the same as the node the ghost is standing on, alternative behaviour is needed
        if pathNodes != []:
            # get the direction from current node to the first node in the path list
            for direction in self.node.neighbors:
                if self.node.neighbors[direction] == pathNodes[0]:
                    return direction

        print("couldn't discern path, defaulting to random")
        return self.randomDirection(directions)
