from algorithms import aStar
from algorithms import euclidianDistance
from pellets import PelletGroup
from vector import Vector2
from constants import *
import math
import pygame

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
        print("AI searching for nearest pellet...")  # Debug log

        # Step 1: Get valid directions from Pac-Man
        valid_moves = pacman.getValidDirections()
        print(f"Valid moves: {valid_moves}")  # Debug log

        if not valid_moves:
            print("Pac-Man has no valid moves! AI stopping.")
            pacman.direction = STOP
            return

        # Step 2: Find the closest pellet that Pac-Man can reach
        if pacman.pellets.pelletList:
            valid_pellets = [
                p for p in pacman.pellets.pelletList if aStar(pacman.node, p.node)
            ]

            if not valid_pellets:
                print("A* Warning: No valid paths to any pellet!")
                return

            nearest_pellet = min(valid_pellets, key=lambda p: euclidianDistance(pacman.node, p.node))
            print(f"Target pellet at {nearest_pellet.position}, Node: {nearest_pellet.node.position}, Pacman: {pacman.position}")

            # Step 3: Compute paths for each valid move
            best_direction = None
            shortest_path = None
            last_node = pacman.previous_node  # Track the last node visited

            for direction in valid_moves:
                next_node = pacman.node.neighbors[direction]

                if next_node and (next_node != last_node or len(valid_moves) == 1):  # Avoid going back unless necessary
                    print(f"🔍 Running A* from {pacman.node.position} to {nearest_pellet.node.position}")

                    path = aStar(pacman.node, nearest_pellet.node)

                    print(f"Path Length: {len(path)}")

                    if not path:
                        print("🚨 A* failed to find a path!")

                    if path and (shortest_path is None or len(path) < len(shortest_path)):
                        best_direction = direction
                        shortest_path = path  # Store the best path

            # Step 4: Set Pac-Man’s direction to the best option
            if best_direction is not None:
                pacman.previous_node = pacman.node
                pacman.direction = best_direction
                pacman.path = shortest_path  # ✅ Store path for rendering
                print(f"AI setting Pac-Man direction to: {best_direction}")
                print(f"AI calculated path: {[node.position for node in shortest_path]}")
                return
            elif best_direction is None and shortest_path is not None:
                if len(shortest_path) > 2:
                    best_direction = next((direction for direction in valid_moves if
                                           pacman.node.neighbors[direction] == shortest_path[2]),
                                          None)
                else:
                    return
            else:
                print("=== AI found a path but no valid forward direction! ===")
                print(f"Pac-Man at Node: {pacman.node.position}")
                print(f"Valid Moves at this Node: {valid_moves}")
                print(f"Target Pellet: {nearest_pellet.node.position}")
                print(f"Calculated Path: {[node.position for node in shortest_path] if shortest_path else 'No path'}")

        # Step 5: If there are no more pellets, stop moving
        if not pacman.pellets.pelletList:
            print("No more pellets. AI stopping.")
            pacman.direction = STOP

        # Step 6: Check if a ghost is too close and trigger flee mode
        if any(g.node.position.distance(pacman.position) < 30 and g.mode.current is not FREIGHT for g in pacman.ghosts):
            print("Ghost detected nearby! Switching to Flee mode.")
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
        self.pacmanPlayer = pacman
        self.pellets = pellets
        self.ghosts = ghosts
        self.nodes = nodes
        self.path = []

    def change_state(self, state):
        self.state.exit(self)
        self.state = state
        self.state.enter(self)

    def update(self):
        self.state.execute(self)

    def follow_path(self, path):
        if not path:
            print("A* Warning: Trying to follow an empty path!")
            return

            # Step 1: Store the path if it's the first time following it
        if not self.path:
            self.path = path[:]  # Copy the full path

        print(f"Full path length: {len(self.path)}")

        # Step 2: Get the next node
        next_node = self.path[0]
        next_next_node = self.path[1] if len(self.path) > 1 else None

        print(f"Next node: {next_node.position}")

        # Step 3: Get valid movement options
        valid_directions = self.pacmanPlayer.get_valid_directions()

        # Step 4: Move in a valid direction, but do NOT teleport!
        for direction, neighbor in self.pacmanPlayer.node.neighbors.items():
            if neighbor == next_node and direction in valid_directions:
                self.pacmanPlayer.direction = direction
                self.pacmanPlayer.target = next_node  # Set movement target
                print(f"Pac-Man moving {direction} toward {next_node.position}")

                # Step 5: Prepare for next move without teleporting
                if next_next_node and next_next_node in self.pacmanPlayer.node.neighbors.values():
                    print(f"Planning for next move to {next_next_node.position}")
                    self.path.pop(0)  # Remove first node but keep the second
                return

    def execute(self, pacman):
        """Ensure AI can be called externally (e.g., when Pac-Man hits a wall)."""
        if self.state:
            self.state.execute(pacman)  # Trigger AI behavior

