import pygame
from pygame.locals import *

from algorithm import aStar, euclidianDistance
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from FSM import FSM, SeekPellet

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.fsm = FSM(self)
        self.fsm.change_state(SeekPellet())
        self.path = []
        self.path_index = 0
        self.ai_control = True  # Set to False if you want to let player control it again
        self.powered_up = False
        self.ghosts = []
        self.next_direction = None

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
        self.position += self.directions[self.direction] * self.speed * dt

        if not self.ai_control:
            direction = self.getValidKey()
        else:
            direction = self.direction  # Stay on AI's current direction

        # Handle AI path following
        if self.ai_control and self.path:
            if self.target == self.node and self.path_index < len(self.path):
                next_node = self.path[self.path_index]
                direction_vector = next_node.position - self.node.position

                # Translate vector into a direction (UP, DOWN, etc.)
                for dir, vec in self.directions.items():
                    if vec == direction_vector.normalize():
                        print("[Direction]", dir)
                        self.direction = dir
                        break

                self.target = next_node
                self.path_index += 1

        if self.overshotTarget():
            self.node = self.target

            # Portal warp
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            # Apply FSM decision
            if self.ai_control:
                self.fsm.update()

            # Apply FSM-set direction if it exists
            if self.next_direction:
                self.direction = self.next_direction
                self.next_direction = None

            # Get next target node based on direction
            proposed_target = self.getNewTarget(self.direction)

            # Only move if the direction is allowed
            if proposed_target and proposed_target != self.node:
                self.target = proposed_target
                self.setBetweenNodes(self.direction)
            else:
                self.direction = STOP

            self.setPosition()

    def render(self, screen):
        # Draw Pac-Man sprite at his current position
        screen.blit(self.image, self.position.asInt())

        # Draw A* path (debug)
        if hasattr(self, "path") and self.path:
            for i, node in enumerate(self.path[self.path_index:]):
                pos = node.position + Vector2(TILEWIDTH, TILEHEIGHT) / 2

                pygame.draw.circle(screen, (0, 255, 0), pos.asInt(), 4)  # Green dot

                if i > 0:
                    prev_node = self.path[self.path_index + i - 1]
                    prev_pos = prev_node.position + Vector2(TILEWIDTH, TILEHEIGHT) / 2
                    pygame.draw.line(screen, (0, 255, 0), prev_pos.asInt(), pos.asInt(), 2)  # Green line

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
                if pellet.__class__.__name__ == "PowerPellet":
                    print("[Pacman] Power pellet eaten!")
                    self.powered_up = True  # ← You'll use this in FSM
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

    def get_closest_pellet(self, pellets, node_group):
        closest = None
        shortest_distance = float('inf')

        for pellet in pellets:
            if not pellet.visible:
                continue

            pellet_node = node_group.getNodeFromPixels(pellet.position.x, pellet.position.y)
            if pellet_node is None:
                continue

            distance = euclidianDistance(self.node, pellet_node)
            if distance < shortest_distance:
                shortest_distance = distance
                closest = pellet

        return closest

    def set_path(self, path):
        self.path = path
        self.path_index = 0

    def ghost_nearby(self, ghosts, node_group, depth=8):
        for ghost in ghosts:
            if ghost.mode.current == FREIGHT:
                continue  # ignore vulnerable ghosts

            ghost_node = ghost.node
            pacman_node = self.node
            ghost_target = ghost.target

            if ghost_node is None or pacman_node is None or ghost_target is None:
                continue

            # Check if ghost is within N steps
            visited = set()
            frontier = [(pacman_node, 0)]

            found = False
            while frontier:
                current, dist = frontier.pop(0)
                if current == ghost_node:
                    found = True
                    break

                if dist < depth:
                    for neighbor in current.neighbors.values():
                        if neighbor and neighbor not in visited:
                            visited.add(neighbor)
                            frontier.append((neighbor, dist + 1))

            if found:
                # BONUS: check if ghost is heading toward Pac-Man
                to_pacman_before = euclidianDistance(ghost_node, pacman_node)
                to_pacman_after = euclidianDistance(ghost_target, pacman_node)

                if to_pacman_after < to_pacman_before:
                    print(f"[Evade Triggered] Ghost at {ghost_node.position} heading toward Pac-Man!")
                    return True

        return False

    def getReverseDirection(self):
        opposites = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        return opposites.get(self.direction, STOP)