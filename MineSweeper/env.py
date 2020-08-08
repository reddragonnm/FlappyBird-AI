import pygame as pg
import neat
import random
import time

pg.init()

grid_size = 25
bombs = 100
block_size = 15
margin = 20

fps = 20
fps_clock = pg.time.Clock()

is_bomb_color = 0, 0, 0
not_bomb_color = 0, 255, 255
not_revealed_color = 255, 255, 0

'''
    0 - empty
    1, 2, 3, 4, 5, 6, 7, 8 - bombs number
    9 - bomb
    10 - not revealed
'''

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.color = [random.randint(0, 255) for _ in range(3)]

        self.is_bomb = False
        self.revealed = False

        self.val = 0
        self.adj_tiles = []

    def make_bomb(self):
        self.is_bomb = True
        self.adj_bombs = None

    def get_adjacent_bombs(self, board):
        if self.is_bomb:
            self.val = 9
            self.adj_tiles = None

            return

        x = self.x
        y = self.y

        indexes = [
            (x - 1, y - 1),
            (x, y - 1),
            (x + 1, y - 1),
            (x - 1, y),
            (x + 1, y),
            (x - 1, y + 1),
            (x, y + 1),
            (x + 1, y + 1)
        ]

        for index in indexes:
            try:
                if index[0] >= 0 and index[1] >= 0:
                    tile = board[index[0]][index[1]]

                    if tile.is_bomb:
                        self.val += 1
                    else:
                        self.adj_tiles.append(tile)

            except IndexError:
                pass

    def get_value(self):
        if self.revealed:
            return self.val
        else:
            return 10

    def display(self, screen):
        x = margin + (self.x * block_size)
        y = margin + (self.y * block_size)

        if not self.revealed:
            color = not_revealed_color
        else:
            if not self.is_bomb:
                color = not_bomb_color
            else:
                color = is_bomb_color

        pg.draw.rect(screen, color, (x, y, block_size, block_size))
        pg.draw.rect(screen, (255, 0, 0), (x, y, block_size, block_size), 2)

        # if self.revealed and self.val != 0:
        #     screen.blit(font.render(f"{self.get_value()}", True, self.color, (x + block_size // 3, y + block_size // 3)))

    def filter_lst(self, lst):
        filtered = []

        for tile in lst:
            if not tile.revealed:
                filtered.append(tile)

        return filtered

    def reveal_adjacent(self):
        tiles = [self]

        while True:
            new_tiles = []

            for tile in tiles:
                for adj in self.filter_lst(tile.adj_tiles):
                    adj.revealed = True

                    if adj.val == 0:
                        new_tiles.append(adj)

            tiles = new_tiles

            if tiles == []:
                break


    def click(self):
        self.revealed = True
        if self.val == 0:
            self.reveal_adjacent()

class Board:
    def __init__(self):
        self.board = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.board_flat = []

        self.fill_board()

        # side = (block_size * grid_size) + (2 * marign)
        # self.screen = pg.display.set_mode((side, side))

    def fill_board(self):
        for i in range(grid_size):
            for j in range(grid_size):
                tile = Tile(i, j)
                self.board[i][j] = tile
                self.board_flat.append(tile)

        bomb_tiles = random.sample(self.board_flat, bombs)

        for tile in bomb_tiles:
            tile.make_bomb()

        for all_tile in self.board_flat:
            all_tile.get_adjacent_bombs(self.board)

        print(len(self.board_flat))

    def display(self, screen):
        for tile in self.board_flat:
            tile.display(screen)

    def click(self, index):
        tile = self.board_flat[index % grid_size ** 2]
        tile.click()

        if tile.is_bomb:
            return -10, True
        else:
            if not tile.revealed:
                return 3, False
            else:
                return -5, True

    def get_board_info(self):
        lst = []

        for tile in self.board_flat:
            lst.append(tile.get_value())

        return lst

class Player:
    def __init__(self, genome, config, board):
        self.board = board
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)

        genome.fitness = 0
        self.genome = genome

        self.dead = False

    def think(self):
        output = self.net.activate(self.board.get_board_info())
        print(output)
        # output = int(output[0] * grid_size ** 2) - 1
        output = int((output[0] * grid_size ** 2)  / 100) - 1

        # print("click", output, self.genome.fitness)
        reward, self.dead = self.board.click(output)
        self.genome.fitness += reward

    def map_values(self, n, start1, stop1, start2, stop2):
        return int(((n - start1) / (stop1 - start1)) * (stop2 - start2) + start2)

    def display(self, screen):
        self.board.display(screen)

class Env:
    def __init__(self):
        self.players = []
        self.board = Board()

        self.score = 0
        self.generation = 0

    def add_player(self, genome, config):
        self.players.append(Player(genome, config, self.board))

    def display_one(self, screen):
        try:
            player = self.players[0]
            player.display(screen)
        except IndexError:
            pass

    def check_removal(self):
        to_remove = []

        for player in self.players:
            if player.dead:
                to_remove.append(player)

        for rem in to_remove:
            self.players.remove(rem)

    def reset(self):
        self.players = []
        self.board = Board()

        self.score = 0
        self.generation = 0

    def all_dead(self):
        # print("Check all dead", len(self.players) == 0)
        return len(self.players) == 0

    def think_all(self):
        for player in self.players:
            player.think()

env = Env()

side = (block_size * grid_size) + (2 * margin)
screen = pg.display.set_mode((side, side))

font = pg.font.Font('freesansbold.ttf', 32)

def eval_genomes(genomes, config):

    for genome_id, genome in genomes:
        env.add_player(genome, config)

    while True:
        screen.fill((0, 0, 255))

        # print("Hello")
        env.check_removal()
        env.display_one(screen)
        env.think_all()

        if env.all_dead():
            env.reset()
            break

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

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
    print(f"Best genome:\n {winner}")

if __name__ == "__main__":
    main()

pg.quit()
