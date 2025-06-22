import pygame
import math
from track import WALLS

CAR_WIDTH, CAR_HEIGHT = 20, 10

class Car:
    def __init__(self, x, y):
        self.speed = 0.0
        self.max_speed = 10.0  
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.velocity = 2
        self.alive = True

        self.prev_x = x
        self.prev_y = y
        self.prev_angles = []

    def draw_sensors(self, surface):
        sensor_length = 100
        angles = [-45, 0, 45]  # relative to car angle

        for a in angles:
            rad = math.radians(self.angle + a)
            end_x = self.x + sensor_length * math.cos(rad)
            end_y = self.y - sensor_length * math.sin(rad)
            pygame.draw.line(surface, (200, 200, 200), (self.x, self.y), (end_x, end_y), 1)

    def update(self, output):
        if not self.alive:
            return

        # Output[0] controls steering: -1 (left) to 1 (right)
        turn = output[0] * 5  # steering sensitivity
        self.angle += turn

        # Move forward
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.velocity
        dy = -math.sin(rad) * self.velocity
        self.x += dx
        self.y += dy

        # Update speed based on position change
        dx = self.x - self.prev_x
        dy = self.y - self.prev_y
        self.speed = (dx ** 2 + dy ** 2) ** 0.5
        self.prev_x = self.x
        self.prev_y = self.y

        # Collision with walls
        for wall in WALLS:
            if self.collides_with_wall(wall):
                self.alive = False
                break

    def draw(self, win):
        rect = pygame.Rect(0, 0, CAR_WIDTH, CAR_HEIGHT)
        rect.center = (self.x, self.y)
        rotated = pygame.transform.rotate(pygame.Surface((CAR_WIDTH, CAR_HEIGHT)), self.angle)
        rotated.fill((0, 255, 0))
        win.blit(rotated, rotated.get_rect(center=rect.center))

    def get_inputs(self):
        return [
            self.x / 800,
            self.y / 600,
            math.sin(math.radians(self.angle)),
            math.cos(math.radians(self.angle)),
            self.speed / self.max_speed  # 5th input
        ]


    def get_fitness_delta(self):
        return self.y

    def collides_with_wall(self, wall):
        x1, y1, x2, y2 = wall
        car_rect = pygame.Rect(self.x - 10, self.y - 5, 20, 10)
        return car_rect.clipline((x1, y1), (x2, y2))

    def collides_with(self, other_car):
        rect1 = pygame.Rect(self.x - 10, self.y - 5, 20, 10)
        rect2 = pygame.Rect(other_car.x - 10, other_car.y - 5, 20, 10)
        return rect1.colliderect(rect2)

    def is_spinning(self):
        self.prev_angles.append(self.angle)
        if len(self.prev_angles) > 10:
            self.prev_angles.pop(0)
        if len(set(int(a) for a in self.prev_angles)) <= 2:
            return True
        return False
