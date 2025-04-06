from algorithm import aStar, euclidianDistance
from constants import *

class State:
    def enter(self, entity):
        pass

    def execute(self, entity):
        pass

    def exit(self, entity):
        pass

class SeekPellet(State):
    def enter(self, entity):
        print("Entering *** SeekPellet *** State")

    def execute(self, entity):
        # if entity.powered_up:
        #     entity.fsm.change_state(PowerMode())
        #     return

        if entity.ghost_nearby(entity.ghosts, entity.node_group, depth=4):
            entity.fsm.change_state(EvadeGhost())
            return

        print("Seeking Pellets...")
        pellet = entity.get_closest_pellet(entity.pellets, entity.node_group)
        if pellet:
            pellet_node = entity.node_group.getNodeFromPixels(pellet.position.x, pellet.position.y)
            path = aStar(entity.node, pellet_node)
            if path and len(path) > 1:
                entity.set_path(path)
                next_node = path[1]
                direction_vector = (next_node.position - entity.node.position).normalize()

                for dir, vec in entity.directions.items():
                    if vec == direction_vector:
                        entity.next_direction = dir
                        entity.target = entity.getNewTarget(dir)
                        if entity.target and entity.target != entity.node:
                            entity.setBetweenNodes(dir)
                        break

    def exit(self, entity):
        print("Exiting *** SeekPellet *** State")

class EvadeGhost(State):
    def enter(self, entity):
        print("Entering *** EvadeGhost *** State")

    def execute(self, entity):
        print("[EvadeGhost] Evaluating escape...")

        # Step 1: Get danger sources
        ghost_nodes = [
            ghost.node for ghost in entity.ghosts
            if ghost.mode.current != FREIGHT and ghost.node
        ]

        if not ghost_nodes:
            print("[EvadeGhost] No ghosts nearby. Switching back.")
            entity.fsm.change_state(SeekPellet())
            return

        # Step 2: Find safest node (farthest from all ghosts)
        candidates = [
            node for node in entity.node_group.nodesLUT.values()
            if len(node.neighbors) >= 2
        ]

        best_node = None
        max_total_distance = -float('inf')

        for node in candidates:
            total_dist = sum(euclidianDistance(node, g) for g in ghost_nodes)
            if total_dist > max_total_distance:
                best_node = node
                max_total_distance = total_dist

        if best_node:
            from algorithm import aStar
            path = aStar(entity.node, best_node)
            entity.full_path = path  # for debugging

            if path and len(path) > 1:
                next_node = path[1]
                direction_vector = (next_node.position - entity.node.position).normalize()

                # Check if this step moves away from ghosts
                current_dist = min(euclidianDistance(entity.node, g) for g in ghost_nodes)
                next_dist = min(euclidianDistance(next_node, g) for g in ghost_nodes)

                if next_dist < current_dist:
                    print("[EvadeGhost] WARNING: Chosen path is moving TOWARD ghost!")
                else:
                    print(f"[EvadeGhost] Escaping: current_dist={current_dist:.2f}, next_dist={next_dist:.2f}")

                # Set next direction
                for dir, vec in entity.directions.items():
                    if vec == direction_vector:
                        entity.next_direction = dir
                        return

        print("[EvadeGhost] No valid escape path found.")

    def exit(self, entity):
        print("Exiting *** EvadeGhost *** State")

class ChaseFruit(State):
    def enter(self, entity):
        print("Entering *** ChaseFruit *** State")

    def execute(self, entity):
        print("Chasing Fruit...")

    def exit(self, entity):
        print("Exiting *** ChaseFruit *** State")

class PowerMode(State):
    def enter(self, entity):
        print("Entering *** PowerMode *** State")

    def execute(self, entity):
        print("[PowerMode] Seeking edible ghosts...")

        # Step 1: Get vulnerable ghosts
        vulnerable_ghosts = [
            g for g in entity.ghosts if g.mode.current == FREIGHT and g.node
        ]

        if not vulnerable_ghosts:
            print("[PowerMode] No edible ghosts left. Switching to SeekPellet.")
            entity.fsm.change_state(SeekPellet())
            return

        # Step 2: Choose closest ghost
        target_ghost = min(
            vulnerable_ghosts,
            key=lambda g: euclidianDistance(entity.node, g.node)
        )

        # Step 3: Calculate path
        path = aStar(entity.node, target_ghost.node)
        entity.full_path = path  # for debug visualization

        if path and len(path) > 1:
            next_node = path[1]
            direction_vector = (next_node.position - entity.node.position).normalize()

            for dir, vec in entity.directions.items():
                if vec == direction_vector:
                    entity.next_direction = dir
                    print(f"[PowerMode] Chasing ghost via {dir}")

                    # Start moving!
                    entity.target = entity.getNewTarget(entity.next_direction)
                    if entity.target and entity.target != entity.node:
                        entity.setBetweenNodes(entity.next_direction)
                    break
        else:
            print("[PowerMode] No valid path to ghost found.")

    def exit(self, entity):
        print("Exiting *** PowerMode *** State")
        entity.powered_up = False

class FSM:
    def __init__(self, owner):
        self.owner = owner
        self.current_state = None

    def change_state(self, new_state):
        if self.current_state:
            self.current_state.exit(self.owner)
        self.current_state = new_state
        self.current_state.enter(self.owner)

    def update(self):
        if self.current_state:
            self.current_state.execute(self.owner)

