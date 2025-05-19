from algorithms import aStar
from algorithms import euclidianDistance
from pellets import PelletGroup
from vector import Vector2
from constants import *
import math
import pygame
import random

def renderPath(screen, pacman):
    """ Draw the A* path for Pac-Man """
    if hasattr(pacman, "path") and pacman.path:
        # ✅ Draw connecting lines between path nodes
        for i in range(len(pacman.path) - 1):
            pygame.draw.line(
                screen, (0, 255, 0),  # Green color for path
                pacman.path[i].position.asTuple(),
                pacman.path[i + 1].position.asTuple(),
                2  # Line thickness
            )

        # ✅ Draw path nodes as green dots
        for node in pacman.path:
            pygame.draw.circle(screen, (0, 255, 0), node.position.asInt(), 5)

class State:
    def enter(self, pacman):
        pass

    def execute(self, pacman):
        pass

    def exit(self, pacman):
        pass


class Search(State):
    def execute(self, pacman):
        # Check if a ghost is too close and trigger flee mode
        # Right now does nothing
        # distance = (pacman.position - pacman.ghost.position).magnitudeSquared()
        if any((pacman.position - g.position).magnitudeSquared() < 10000 and g.mode.current is not FREIGHT or g.mode.current is not SPAWN for g in
               pacman.ghosts):
            print("Ghost detected nearby! Switching to Flee mode.")
            pacman.fsm.change_state(Flee())

        print("========= AI searching for nearest pellet... =========")  # Debug log
        pacman.fsm.getNearestPellet()


class Eat(State):
    def execute(self, pacman):
        print("Eating")
        if pacman.powered_up:
            edible_ghosts = [g for g in pacman.ghosts if g.mode.current is FREIGHT]
            if edible_ghosts:
                nearest_ghost = min(edible_ghosts, key=lambda g: pacman.pacman.position.distance(g.position))
                path = aStar(pacman.pacman.node, nearest_ghost)
                pacman.fsm.follow_path(path)
            else:
                pacman.fsm.change_state(Search())
        else:
            nearest_pellet = min(pacman.pellets.pelletList,
                                 key=lambda p: pacman.pacman.position.distance(p.position))
            path = aStar(pacman.pacman.node, nearest_pellet)
            pacman.fsm.follow_path(path)

        if any(g.node.position.distance(pacman.pacman.position) < 50 and g.mode.current is not FREIGHT for g in pacman.ghosts):
            pacman.fsm.change_state(Flee())


class Flee(State):
    def execute(self, pacman):
        print("Flee")
        distances = []
        for direction in directions:
            vec = self.node.position + self.directions[direction] * TILEWIDTH - self.currentFleeTarget.position
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]

        safe_spot = max(pacman.nodes.nodesLUT.values(), key=lambda n: max(g.position.distance(n.position) for g in pacman.ghosts))
        path = aStar(pacman.node, safe_spot)

        pacman.fsm.follow_path(path)

        if all(g.node.position.distance(pacman.position) > 500 or g.mode.current is FREIGHT for g in pacman.ghosts):
            pacman.fsm.change_state(Search())


class PacmanAI:
    def __init__(self, pacman, pellets, ghosts, nodes):
        self.state = Search()
        self.pacmanPlayer = pacman
        self.pellets = pellets
        self.ghosts = ghosts
        self.nodes = nodes
        self.path = []
        self.currentSeekTarget = getNearestPellet()

    def checkForNearbyGhost(self):
        closestGhost = None
        closestDistance = 1000000

        for ghost in self.ghosts:
            distance = (self.position - ghost.position).magnitudeSquared()
            if distance < closestDistance:
                closestGhost = ghost
                closestDistance = distance

        if closestDistance < 10000:
            self.currentFleeTarget = closestGhost
            self.directionMethod = self.fleeDirection
        else:
            self.directionMethod = self.seekDirection

    def getNearestPellet(self):
        closestPellet = None
        closestDistance = 1000000

        for pellet in self.pellets.pelletList:
            distance = (self.position - pellet.position).magnitudeSquared()
            if distance < closestDistance:
                closestPellet = pellet
                closestDistance = distance

        self.currentSeekTarget = closestPellet
        return closestPellet

    def determineNextDirection(self, directions):
        # Get the shortest path between pacman's current movement target and the last target of the current target
        self.path = self.getAStarPathToPellet()
        # Get pacman's current movement target, then converts it to a node object
        pacmanTarget = self.target
        pacmanTarget = self.nodes.getNodeFromLUTNode(pacmanTarget)
        self.path.append(pacmanTarget)
        nextTargetNode = path[1]
        # Compares coordinates of pacman's target movement node and the next target node
        # if the x-coordinate of pacman's target movement node is greater than the x-coordinate of the next target node
        if pacmanTarget[0] > nextTargetNode[0] and 2 in directions: #Left
            return 2
        # if the x-coordinate of pacman's target movement node is less than the x-coordinate of the next target node
        if pacmanTarget[0] < nextTargetNode[0] and -2 in directions: #Right
            return -2
        # if the y-coordinate of pacman's target movement node is greater than the y-coordinate of the next target node
        if pacmanTarget[1] > nextTargetNode[1] and 1 in directions: #Up
            return 1
        # if the y-coordinate of pacman's target movement node is less than the y-coordinate of the next target node
        if pacmanTarget[1] < nextTargetNode[1] and -1 in directions: #Down
            return -1
        else:
            print(self.currentSeekTarget.direction)
            print(directions)
            # return the opposite direction of the current target's direction is in the valid directions
            if -1 * self.currentSeekTarget.direction in directions:
                return -1 * self.currentSeekTarget.direction
            else:
            # else return a random direction from the valid directions
                return choice(directions)

    def change_state(self, state):
        self.state.exit(self)
        self.state = state
        self.state.enter(self)

    def update(self):
        self.state.execute(self)

    def execute(self, pacman):
        """Ensure AI can be called externally (e.g., when Pac-Man hits a wall)."""
        if self.state:
            self.state.execute(pacman)  # Trigger AI behavior

