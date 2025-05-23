from random import randint, uniform
import pygame
from constants import (
    PACMAN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STOP,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    RED,
    WHITE,
    YELLOW,
)
from vector import Vector2


class Ghost(object):
    def __init__(self, screen):
        self.name = PACMAN
        self.position = pygame.math.Vector2(200, 400)
        self.directions = {
            STOP: pygame.math.Vector2(),
            UP: pygame.math.Vector2(0, -1),
            DOWN: pygame.math.Vector2(0, 1),
            LEFT: pygame.math.Vector2(-1, 0),
            RIGHT: pygame.math.Vector2(1, 0),
        }
        self.direction = STOP
        self.speed = 10
        self.radius = 10
        self.color = RED

        self.velocity = pygame.math.Vector2(self.speed, 0).rotate(uniform(0, 360))
        self.acceleration = Vector2()
        self.screen = screen
        self.last_update = 0

        self.target = pygame.math.Vector2(
            randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT)
        )

    def update(self, dt):
        # self.follow_mouse()
        # self.acceleration = self.seek_and_arrive(pygame.mouse.get_pos())
        self.acceleration = self.wander()
        self.velocity += self.acceleration
        if self.velocity.length() > self.speed:
            self.velocity.scale_to_length(self.speed)
        self.position += self.velocity
        if self.position.x > SCREEN_WIDTH:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        if self.position.y > SCREEN_HEIGHT:
            self.position.y = 0
        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT

        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.getValidKey()
        self.direction = direction

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_UP]:
            return UP
        if key_pressed[pygame.K_DOWN]:
            return DOWN
        if key_pressed[pygame.K_LEFT]:
            return LEFT
        if key_pressed[pygame.K_RIGHT]:
            return RIGHT
        return STOP

    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def follow_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        # Avoid a division by zero in normalization
        mouse_pos = (mouse_pos[0] + 1, mouse_pos[1] + 1)
        self.velocity = (mouse_pos - self.position).normalize() * 0.2
        # normalize == make length 1
        # unit vectors are usually used for representing direction
        # and we can scale it to whatever the velocity is

    def seek(self, target: pygame.Vector2):
        self.desired_velocity = (target - self.position).normalize() * self.speed
        steer = self.desired_velocity - self.velocity
        STEERING_FORCE = 0.5
        if steer.length() > STEERING_FORCE:
            steer.scale_to_length(STEERING_FORCE)
        return steer

    def seek_and_arrive(self, target: tuple[int, int]):
        APPROACH_RADIUS = 50
        self.desired_velocity = target - self.position
        distance = (
            self.desired_velocity.length()
        )  # we get the distance before normalizing the desired
        self.desired_velocity.normalize_ip()  # ip = in place
        if distance < APPROACH_RADIUS:
            self.desired_velocity *= distance / APPROACH_RADIUS * self.speed
        else:
            self.desired_velocity *= self.speed
        steer = self.desired_velocity - self.velocity
        STEERING_FORCE = 0.5
        if steer.length() > STEERING_FORCE:
            steer.scale_to_length(STEERING_FORCE)
        return steer

    def draw_vectors(self):
        scale = 25
        APPROACH_RADIUS = 50
        # vel vector
        pygame.draw.line(
            self.screen,
            YELLOW,
            self.position,
            (self.position + self.velocity * scale),
            5,
        )
        # desired
        pygame.draw.line(
            self.screen,
            RED,
            self.position,
            (self.position + self.desired_velocity * scale),
            5,
        )
        if self.WANDER_TYPE == 1:
            pygame.draw.circle(
                self.screen, WHITE, (int(self.target.x), int(self.target.y)), 8
            )

    def wander(self):
        RAND_TARGET_TIME = 500
        self.WANDER_TYPE = 1

        # select random target every few sec
        now = pygame.time.get_ticks()  # returns time since pygame.init() was called
        if now - self.last_update > RAND_TARGET_TIME:
            self.last_update = now
            self.target = pygame.math.Vector2(
                randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT)
            )
        return self.seek(self.target)
