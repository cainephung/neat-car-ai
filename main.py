import pygame
import neat
import os
from car import Car
from track import WALLS

# Pygame setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
pygame.display.set_caption("NEAT Car AI")

FPS = 60
TRACK_COLOR = (200, 200, 200)
BG_COLOR = (30, 30, 30)

def draw_window(cars):
    WIN.fill(BG_COLOR)

    # Draw track
    for x1, y1, x2, y2 in WALLS:
        pygame.draw.line(WIN, (255, 255, 255), (x1, y1), (x2, y2), 2)

    # Draw cars
    for car in cars:
        if car.alive:
            car.draw(WIN)

    pygame.display.update()

def eval_genomes(genomes, config):
    cars = []
    nets = []
    ge = []

    start_x, start_y = 300, 550
    offset_step = 10  # Spread cars out in grid to avoid overlapping

    start_x, start_y = 300, 550
    offset_step = 50  

    for idx, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        offset_x = (idx % 5) * offset_step
        offset_y = (idx // 5) * offset_step
        car = Car(start_x + offset_x, start_y - offset_y)

        cars.append(car)
        nets.append(net)
        ge.append(genome)


    run_time = 0
    max_time = 2000

    while run_time < max_time and any(car.alive for car in cars):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        draw_window(cars)

        for i, car in enumerate(cars):
            if not car.alive:
                continue

            inputs = car.get_inputs()
            output = nets[i].activate(inputs)
            car.update(output)

        # Car-to-car collision
        for i, car1 in enumerate(cars):
            if not car1.alive:
                continue
            for j, car2 in enumerate(cars):
                if i != j and car2.alive and car1.collides_with(car2):
                    car1.alive = False
                    car2.alive = False

        for i, car in enumerate(cars):
            ge[i].fitness = car.get_fitness_delta()

        CLOCK.tick(FPS)
        run_time += 1

def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    population.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
