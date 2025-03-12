from algorithms import aStar
from pellets import PelletGroup
from vector import Vector2
from constants import *
import math


class State:
    def enter(self, pacman):
        pass

    def execute(self, pacman):
        pass

    def exit(self, pacman):
        pass


class Search(State):
    def execute(self, pacman):
        # print("Search")
        if pacman.pellets.pelletList:

            nearest_pallet = min(pacman.nodes.nodesLUT.values(), key=lambda n: pacman.pacman.position.distance(n.position))

            path = aStar(pacman.pacman.node, nearest_pallet)
            # pacman.follow_path(path)  # Continue following the path dynamically

            print("pacman position", pacman.pacman.position.x, pacman.pacman.position.y)
            print("nearest_node", nearest_pallet.position.x, nearest_pallet.position.y)

            # else:
                # print("No valid path found.")

        # If there are no more pellets, stop searching
        if not pacman.pellets.pelletList:
            print("No more pellets. AI stopping.")
            pacman.direction = STOP  # Prevent unnecessary movement


        if any(g.node.position.distance(pacman.pacman.position) < 30 and g.mode.current is not FREIGHT for g in pacman.ghosts):
            pacman.change_state(Flee())


class Eat(State):
    def execute(self, pacman):
        print("Eating")
        if pacman.powered_up:
            edible_ghosts = [g for g in pacman.ghosts if g.mode.current is FREIGHT]
            if edible_ghosts:
                nearest_ghost = min(edible_ghosts, key=lambda g: pacman.pacman.position.distance(g.position))
                path = aStar(pacman.pacman.node, nearest_ghost)
                pacman.follow_path(path)
            else:
                pacman.change_state(Search())
        else:
            nearest_pellet = min(pacman.pellets.pelletList,
                                 key=lambda p: pacman.pacman.position.distance(p.position))
            path = aStar(pacman.pacman.node, nearest_pellet)
            pacman.follow_path(path)

        if any(g.node.position.distance(pacman.pacman.position) < 50 and g.mode.current is not FREIGHT for g in pacman.ghosts):
            pacman.change_state(Flee())


class Flee(State):
    def execute(self, pacman):
        print("Flee")
        safe_spot = max(pacman.pacman.nodes.nodesLUT.values(), key=lambda n: min(g.position.distance(n.position) for g in pacman.ghosts))
        path = aStar(pacman.pacman.node, safe_spot)
        if path:
            pacman.follow_path(path)

        if all(g.node.position.distance(pacman.pacman.position) > 100 or g.mode.current is FREIGHT for g in pacman.ghosts):
            pacman.change_state(Search())


class PacmanAI:
    def __init__(self, pacman, pellets, ghosts, nodes):
        self.state = Search()
        self.pacman = pacman
        self.pellets = pellets
        self.ghosts = ghosts
        self.nodes = nodes

    def change_state(self, state):
        self.state.exit(self)
        self.state = state
        self.state.enter(self)

    def update(self):
        self.state.execute(self)

    def follow_path(self, path):
        if path:
            next_node = path.pop(0)  # Get the next node in the path

            # Get valid movement options
            valid_directions = self.pacman.get_valid_directions()

            # Ensure Pac-Man moves in a valid direction
            for direction, neighbor in self.pacman.node.neighbors.items():
                if neighbor == next_node and direction in valid_directions:
                    self.pacman.direction = direction
                    self.pacman.move_to(next_node)
                    break  # Stop once a valid direction is found

            if path:
                self.follow_path(path)  # Keep following dynamically
