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
        self.node = node
        self.nodes = nodes
        self.previous_node = None  # Track previous node to prevent backtracking

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

        # Step 1: Move in the current direction at controlled speed
        movement = self.directions[self.direction] * self.speed * dt
        self.position += movement

        if self.overshotTarget():
            print(f"Pac-Man reached node at {self.target.position}")

            # Align Pac-Man with the target node
            self.position = self.target.position.copy()
            self.node = self.target
            self.target = None  # Clear the target

            # AI updates Pac-Man's direction at every node
            if hasattr(self, "fsm") and self.fsm:
                self.fsm.execute(self)  # Recalculate movement immediately

            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            self.target = self.getNewTarget(self.direction)

            if self.target is not self.node:
                self.direction = self.direction  # Keeping the same direction if valid
            else:
                self.target = self.getNewTarget(self.direction)

            # Ensure Pac-Man picks a new direction when hitting a wall
            if self.target is self.node:
                print(f"Pac-Man hit a wall at {self.node.position}. AI selecting a new direction.")
                self.direction = STOP  # Temporarily stop movement

                if self.fsm:  # Ensure AI re-evaluates movement
                    self.fsm.execute(self)  # Call AI to select a new path
                    print(f"Pac-Man AI set new direction: {self.direction}")

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

    def getValidDirections(self):
        """ Returns a list of valid movement directions based on node neighbors. """
        valid_moves = [direction for direction, node in self.node.neighbors.items() if node is not None]

        if not valid_moves:
            print(f"Pac-Man at {self.node.position} is stuck! No valid moves.")

        return valid_moves

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