# Minesweeper
#### A 2x scale replica of the original Windows Minesweeper.
Made using python and Tkinter, the GUI, sprites and sounds match the original game exactly.

Resources from the original game were extracted using a program called ResourcesExtract.

Sounds are handled by pygame.

Minesweeper will run no worries on python >= 3.6, I haven't tested with versions below this, 
but given that Pillow >= 8.0 only supports >= 3.6, that's what I'm gonna go with.

**NOTE:** To run the game, you will need the following python modules installed:
- Pygame
- Python Imaging Library (PIL)
- Tkinter (installed by default)
- Webbrowser (installed by default)
- OS (installed by default)

So you may have to do this:

`pip install pygame`

`pip install Pillow`

If you're going to download this repository to import into you're own code, simply download the minesweeper folder (not root folder Minesweeper).

If you just want to play the game, download the entire repository and start the game using run.py

Files:
- __minesweeper/\_\_init\_\_.py__ - makes importing stuff easier: `from minesweeper import MinesweeperApp`
- __minesweeper/best_times.csv__ - stores fastest completion times/names for beginner, intermediate, and expert levels.
- __minesweeper/core.py - core__ Minesweeper game functionality. Keeps track of tiles, bombs, numbers, clicking and marking tiles, resetting game, winning and losing.
- __minesweeper/dialogs.py__ - custom Tkinter dialog boxes for custom difficulty, best times, player name, etc.
- __minesweeper/icon.ico__ - minesweeper icon.
- __minesweeper/main.py__ - Tkinter-based GUI Application that controls core game.
- __minesweeper/tile.py__ - Tile class, used by core game to store information of a tile, such as number, mark, and whether or not the tile is safe.
- __run.py__ - imports and runs MinesweeperApp class from minesweeper/main.py, making playing the game easier and faster.

> _Too many mines, not enough sweepers. - Caleb Webster_
