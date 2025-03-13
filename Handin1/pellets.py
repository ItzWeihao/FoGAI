import pygame
from vector import Vector2
from constants import *
import numpy as np

class Pellet(object):
    def __init__(self, row, column, nodes):
        self.name = PELLET
        self.position = Vector2(column*TILEWIDTH, row*TILEHEIGHT)
        self.color = WHITE
        self.radius = int(2 * TILEWIDTH / 16)
        self.collideRadius = 2 * TILEWIDTH / 16
        self.points = 10
        self.visible = True
        # Find the closest node to this pellet
        self.node = self.findClosestNode(nodes)

    def findClosestNode(self, nodes):
        if not nodes.nodesLUT:  # Check if nodes are empty
            print("Error: No nodes found in nodesLUT!")
            return None

        closest_node = min(nodes.nodesLUT.values(), key=lambda n: self.position.distance(n.position))
        print(f"Pellet at {self.position} assigned to node at {closest_node.position}")
        return closest_node

    def render(self, screen):
        if self.visible:
            adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
            p = self.position + adjust
            pygame.draw.circle(screen, self.color, p.asInt(), self.radius)


class PowerPellet(Pellet):
    def __init__(self, row, column, nodes):
        Pellet.__init__(self, row, column, nodes)
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flashTime = 0.2
        self.timer= 0


    def update(self, dt):
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0


class PelletGroup(object):
    def __init__(self, pelletfile, nodes):
        self.pelletList = []
        self.powerpellets = []
        self.createPelletList(pelletfile, nodes)
        self.numEaten = 0

    def update(self, dt):
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)
                
    def createPelletList(self, pelletfile, nodes):
        data = self.readPelletfile(pelletfile)        
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.pelletList.append(Pellet(row, col, nodes))
                elif data[row][col] in ['P', 'p']:
                    pp = PowerPellet(row, col, nodes)
                    self.pelletList.append(pp)
                    self.powerpellets.append(pp)
                    
    def readPelletfile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def isEmpty(self):
        if len(self.pelletList) == 0:
            return True
        return False
    
    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)