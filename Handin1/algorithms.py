# From Jakob Ehlers!
# Taken from exercises

import math
from queue import PriorityQueue
from nodes import Node


# this calculates pyhtogoras for two nodes, it's used as heuristic for astar
def euclidianDistance(node0: Node, node1: Node):
    aSquared = (node1.position.x - node0.position.x) ** 2
    bSquared = (node1.position.y - node0.position.y) ** 2
    return math.sqrt(aSquared + bSquared)


# basically copied from the lectured slides
# the one difference is that this doesn't need a direct reference to the graph as it is implicitly in the nodes
def aStar(start_node: Node, end_node: Node, heuristic=euclidianDistance):
    # distances is for storing the shortest distance to node
    distances = {start_node: 0.0}

    open_nodes = PriorityQueue()
    # counter is for tie-breaking distances ex. use random.random() for less determinism
    counter = 0
    open_nodes.put((heuristic(start_node, end_node), counter, start_node))
    counter += 1

    # incomming nodes is for storing the shortest path between nodes
    incomming_nodes = {}

    while open_nodes.not_empty:
        # we unwrapping the node from the tupple
        _, r, current_node = open_nodes.get()
        # if the next node is the target node the path has been set
        if current_node == end_node:
            # backtrak to reconstruct path
            path = []
            while current_node is not start_node:
                path.insert(0, current_node)
                current_node = incomming_nodes[current_node]
            return path

        for neighbor in current_node.neighbors.values():
            if neighbor is None:
                continue

            # the cost is the distance from the current_node to the neighbour
            cost = euclidianDistance(current_node, neighbor)

            new_distance = distances[current_node] + cost

            if neighbor not in distances or new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                # the predicted total is where the heuristic is applied
                predicted_total = new_distance + heuristic(neighbor, end_node)
                incomming_nodes[neighbor] = current_node
                open_nodes.put((predicted_total, counter, neighbor))
                counter += 1
    return []
