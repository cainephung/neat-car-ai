import pygame
import math
from track import WALLS

CAR_WIDTH = 20
CAR_HEIGHT = 40
CAR_COLOR = (100, 200, 255)

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.vel = 2
        self.surface = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        self.surface.fill(CAR_COLOR)
        self.alive = True
        self.distance_driven = 0
        self.rect = self.surface.get_rect(center=(self.x, self.y))

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
        self.rect.center = (self.x, self.y)

        if self.check_collision():
            self.alive = False

    def cast_rays(self):
        angles = [-60, -30, 0, 30, 60]
        ray_lengths = []

        for a in angles:
            ray_angle = math.radians(self.angle + a)
            for i in range(1, 200, 2):
                ray_x = self.x + i * math.sin(ray_angle)
                ray_y = self.y - i * math.cos(ray_angle)

                for x1, y1, x2, y2 in WALLS:
                    if self.line_intersects(ray_x, ray_y, x1, y1, x2, y2):
                        ray_lengths.append(i / 200.0)
                        break
                else:
                    continue
                break
            else:
                ray_lengths.append(1.0)
        return ray_lengths

    def line_intersects(self, px, py, x1, y1, x2, y2):
        d1 = math.hypot(px - x1, py - y1)
        d2 = math.hypot(px - x2, py - y2)
        line_len = math.hypot(x2 - x1, y2 - y1)
        buffer = 2.0
        return line_len - buffer <= d1 + d2 <= line_len + buffer

    def check_collision(self):
        for x1, y1, x2, y2 in WALLS:
            if self.line_intersects(self.x, self.y, x1, y1, x2, y2):
                return True
        return False

    def draw(self, win):
        rotated = pygame.transform.rotate(self.surface, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        win.blit(rotated, rect)

        # Draw sensor rays
        angles = [-60, -30, 0, 30, 60]
        for i, a in enumerate(angles):
            ray_angle = math.radians(self.angle + a)
            length = 200 * self.cast_rays()[i]
            end_x = self.x + length * math.sin(ray_angle)
            end_y = self.y - length * math.cos(ray_angle)
            pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (end_x, end_y), 1)

    def get_inputs(self):
        return self.cast_rays()

    def get_fitness_delta(self):
        movement_score = self.distance_driven / 100  # scaled reward
        alive_bonus = 1.0 if self.alive else -2.0    # harsh penalty for dying
        return movement_score + alive_bonus

    def collides_with(self, other_car):
        return self.rect.colliderect(other_car.rect)
