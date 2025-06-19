import pygame
import math

CAR_WIDTH = 20
CAR_HEIGHT = 40
CAR_COLOR = (100, 200, 255)

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # in degrees
        self.vel = 2
        self.surface = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        self.surface.fill(CAR_COLOR)
        self.rect = self.surface.get_rect(center=(x, y))
        self.alive = True
        self.distance_driven = 0

    def update(self, output):
        if not self.alive:
            return

        turn_left = output[0] > 0.5
        turn_right = output[1] > 0.5

        if turn_left:
            self.angle += 4
        if turn_right:
            self.angle -= 4

        radians = math.radians(self.angle)
        self.x += self.vel * math.sin(radians)
        self.y -= self.vel * math.cos(radians)
        self.distance_driven += self.vel

    def draw(self, win):
        rotated = pygame.transform.rotate(self.surface, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        win.blit(rotated, rect)

    def get_inputs(self):
        # Placeholder: return 5 constant values (for compatibility with config)
        return [0.5, 0.5, 0.5, 0.5, 0.5]

    def get_fitness_delta(self):
        # Basic fitness increase by distance
        return 0.1
