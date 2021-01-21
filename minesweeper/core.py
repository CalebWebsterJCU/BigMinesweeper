from minesweeper.tile import Tile
import random
from string import ascii_letters as letters


def _prev(lst, idx):
    return lst[lst.index(idx) - 1]


def _next(lst, idx):
    return lst[lst.index(idx) + 1]


class MineSweeper:
    """Minesweeper."""
    
    def __init__(self):
        self.tiles = {}
        self.num_bombs = 0
        self.time = 0
        self.unmarked_bombs = 0
        self.rows = {}
        self.columns = {}
        self.sorted_letters = sorted(letters)
    
    def tick(self):
        if self.time < 999:
            self.time += 1
    
    def setup(self, rows, columns, bombs=0, scatter_now=False):
        self.rows = {x: str(x + 1) for x in range(rows)}  # {0: '1', 1: '2', 2: '3'}
        self.columns = {x: self.sorted_letters[x] for x in range(columns)}  # {0: 'a', 1: 'b', 2: 'c'}
        self.num_bombs = bombs
        if self.num_bombs > (rows * columns) - 1:
            self.num_bombs = (rows * columns) - 1
        self.unmarked_bombs = bombs
        self.tiles.clear()
        self.time = 0
        # Create tiles
        for row in self.rows.values():  # ['a', 'b', 'c', 'd', 'e']
            for column in self.columns.values():  # ['1', '2', '3', '4', '5']
                neighbours = self.get_neighbours(row, column)
                tile = Tile(row=row, column=column, neighbours=neighbours)
                self.tiles[column + row] = tile
        # If specified, scatter bombs right away
        if scatter_now:
            self.scatter_bombs()
    
    def reset(self, scatter_now=False):
        self.time = 0
        self.unmarked_bombs = self.num_bombs
        for tile in self.tiles.values():
            tile.is_clicked = False
            tile.number = 0
            tile.is_safe = True
            tile.reset_mark()
        if scatter_now:
            self.scatter_bombs()
    
    def scatter_bombs(self, tile_to_avoid=None):
        """Choose a number of random safe tiles and make them bombs."""
        for x in range(self.num_bombs):
            # Choose a random safe tile
            rand_tile = random.choice(list(self.tiles.values()))
            while not rand_tile.is_safe or rand_tile == tile_to_avoid:
                rand_tile = random.choice(list(self.tiles.values()))
            
            rand_tile.is_safe = False
        
        self.set_tile_nums()
    
    def get_neighbours(self, r, c):
        
        rows = sorted(list(self.rows.values()), key=int)
        cols = sorted(list(self.columns.values()))
        
        neighbours = {}
        
        if r != rows[0] and c != cols[0]:
            neighbours['top-left'] = _prev(cols, c) + _prev(rows, r)
        if r != rows[0]:
            neighbours['top'] = c + _prev(rows, r)
        if r != rows[0] and c != cols[-1]:
            neighbours['top-right'] = _next(cols, c) + _prev(rows, r)
        if r != rows[-1] and c != cols[0]:
            neighbours['bottom-left'] = _prev(cols, c) + _next(rows, r)
        if r != rows[-1]:
            neighbours['bottom'] = c + _next(rows, r)
        if r != rows[-1] and c != cols[-1]:
            neighbours['bottom-right'] = _next(cols, c) + _next(rows, r)
        if c != cols[0]:
            neighbours['left'] = _prev(cols, c) + r
        if c != cols[-1]:
            neighbours['right'] = _next(cols, c) + r
        return neighbours
    
    def get_adjacent_tiles(self, tile):
        return [self.tiles[c] for c in tile.neighbours.values()]
    
    def set_tile_nums(self):
        for tile in self.tiles.values():
            for adjacent_tile in self.get_adjacent_tiles(tile):
                if not adjacent_tile.is_safe:
                    tile.number += 1
    
    def click_tile(self, tile):
        if not tile.is_clicked:
            if tile.mark != 'flag':
                tile.is_clicked = True
                if tile.number == 0 and tile.is_safe:
                    adjacent_tiles = self.get_adjacent_tiles(tile)
                    for adjacent_tile in [t for t in adjacent_tiles if not t.is_clicked]:
                        self.click_tile(adjacent_tile)
                    return True
        return False
    
    def mark_tile(self, tile):
        if not tile.is_clicked:
            if tile.mark == 'flag':
                self.unmarked_bombs += 1
            tile.change_mark()
            if tile.mark == 'flag':
                self.unmarked_bombs -= 1
    
    def click_all_bombs(self):
        for tile in self.tiles.values():
            if not tile.is_safe:
                self.click_tile(tile)
    
    def game_is_won(self):
        for tile in self.tiles.values():
            if tile.is_safe and not tile.is_clicked:
                return False
        return True
    
    def game_is_lost(self):
        for tile in self.tiles.values():
            if not tile.is_safe and tile.is_clicked:
                return True
        return False
    
    def game_is_over(self):
        return self.game_is_won() or self.game_is_lost()
    
    def print_board_to_console(self):
        for index, tile in enumerate(self.tiles):
            if tile.is_clicked:
                print('c', end=' ')
            elif tile.is_safe:
                print(tile.number, end=' ')
            else:
                print('b', end=' ')
            # else:
            #     print('?', end='')
            if (index + 1) % len(self.columns) == 0:
                print()
