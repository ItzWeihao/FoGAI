import pygame
import random
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from FSM import PacmanAI
from FSM import Search

class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.nodes = nodes

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def setGhosts(self, ghosts):
        self.ghosts = ghosts

    def setPellets(self, pellets):
        self.pellets = pellets

    def setFSM(self, pellets, ghosts, nodes):
        self.fsm = PacmanAI(self, pellets, ghosts, nodes)

    def update(self, dt):	
        self.sprites.update(dt)

        # print(self.position)

        self.position += self.directions[self.direction]*self.speed*dt
        # direction = self.getValidKey()
        if hasattr(self, "fsm"):
            self.fsm.update()

        # print(self.direction)

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            self.target = self.getNewTarget(self.direction)

            if self.target is not self.node:
                # validDirectionsSize = len(self.get_valid_directions())
                # randomInt = random.randint(0, validDirectionsSize - 1)
                self.direction = self.direction
                # print(self.get_valid_directions())
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(self.direction):
                self.reverseDirection()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP  

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                self.pellets.pelletList.remove(pellet)  # Remove eaten pellet
                self.fsm.change_state(Search())
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def move_to(self, target_position):
        """Move Pac-Man towards the next node in the path."""
        if target_position in self.node.neighbors.values():
            # Find the direction that leads to the target node
            for direction, neighbor in self.node.neighbors.items():
                if neighbor == target_position:
                    self.direction = direction
                    self.target = target_position
                    return

        # If no valid neighbor found, stop
        self.direction = STOP

    def get_valid_directions(self):
        """Returns a list of valid movement directions for Pac-Man."""
        valid_directions = []

        # Check all possible movement directions (UP, DOWN, LEFT, RIGHT)
        for direction, neighbor in self.node.neighbors.items():
            if neighbor is not None:  # If there is a valid path in this direction
                valid_directions.append(direction)

        return valid_directions  # Returns a list like [LEFT, UP]