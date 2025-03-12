from constants import FLEE, SCREEN_HEIGHT, SCREEN_WIDTH, SEEK, WANDER


class State(object):
    def __init__(self, state: int):
        self.state = state

    # EXERCISE 12
    def getOtherStates(self, state1, state2):
        # SEEK
        if self.state == SEEK:
            self.wander = state1
            self.flee = state2
            self.seek2wander = Transition(self.state, self.wander)
        # WANDER
        if self.state == WANDER:
            self.seek = state1
            self.flee = state2
            self.wander2seek = Transition(self.state, self.seek)
            self.wander2flee = Transition(self.state, self.flee)
        # FLEE
        if self.state == FLEE:
            self.seek = state1
            self.wander = state2
            self.flee2seek = Transition(self.state, self.seek)

    # Return which transitions are possible from each state
    def getTransitions(self):
        if self.state == SEEK:
            return [self.seek2wander]
        elif self.state == WANDER:
            return [self.wander2seek, self.wander2flee]
        elif self.state == FLEE:
            return [self.flee2seek]
        else:
            return []


class Transition(object):
    def __init__(self, start_state: int, target_state: int):
        self.start_state = start_state
        self.target_state = target_state

    # EXERCISE 8
    def seek2wander(self, path_len: int):
        return path_len < 2

    def wander2seek(self, timer: float, position: tuple[int, int]):
        return (
            timer >= 2.0
            and timer <= 5.0
            and position[0] < SCREEN_WIDTH / 2
            and position[1] < SCREEN_HEIGHT / 2
        )

    def wander2flee(self, timer: float):
        return timer > 5.0

    def flee2seek(self, coordinates: tuple[int, int]):
        if any(
            [
                coordinates == (16, 64),  # top-left
                coordinates == (416, 64),  # top-right
                coordinates == (16, 464),  # bot-left
                coordinates == (416, 464),  # bot right
            ]
        ):
            return True
        else:
            return False

    # EXERCISE 9
    # Tests for checking if state has to change
    def isTriggered(self, path_len: int, position: tuple[int, int], timer: float):
        # SEEK
        if self.start_state == SEEK and self.target_state == WANDER:
            return self.seek2wander(path_len)
        # WANDER
        if self.start_state == WANDER and self.target_state == SEEK:
            return self.wander2seek(timer, position)
        if self.start_state == WANDER and self.target_state == FLEE:
            return self.wander2flee(timer)
        # FLEE
        if self.start_state == FLEE and self.target_state == SEEK:
            return self.flee2seek(position)
        return False


class StateMachine(object):
    # EXERCISE 14
    def __init__(self, initial_state: int):
        self.wander = State(WANDER)
        self.seek = State(FLEE)
        self.flee = State(SEEK)

        self.wander.getOtherStates(self.seek, self.flee)
        self.seek.getOtherStates(self.wander, self.flee)
        self.flee.getOtherStates(self.seek, self.wander)

        if self.initial_state == SEEK:
            self.initial_state = self.seek
        elif self.initial_state == WANDER:
            self.initial_state = self.wander
        elif self.initial_state == FLEE:
            self.initial_state = self.flee

        self.current_state = self.initial_state

    # EXERCISE 15
    # Checks and applies transitions, returning a list of actions.
    def updateState(self, path_len, coordinates, timer):
        triggered = None
        for transition in self.current_state.getTransitions():
            if transition.isTriggered(path_len, coordinates, timer):
                triggered = transition
                break

        if triggered is not None:
            target_state = triggered.target_state

            # current state exit code

            # next state enter code

            self.current_state = target_state
            # return
        # update
