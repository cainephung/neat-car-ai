import pygame
import neat
import os
from car import Car

# Pygame setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEAT Car AI")

FPS = 60
TRACK_COLOR = (200, 200, 200)
BG_COLOR = (30, 30, 30)

def draw_window(cars):
    WIN.fill(BG_COLOR)
    for car in cars:
        car.draw(WIN)
    pygame.display.update()

def eval_genomes(genomes, config):
    cars = []
    nets = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        car = Car(400, 500)
        cars.append(car)
        nets.append(net)
        ge.append(genome)

    run = True
    clock = pygame.time.Clock()

    while run and len(cars) > 0:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        for i, car in enumerate(cars):
            # Basic sensor inputs (placeholder values for now)
            inputs = car.get_inputs()
            output = nets[i].activate(inputs)

            car.update(output)
            ge[i].fitness += car.get_fitness_delta()

        draw_window(cars)

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
