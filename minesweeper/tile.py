from collections import deque


class Tile:
    """A tile in a game of minesweeper."""
    
    def __init__(self, row, column, neighbours, is_safe=True, number=0):
        self.row = row
        self.column = column
        self.neighbours = neighbours
        self.is_clicked = False
        self.is_safe = is_safe
        self.marks = deque(('none', 'flag', 'question'))
        self.mark = self.marks[0]
        self.number = number
    
    def __str__(self):
        return f'Tile, {"safe" if self.is_safe else "bomb"}, {"clicked" if self.is_clicked else "not clicked"}'
    
    def __repr__(self):
        return 'safe' if self.is_safe else 'bomb'
    
    def change_mark(self):
        self.marks.rotate(-1)
        self.mark = self.marks[0]
    
    def reset_mark(self):
        self.marks = deque(('none', 'flag', 'question'))
        self.mark = self.marks[0]
