import pygame as pg
import neat
import random

pg.init()

grid_size = 10
bombs = 10
block_size = 50
margin = 20 

def map_values(n, start1, stop1, start2, stop2):
    return ((n - start1) / (stop1 - start1)) * (stop2 - start2) + start2

'''
    0 - empty
    1, 2, 3, 4, 5, 6, 7, 8 - bombs number
    9 - bomb
    10 - not revealed
'''

side = (block_size * grid_size) + (2 * margin)
screen = pg.display.set_mode((side, side))

font = pg.font.Font('freesansbold.ttf', 32)

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.is_bomb = False
        self.revealed = False

        self.val = 0
        self.adj_tiles = []

        self.rect = None

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

    def display(self):
        x = margin + (self.x * block_size)
        y = margin + (self.y * block_size)

        if not self.revealed:
            color = (255, 255, 0)
        else:
            if not self.is_bomb:
                color = (0, 255, 255)
            else:
                color = (0, 0, 0)        

        self.rect = pg.draw.rect(screen, color, (x, y, block_size, block_size))
        pg.draw.rect(screen, (255, 0, 0), (x, y, block_size, block_size), 2)

        if self.revealed and self.val != 0:
            screen.blit(font.render(f"{self.get_value()}", True, (255, 255, 255)), (x + block_size // 3, y + block_size // 3))

    def all_empty(self, lst):
        n = 0
        for l in lst:
            if l.val == 0:
                n += 1

        return n == len(lst)

    def reveal_adjacent(self):
        self.revealed = True

        tiles = [self]
        # tiles = self.adj_tiles

        while True:
            new_tiles = []

            for tile in tiles:
                for adj in tile.adj_tiles:
                    adj.revealed = True
                    pg.display.update()

            tiles = new_tiles

            if tiles == []:
                break  


    def check_click(self, mouse_x, mouse_y):
        if self.rect.collidepoint(mouse_x, mouse_y):
            if not self.val != 0:
                self.reveal_adjacent()
            else:
                self.revealed = True

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

    def display(self):
        for tile in self.board_flat:
            tile.display()

    def check_click(self, pos):
        mouse_x, mouse_y = pos
        for tile in self.board_flat:
            tile.check_click(mouse_x, mouse_y)

board = Board()

while True:
    board.display()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()

        if event.type == pg.MOUSEBUTTONDOWN:
            board.check_click(pg.mouse.get_pos())

    pg.display.update()



