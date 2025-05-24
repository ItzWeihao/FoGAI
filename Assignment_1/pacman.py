import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from FSM import *

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.power = False
        self.FSM = FSM(EAT)
        self.closestGhost = None

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

    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        self.getClosestGhostPosition()
        #self.getClosestPelletPosition()
        self.getNearestPellet()
        self.FSM.updateState(self, self.closestPellet, self.closestGhost)
        direction = self.directionMethod(self.validDirections())
        # print(self.power)
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
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
                return pellet
        return None

    def pacmanPowered(self, power):
        self.power = power
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

    def setGhost(self, ghosts):
        self.ghosts = ghosts

    def getClosestGhostPosition(self):
        closestDistance = 100

        for ghost in self.ghosts:
            distance = (self.position - ghost.position).magnitude()
            if ghost.mode.current != SPAWN:
                if distance < closestDistance:
                    self.closestGhost = ghost
                    closestDistance = distance
                    # print(closestGhost, ": ", closestDistance)

    def setPellets(self, pellets):
        self.pellets = pellets

    def getClosestPelletPosition(self):
        #for pellet in self.pellets.pelletList:
        closestPellet = self.pellets.getClosestPellet(self)
        if closestPellet is not None and closestPellet.position.magnitude() < 40 and self.power or not self.power:
            self.directionMethod = self.goalDirection
            self.goal = closestPellet.position
            self.closestPellet = closestPellet
            self.debugFollow = 0
            # print(closestPellet)
            return True
        return False

    def getNearestPellet(self):
        # closestPellet = None
        closestDistance = 1000000

        for pellet in self.pellets.pelletList:
            distance = (self.position - pellet.position).magnitude()
            if distance < closestDistance:
                self.closestPellet = pellet
                closestDistance = distance

        # self.currentSeekTarget = self.closestPellet

    def moveTowardNearest(self, target):
        if not target:
            return False

        closest_target = None
        closest_dist = float('inf')

        dist = (target.position - self.position).magnitude()
        if dist < closest_dist:
            closest_dist = dist
            closest_target = target

        if closest_target:
            self.goal = closest_target.position
            self.directionMethod = self.goalDirection  # Assuming goalDirection is a function
            self.debugFollow = 0
            return True

        return False