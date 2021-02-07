import random
import pygame as pg
from pygame.color import THECOLORS as colors

from neatpy.population import Population
from neatpy.options import Options
from neatpy.draw import draw_brain_pygame
from neatpy.save import save_brain

pg.init()
pg.font.init()

speed = 10
fps = 25
running = True

height, width = 600, 400
screen = pg.display.set_mode((width, height))
fps_clock = pg.time.Clock()

def load_image(file_name, width=None, height=None):
    if width is None or height is None:
        return pg.image.load(f'images/{file_name}.gif')
    else:
        return pg.transform.scale(pg.image.load(f'images/{file_name}.gif'), (width, height))

class Ground:
    img = load_image('ground', width, 100)
    grounds = [0]

    @staticmethod
    def show(speed):
        if Ground.grounds[-1] <= 0:
            Ground.grounds.append(Ground.grounds[-1] + width)

        if Ground.grounds[0] < -width:
            Ground.grounds = Ground.grounds[1:]

        for i in range(len(Ground.grounds)):
            screen.blit(Ground.img, (Ground.grounds[i], height - 100))
            Ground.grounds[i] -= speed

class Bg:
    img = load_image('bg', width, height - 100)
    bgs = [0]

    @staticmethod
    def show(speed):
        if Bg.bgs[-1] <= 0:
            Bg.bgs.append(Bg.bgs[-1] + width)

        if Bg.bgs[0] < -width:
            Bg.bgs = Bg.bgs[1:]

        for i in range(len(Bg.bgs)):
            screen.blit(Bg.img, (int(Bg.bgs[i]), 0))
            Bg.bgs[i] -= speed

class Pipe:
    def __init__(self):
        self.dim = 100, 800
        self.pipet = load_image('pipet', *self.dim)
        self.pipeb = load_image('pipeb', *self.dim)

        self.gap = 175

        self.x = width
        self.y = random.randrange(height - 100 - self.gap)

        self.rectt = None
        self.rectb = None

    def show(self):
        self.rectt = screen.blit(self.pipet, (self.x, self.y - self.dim[1]))
        self.rectb = screen.blit(self.pipeb, (self.x, self.y + self.gap))

        self.x -= speed

    def next_pipe(self):
        return self.x < width / 4

class Bird:
    def __init__(self, brain):
        self.img = load_image('bird', 45, 45)
        self.rect = None
        
        self.y = 300
        self.y_vel = 0
        self.g = 3

        self.rotation = 40

        self.brain = brain
        self.brain.fitness = 0

    def rotate_img(self, image, angle, x, y):
        rotated_image = pg.transform.rotate(image, angle)
        self.rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

        return rotated_image
 
    def show(self):
        self.brain.fitness += 1

        img = self.rotate_img(self.img, self.rotation, 100, self.y)
        screen.blit(img, self.rect)

        self.y += self.y_vel
        self.y_vel += self.g

        self.rotation = max(-self.y_vel * 4, -80)

    def jump(self):
        self.y_vel = -15

    def think(self, pipe):
        inputs = [
            self.y,
            pipe.y,
            pipe.y + pipe.gap,
            self.y_vel,
            pipe.x
        ]

        if self.brain.predict(inputs)[0] > 0.5:
            self.jump()

    def death(self, pipe):
        return (
            self.rect.colliderect(pipe.rectt) or
            self.rect.colliderect(pipe.rectb) or
            self.y > height - 100 or
            self.y < 0
        )

pipes = [Pipe()]
font = pg.font.Font('freesansbold.ttf', 32)

Options.set_options(5, 1, 500)
p = Population()
gen = 1
score = 0
high_score = 0
birds = [Bird(brain) for brain in p.pool]

def get_cur_pipe():
    for pipe in pipes:
        if not (pipe.x + pipe.dim[0] <= 100):
            return pipe

while running:
    screen.fill(colors['black'])

    Bg.show(speed/10)
    for pipe in pipes:
        pipe.show()

    if pipes[-1].next_pipe(): pipes.append(Pipe())
    if pipes[0].x < -pipes[0].dim[0]:
        pipes = pipes[1:]
        score += 1

        high_score = max(high_score, score)

    Ground.show(speed)

    to_remove = []
    pipe = get_cur_pipe()

    for bird in birds:
        bird.show()
        bird.think(pipe)

        if bird.death(pipe):
            to_remove.append(bird)

    for rem in to_remove:
        birds.remove(rem)

    if len(birds) == 0:
        p.epoch()
        birds = [Bird(brain) for brain in p.pool]
        pipes = [Pipe()]

        gen += 1
        score = 0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            save_brain(p.best, 'bird.json')
            running = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                fps *= 2
            elif event.key == pg.K_DOWN:
                fps /= 2

    draw_brain_pygame(screen, p.best, 150, 10, 100, circle_size=8)

    screen.blit(font.render(f"High Score: {high_score}", True, colors['white']), (10, height - 130))
    screen.blit(font.render(f"Generation: {gen}", True, colors['white']), (10, height - 100))
    screen.blit(font.render(f"Score: {score}", True, colors['white']), (10, height - 70))
    screen.blit(font.render(f"Birds Alive: {len(birds)}", True, colors['white']), (10, height - 40))

    pg.display.update()
    fps_clock.tick(fps)

pg.quit()