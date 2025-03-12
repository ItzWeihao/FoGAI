from vector import Vector2
from constants import GHOST
from entity import Entity


class Ghost(Entity):
    def __init__(self, node, pacman):
        Entity.__init__(self, node)
        self.name = GHOST
        self.points = 200
        self.goal = Vector2()
        # self.directionMethod = self.randomDirection
        self.pacman = pacman

        self.speed = 80

    def update(self, dt):
        self.goal = self.pacman.position
        Entity.update(self, dt)

    # EXERCISE 16
    # SEEK <--> WANDER --> FLEE
    #  ^---------------------'
    # SEEKtoWANDER = if target is < 2 nodes away
    # WANDERtoSEEK = if character is in top-left quarter in 2 < x <= 5 seconds
    # WANDERtoFLEE = after 5 seconds
    # FLEEtoSEEK = if character hits one of the corners
    def advancedFSM(self):
        return
