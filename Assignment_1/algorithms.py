# From Jakob Ehlers!
# Taken from exercises

import math
from nodes import Node
import sys


# this calculates pyhtogoras for two nodes, it's used as heuristic for astar
def euclidianDistance(node0: Node, node1: Node):
    aSquared = (node1.position.x - node0.position.x) ** 2
    bSquared = (node1.position.y - node0.position.y) ** 2
    return math.sqrt(aSquared + bSquared)


# basically copied from the lectured slides
# the one difference is that this doesn't need a direct reference to the graph as it is implicitly in the nodes
def aStar(nodes, start_node):
    unvisited_nodes = list(nodes.costs)
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node is None or shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        if current_min_node is None:
            break

        neighbors = nodes.getNeighbors(current_min_node)
        for neighbor in neighbors:
            tentative_value = shortest_path[current_min_node] + euclidianDistance(
                current_min_node, neighbor
            )
            if tentative_value < shortest_path.get(neighbor, max_value):
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node

        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    return previous_nodes, shortest_path