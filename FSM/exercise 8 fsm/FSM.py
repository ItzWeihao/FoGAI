from ExerciseSession1.code.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from vector import Vector2


class State(object):
    def __init__(self, state):
        self.state = state

    # EXERCISE 12
    def getOtherStates(self, state1, state2):
        # SEEK

        # WANDER

        # FLEE
        return

    # EXERCISE 13
    # Return which transitions are possible from each state
    def getTransitions(self):
        return


class Transition(object):
    def __init__(self, start_state: State, target_state: State):
        self.start_state = start_state
        self.target_state = target_state

    # EXERCISE 8
    def seek2wander(self, lengthOfPathToEnemy: int):
        return lengthOfPathToEnemy < 2

    def wander2seek(self, timer: float, position: Vector2):
        return (
            timer >= 2.0
            and timer <= 5.0
            and position.x < SCREEN_WIDTH / 2
            and position.y < SCREEN_HEIGHT / 2
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
        ):  # bot-right
            return True
        else:
            return False

    # EXERCISE 9
    # Tests for checking if state has to change
    def isTriggered(self, path_len=None, coordinates=None, timer=None):
        # SEEK

        # WANDER

        # FLEE
        return


class StateMachine(object):
    # EXERCISE 14
    def __init__(self):
        return

    # EXERCISE 15
    # Checks and applies transitions, returning a list of actions.
    def updateState(self, path_len=None, coordinates=None, timer=None):
        return
