import pygame as pg
import neat
from random import randint
from collections import deque

pg.init()
pg.font.init()

screen_width, screen_height = 600, 400
screen = pg.display.set_mode((screen_width, screen_height))

WHITE = 255, 255, 255

fps = 20
fps_clock = pg.time.Clock()

speed = 5

class Background:
    class Cloud:
        def __init__(self, floor_y):
            self.floor_y = floor_y - 100
            self.cloud = pg.transform.scale(pg.image.load("images/cloud.png"), (screen_width // 12, 25))

            self.x = screen_width + self.cloud.get_width()
            self.y = randint(0, self.floor_y)
            self.speed = randint(3, 10)

        def display(self):
            screen.blit(self.cloud, (self.x, self.y))

            self.x -= self.speed

            if self.x < -self.cloud.get_width():
                self.speed = randint(3, 10)
                self.x = screen_width + self.cloud.get_width()
                self.y = randint(0, self.floor_y)

    def __init__(self):
        self.floor = pg.transform.scale(pg.image.load("images/floor.png"), (screen_width, screen_height // 40))
        self.floor_x = 0
        self.floor_y = screen_height - 100

        self.clouds= [self.Cloud(self.floor_y) for _ in range(3)]

    def display(self):
        screen.blit(self.floor, (self.floor_x, self.floor_y))

        for cloud in self.clouds:
            cloud.display()

class Dino:
    def __init__(self):
        self.images = [
            pg.transform.scale(pg.image.load("images/d1.png"), (screen_width // 12, screen_width // 12)),
            pg.transform.scale(pg.image.load("images/d2.png"), (screen_width // 12, screen_width // 12))
        ]

        self.image = self.images[0]
        self.time_stamp = 0

        self.x = 50
        self.y = screen_height - 150

        self.vel = -5
        self.grav = 1

    def display(self):
        if self.time_stamp % 3 == 0:
            self.image = self.images[1]
        else:
            self.image = self.images[0]

        screen.blit(self.image, (self.x, self.y))
        self.time_stamp += 1

    def jump(self):
        if self.y == screen_height - 150:
            self.grav = 1
            self.y += self.vel
            self.vel += self.grav
        else:
            self.grav = 0


class Cactus:
    pass

class Bird:
    pass

class GameEnv:
    pass

def eval_genomes():
    pass

def main():
    pass

dino = Dino()
bg = Background()

while True:
    screen.fill(WHITE)

    dino.display()
    dino.jump()
    bg.display()

    pg.display.update()
    fps_clock.tick(fps)

if __name__ == "__main__":
    main()

pg.quit()
