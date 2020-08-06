import pygame as pg
import neat
import random

grid_size = 10
bombs = 10

class Tile:
    def __init__(self):
        self.bomb = False

    def bombize(self):
        self.bomb = True

class Board:
    def __init__(self):
        self.board = [Tile() for _ in range(grid_size ** 2)]
        self.bombize()

    def bombize(self):
        tiles = random.sample(self.board, bombs)
        
        for tile in tiles:
            tile.bombize()

class Player:
    def __init__(self, genome, config):
        genome.fitness = 0

        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome

    def select_tile(self, tile, board):
        pass

    def think(self, board):
        pass


class GameEnv:
    def __init__(self):
        self.players = []
        self.board = Board()
        self.boards
    
    def add_player(self):
        self.players.append(Player())
        self.boards.append(self.board)

    def human_play(self):
        pass

env = GameEnv()
    
