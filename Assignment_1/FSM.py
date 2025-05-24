from constants import EAT, FLEE, HUNT
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

    def runState(self, pacman, closestPellet):
        if self.state == EAT:
            pacman.moveTowardNearest(closestPellet)

class Transition(object):
    def __init__(self, from_state, to_state):
        self.from_state = from_state
        self.to_state = to_state

    # TODO
    def eat2flee(self):
        pass

    # TODO
    def eat2hunt(self):
        pass

    # TODO
    def flee2eat(self):
        pass

    # TODO
    def flee2hunt(self):
        pass

    # TODO
    def hunt2eat(self):
        pass

    # TODO
    def hunt2flee(self):
        pass

    def isTriggered(self):
        # EAT change into any other state
        if self.from_state == EAT and self.to_state == FLEE:
            return self.eat2flee()      # Change Eating -> Fleeing
        if self.from_state == EAT and self.to_state == HUNT:
            return self.eat2hunt()      # Change Eating -> Hunting

        # FLEE change into any other state
        if self.from_state == FLEE and self.to_state == EAT:
            return self.flee2eat()      # Change Fleeing -> Eating
        if self.from_state == FLEE and self.to_state == HUNT:
            return self.flee2hunt()     # Change Fleeing -> Hunting

        # HUNT change into any other state
        if self.from_state == HUNT and self.to_state == EAT:
            return self.hunt2eat()      # Change Hunting -> Eating
        if self.from_state == HUNT and self.to_state == FLEE:
            return self.hunt2flee()     # Change Hunting -> Fleeing

class FSM(object):
    def __init__(self, initial_state: int):
        self.eat = State(EAT)
        self.flee = State(FLEE)
        self.hunt = State(HUNT)

        self.eat.getOtherStates(self.flee, self.hunt)
        self.flee.getOtherStates(self.eat, self.hunt)
        self.hunt.getOtherStates(self.eat, self.flee)

        if initial_state == EAT:
            initial_state = self.eat
        elif initial_state == FLEE:
            initial_state = self.flee
        elif initial_state == HUNT:
            initial_state = self.hunt

        self.current_state = initial_state

    def updateState(self, pacman, closestPellet, closestGhost):
        State.runState(self.current_state, pacman, closestPellet)
        # print(self.current_state.name)