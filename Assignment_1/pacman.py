import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from FSM import *

class Pacman(Entity):
    def __init__(self, node, nodes):
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
        self.closestGhostDistance = None
        self.closestPellet = None
        self.nodes = nodes
        self.power_time = None
        self.timer = None

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
        self.closestGhostDistance = None
        self.FSM.current_state = self.FSM.eat
        self.power = False
        self.power_time = None

    def update(self, dt, screen):
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt

        if self.alive:
            self.getClosestGhostPosition()
            self.FSM.updateState(self)

        if self.power:
            self.timer += dt
            if self.timer >= self.power_time:
                self.power_time = None
                self.power = False

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            direction = self.directionMethod(self.validDirections())

            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
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

    def setPower(self):
        self.power = True
        self.power_time = 6
        self.timer = 0

    def setGhost(self, ghosts):
        self.ghosts = ghosts

    def getClosestGhostPosition(self):
        self.closestGhost = None
        self.closestGhostDistance = float("inf")
        self.ghostDistances = []

        for ghost in self.ghosts:
            if ghost.mode.current != SPAWN:
                distance = (self.position - ghost.position).magnitude()
                self.ghostDistances.append((ghost, distance))

                if distance < self.closestGhostDistance:
                    self.closestGhost = ghost
                    self.closestGhostDistance = distance

    def fleeFromGhost(self):
        if self.closestGhost is not None:
            ghost_pos = self.closestGhost.position
            # direction_to_ghost = (ghost_pos - self.position).normalize()

            # If ghost is directly ahead and not already turning, reverse
            if self.target == self.closestGhost.node and not self.oppositeDirection(self.direction):
                self.reverseDirection()
                return True

            danger_ghosts = [(g, d) for g, d in self.ghostDistances if g.mode.current == CHASE]
            if danger_ghosts:
                danger_ghost = min(danger_ghosts, key=lambda x: x[1])[0]
                ghost_pos = danger_ghost.position

            # Otherwise, pick a flee goal
            direction_away = (self.position - ghost_pos).normalize()
            flee_pos = self.position + direction_away * 30

            closest_node = self.nodes.getClosestNode(flee_pos)
            if closest_node:
                self.goal = closest_node.position
                self.directionMethod = self.goalDirection
                return True

        return False

    def setPellets(self, pellets):
        self.pellets = pellets

    def moveToClosestPelletPosition(self):
        closestPellet = self.pellets.getClosestPellet(self)
        if closestPellet is not None and closestPellet.position.magnitude() < 40 and self.power or not self.power:
            self.goal = closestPellet.position
            self.directionMethod = self.goalDirection
            return True
        return False

    def huntClosestGhost(self):
        freight_ghosts = [(g, d) for g, d in self.ghostDistances if g.mode.current == FREIGHT]
        if freight_ghosts:
            target_ghost = min(freight_ghosts, key=lambda x: x[1])[0]
            self.goal = target_ghost.position
            self.directionMethod = self.goalDirection
            return True
        return False