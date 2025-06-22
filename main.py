import pygame
import neat
import os
from car import Car
from track import WALLS

# Pygame setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEAT Car AI")
CLOCK = pygame.time.Clock()
FPS = 60

# For replay
BEST_GENOME = None
BEST_NET = None

def draw_window(cars):
    WIN.fill((30, 30, 30))
    for x1, y1, x2, y2 in WALLS:
        pygame.draw.line(WIN, (255, 255, 255), (x1, y1), (x2, y2), 2)
    for car in cars:
        if car.alive:
            car.draw(WIN)
    pygame.display.update()

def eval_genomes(genomes, config):
    global BEST_GENOME, BEST_NET

    cars = []
    nets = []
    ge = []

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
            if not car.alive:
                continue
            delta_y = car.prev_y - car.y
            if delta_y > 0:
                ge[i].fitness += delta_y  # reward for forward movement
            else:
                ge[i].fitness -= 0.5  # small penalty for reversing or no movement

            if car.is_spinning():
                ge[i].fitness -= 1  # penalty for spinning in place


        CLOCK.tick(FPS)
        run_time += 1

    best_index = max(range(len(ge)), key=lambda i: ge[i].fitness)
    BEST_GENOME = ge[best_index]
    BEST_NET = nets[best_index]

def replay_best():
    if BEST_NET is None:
        print("No best genome yet.")
        return

    car = Car(300, 550)
    run_time = 0
    max_time = 1000

    while run_time < max_time and car.alive:
        WIN.fill((30, 30, 30))
        for x1, y1, x2, y2 in WALLS:
            pygame.draw.line(WIN, (255, 255, 255), (x1, y1), (x2, y2), 2)

        inputs = car.get_inputs()
        output = BEST_NET.activate(inputs)
        car.update(output)
        car.draw(WIN)
        car.draw_sensors(WIN)

        print(f"Replay output: {output}, Speed: {car.speed:.2f}, Alive: {car.alive}")
        pygame.display.update()
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

    population.run(eval_genomes, 15)

    print("Training Complete! Press R to replay best car or close the window.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    replay_best()
    pygame.quit()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
