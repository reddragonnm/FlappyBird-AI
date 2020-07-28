import pygame as pg
import neat
from collections import deque
import random

pg.init()
pg.font.init()

draw_lines = True

screen_width, screen_height = 400, 600
screen = pg.display.set_mode((screen_width, screen_height))

bg_image = pg.transform.scale(pg.image.load("Images/background.gif"), (screen_width, screen_height - 100))

font = pg.font.Font('freesansbold.ttf', 32)
WHITE = 255, 255, 255
RED = 255, 0, 0
GREEN = 0, 255, 0

fps_clock = pg.time.Clock()
fps = 20

class Bird:
    def __init__(self):
        self.x = screen_width // 4
        self.y = screen_height // 2

        self.image = pg.image.load("Images/bird.gif")
        self.rect = None

        self.jump_power = 50
        self.fall_power = 15

    def display(self):
        self.fall()
        self.rect = screen.blit(self.image, (self.x, self.y))

    def jump(self):
        if self.y > 0:
            self.y -= self.jump_power

    def fall(self):
        self.y += self.fall_power

class Pipe:
    def __init__(self):
        self.image_top = pg.transform.scale(pg.image.load("Images/pipet.gif"), (100, screen_height))
        self.image_bottom = pg.transform.scale(pg.image.load("Images/pipeb.gif"), (100, screen_height))

        self.top_rect = None
        self.bottom_rect = None

        self.gap = 150
        self.x = screen_width
        self.y = random.randint(10, screen_height - 110 - self.gap)

    def display(self):
        self.top_rect = screen.blit(self.image_top, (self.x, self.y - self.image_top.get_height()))
        self.bottom_rect = screen.blit(self.image_bottom, (self.x, self.y + self.gap))

    def move(self):
        self.x -= 10

    def check_collision(self, bird_rect):
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)

    def reached_bird(self):
        return self.x + self.image_top.get_width() == screen_width // 4

    def behind_bird(self):
        return self.x + self.image_top.get_width() < screen_width // 4

class Ground:
    def __init__(self):
        self.image = pg.image.load("Images/ground.gif")
        self.rect = None

        self.x = 0
        self.y = screen_height - self.image.get_height()

    def display(self):
        self.rect = screen.blit(self.image, (self.x, self.y))

    def collide(self, bird_rect):
        return self.rect.colliderect(bird_rect)

class GameEnv:
    def __init__(self):
        self.birds = []

        self.score = 0
        self.generation = 1
        self.alive_birds = len(self.birds)

        self.pipes = deque(maxlen=2)
        self.pipes.append(Pipe())

        self.ground = Ground()

    def add_bird(self, genome, config):
        genome.fitness = 0

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.birds.append(
            {
                "bird_obj": Bird(),
                "net": net,
                "genome": genome,
            }
        )

    def display_all(self):
        for bird in self.birds:
            bird["bird_obj"].display()

        for pipe in self.pipes:
            pipe.display()

        self.ground.display()

    def check_removal_birds(self):
        birds_to_remove = []
        for bird in self.birds:
            bird_rect = bird["bird_obj"].rect

            if self.ground.collide(bird_rect):
                birds_to_remove.append(bird)
                break

            for pipe in self.pipes:
                if bird["bird_obj"].y > screen_height:
                    birds_to_remove.append(bird)
                    break

                if pipe.check_collision(bird_rect):
                    birds_to_remove.append(bird)
                    break

        for rem in birds_to_remove:
            rem["genome"].fitness -= 1
            self.birds.remove(rem)

        self.alive_birds = len(self.birds)

    def move_pipes(self):
        pipes_to_append = []

        for pipe in self.pipes:
            pipe.move()

            if pipe.reached_bird():
                self.score += 1
                pipes_to_append.append(Pipe())

        self.pipes.extend(pipes_to_append)

    def move_birds(self):
        for bird in self.birds:
            bird["bird_obj"].display()
            bird["genome"].fitness += 1

            output = bird["net"].activate(self.get_info(bird["bird_obj"]))

            if output[0] > 0.5:
                bird["bird_obj"].jump()

    def get_info(self, bird):
        pipe = self.pipes[-1]

        if draw_lines:
            pg.draw.line(screen, RED, (bird.x, bird.y), (pipe.x, pipe.y), 3)
            pg.draw.line(screen, GREEN, (bird.x, bird.y), (pipe.x, pipe.y + pipe.gap), 3)

        return (
            bird.y,
            pipe.y,
            pipe.y + pipe.gap,
            pipe.x
        )

    def all_dead(self):
        return not len(self.birds) > 0

    def reset(self):
        self.birds = []
        self.score = 0

        self.pipes = deque(maxlen=2)
        self.pipes.append(Pipe())

        self.ground = Ground()

env = GameEnv()

def eval_genomes(genomes, config):
    global fps

    for _, genome in genomes:
        genome.fitness = 0
        env.add_bird(genome, config)

    while True:
        screen.blit(bg_image, (0, 0))

        env.move_pipes()
        env.display_all()
        env.move_birds()
        env.check_removal_birds()

        if env.all_dead():
            env.reset()
            break

        screen.blit(font.render(f"Generation: {env.generation}", True, WHITE), (10, screen_height - 100))
        screen.blit(font.render(f"Score: {env.score}", True, WHITE), (10, screen_height - 70))
        screen.blit(font.render(f"Birds Alive: {env.alive_birds}", True, WHITE), (10, screen_height - 40))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
                break

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    fps += 5
                elif event.key == pg.K_DOWN:
                    fps -= 5

        pg.display.update()
        fps_clock.tick(fps)

def main():
    config_file = "config.txt"

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(eval_genomes, 5000)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    main()
    pg.quit()
