from constants import *
from algorithms import aStar

class State(object):
    def __init__(self, state):
        self.state = state
        self.name = state

    def getOtherStates(self, state1, state2):
        # EAT State
        if self.state == EAT:
            self.flee = state1
            self.hunt = state2
            self.eat2flee = Transition(self.state, self.flee)
            self.eat2hunt = Transition(self.state, self.hunt)
        if self.state == FLEE:
            self.eat = state1
            self.hunt = state2
            self.flee2eat = Transition(self.state, self.eat)
            self.flee2hunt = Transition(self.state, self.hunt)
        if self.state == HUNT:
            self.eat = state1
            self.flee = state2
            self.hunt2eat = Transition(self.state, self.eat)
            self.hunt2flee = Transition(self.state, self.flee)

    def getTransition(self):
        if self.state == EAT:
            return [self.eat2flee, self.eat2hunt]
        elif self.state == FLEE:
            return [self.flee2eat, self.flee2hunt]
        elif self.state == HUNT:
            return [self.hunt2eat, self.hunt2flee]
        else:
            return []

    def runState(self, pacman):
        if self.state == EAT:
            pacman.moveToClosestPelletPosition()
        if self.state == FLEE:
            pacman.fleeFromGhost()
        if self.state == HUNT:
            pacman.huntClosestGhost()

class Transition(object):
    def __init__(self, from_state, to_state):
        self.from_state = from_state
        self.to_state = to_state

    # TODO
    def eat2flee(self, pacman):
        ghost_distance = pacman.closestGhostDistance
        if ghost_distance is not None and ghost_distance < 45:
            return True
        return False

    # TODO
    def eat2hunt(self, pacman):
        ghost_distance = pacman.closestGhostDistance
        if pacman.power and pacman.closestGhost is not None and pacman.closestGhost.mode.current == FREIGHT and ghost_distance is not None and ghost_distance < 10:
            return True
        return False

    # TODO
    def flee2eat(self, pacman):
        ghost_distance = pacman.closestGhostDistance
        if ghost_distance is not None and ghost_distance > 85:
            return True
        return False

    # TODO
    def flee2hunt(self, pacman):
        if pacman.power and pacman.closestGhost is not None and pacman.closestGhost.mode.current == FREIGHT:
            return True
        return False

    # TODO
    def hunt2eat(self, pacman):
        ghost_distance = pacman.closestGhostDistance
        if pacman.power is False or ghost_distance is not None and ghost_distance > 10 and pacman.power is True:
            return True
        return False

    # TODO
    def hunt2flee(self, pacman):
        ghost_distance = pacman.closestGhostDistance
        if pacman.power is False and ghost_distance is not None and ghost_distance < 45:
            return True
        return False

    def isTriggered(self, pacman):
        # EAT change into any other state
        if self.from_state == EAT and self.to_state.state == FLEE:
            return self.eat2flee(pacman)      # Change Eating -> Fleeing
        if self.from_state == EAT and self.to_state.state == HUNT:
            return self.eat2hunt(pacman)      # Change Eating -> Hunting

        # FLEE change into any other state
        if self.from_state == FLEE and self.to_state.state == EAT:
            return self.flee2eat(pacman)      # Change Fleeing -> Eating
        if self.from_state == FLEE and self.to_state.state == HUNT:
            return self.flee2hunt(pacman)     # Change Fleeing -> Hunting

        # HUNT change into any other state
        if self.from_state == HUNT and self.to_state.state == EAT:
            return self.hunt2eat(pacman)      # Change Hunting -> Eating
        if self.from_state == HUNT and self.to_state.state == FLEE:
            return self.hunt2flee(pacman)     # Change Hunting -> Fleeing

class FSM(object):
    def __init__(self, initial_state: int):
        self.eat = State(EAT)
        self.flee = State(FLEE)
        self.hunt = State(HUNT)

        self.eat.getOtherStates(self.flee, self.hunt)
        self.flee.getOtherStates(self.eat, self.hunt)
        self.hunt.getOtherStates(self.eat, self.flee)

        initial_state = self.eat

        self.current_state = initial_state

    def updateState(self, pacman):
        #self.current_state.runState(pacman)

        #for transition in self.current_state.getTransition():
        #    if transition.isTriggered(pacman):
        #        print(f"Transitioning from {transition.from_state} to {transition.to_state}")
        #        self.current_state = transition.to_state
        #        break

        print("== FSM Update ==")
        print("Current state:", self.current_state.state)
        self.current_state.runState(pacman)
        print("Ghost distance:", pacman.closestGhostDistance)

        for transition in self.current_state.getTransition():
            print(f"Checking: {transition.from_state} -> {transition.to_state}")
            print(transition.isTriggered(pacman))
            if transition.isTriggered(pacman):
                print(f"Transitioning from {transition.from_state} to {transition.to_state}")
                self.current_state = transition.to_state
                break