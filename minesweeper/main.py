"""
Minesweeper App
2021
This module contains the main code for MinesweeperApp, A 2x scale
replica of the original Windows Minesweeper, run in a TKinter window
with images and sounds extracted from the original game.

`Github <https://www.github.com/CalebWebsterJCU/Minesweeper>`_

Examples:
    Running MinesweeperApp using run.py::

        $ cd Minesweeper
        $ python run.py

    Importing class from package minesweeper::

        from minesweeper import MinesweeperApp

        MinesweeperApp().run()

Attributes:
    DEFAULT_LEVEL (str): Default game starting difficulty

    BEST_TIMES_FILE (str): Name of tile which stores best times

    HELP_LINK (str): Link to Minesweeper help page

"""

from minesweeper.core import MineSweeper
from pygame.mixer import Channel, Sound
from webbrowser import open as webbopen
from PIL import ImageTk, Image as Img
from minesweeper import dialogs
from tkinter import *
import pygame
import json

DEFAULT_LEVEL = 'expert'
BEST_TIMES_FILE = 'minesweeper/best_times.csv'
SETTINGS_FILE = 'minesweeper/settings.json'
HELP_LINK = 'https://www.instructables.com/How-to-play-minesweeper'


class MinesweeperApp:
    """
    a class to store methods, images, and sounds for Minesweeper game.
    
    Instance Attributes:
        game : Minesweeper object
            core game object to manage back end functions
        images : dict
            stores loaded image (.png) files
        widgets : dict
            stores Tkinter widgets, mapping names to objects
        menu_vars : dict
            stores statuses of top menu checkboxes
        is_frozen : bool
            whether or not the game is frozen
        first_btn_clicked : bool
            whether or not the first tile button has been clicked
        difficulty_levels : dict
            stores rows, columns, and bombs for different difficulties
        current_difficulty_level : str
            the game's current difficulty level
        best_times : dict
            stores fastest time and name for each difficulty level
        sounds : dict
            stores loaded sound (.wav) files
        channels : dict
            stores sound channels, one for each sound
        root : Tk object
            base Tkinter window on which to build GUI
    
    Methods:
        read_best_times(filename):
            Read best times from file and return a dict.
        write_best_times(filename, best_times):
            Write best times to a file
        sound_is_on(self):
            Return true if game sound is on, otherwise return false.
        q_marks_are_on(self):
            Return true if "?" marks are on, otherwise return false.
        colour_is_on(self):
            Return true if colour is on, otherwise return false.
        start_game(self):
            Initialize game, setting difficulty level to default.
        run(self):
            Start the Tkinter GUI.
        create_ui(self, remove=False):
            Create the main GUI widgets.
        create_menu(self):
            Create the Tkinter window menu.
        create_buttons(self, remove=False):
            Create tile button for each tile in core game.
        handle_key_press(self, event):
            Handle key presses.
        assemble_number_images(self, num):
            Turn an integer string into a list of number images.
        update_unmarked_bombs(self):
            Update unmarked bombs counter with number from core game.
        update_time(self):
            Update time counter with number from core game.
        change_difficulty(self, difficulty):
            Change difficulty level of core game.
        set_custom_difficulty(self):
            Get rows, columns, and bombs from custom difficulty dialog.
        show_best_times(self):
            Open best times dialog.
        show_best_times(self):
            Open best times dialog.
        exit(self):
            Write best times to file and quit game.
        open_help():
            Open help link in browser.
        open_about_game(self):
            Open about game dialog.
        tick(self):
            Advance game time.
        l_hold(self, event):
            Trigger surprised face upon holding down LMB.
        l_release(self, event):
            Trigger up face button upon releasing LMB.
        face_button_l_hold(self, event):
            Trigger down face upon holding down LMB on face button.
        face_button_l_release(self, event):
            Reset game upon releasing LMB on face button.
        button_l_hold(self, event):
            Trigger down tile upon holding LMB on tile button.
        button_l_release(self, event):
            Click tile upon releasing LMB on tile button.
        button_r_click(self, event):
            Mark tile upon clicking RMB on tile button.
        click_button(self, button):
            Click a tile button, update its image and handle win/loss.
        freeze(self):
            Freeze the game, disabling all buttons and stopping time.
        unfreeze(self):
            Unfreeze game, re-enabling all buttons.
        auto_click_buttons(self, red=None, all_bombs=False):
            Update all buttons whose tiles were clicked automatically.
        mark_button(self, button):
            Mark a tile, alternating between flag, question, and none.
        reset_game(self):
            Reset core game and GUI buttons.
        toggle_colour(self):
            Switch between colour and black-and-white images.
        toggle_q_marks(self):
            Clear all tiles marked with "?".
        load_images(self, colour):
            Load all images, creating and storing Tk PhotoImage objects.
        
    """
    
    def __init__(self):
        """Initialize core game, load resources, create tkinter GUI."""
        # Setup Minesweeper Core
        self.game = MineSweeper()
        self.images = {}
        self.widgets = {}
        self.menu_vars = {}
        self.is_frozen = False
        self.first_btn_clicked = False
        self.difficulty_levels = {
            'beginner': {'rows': 9, 'columns': 9, 'bombs': 10},
            'intermediate': {'rows': 16, 'columns': 16, 'bombs': 40},
            'expert': {'rows': 16, 'columns': 30, 'bombs': 99},
            'custom': {'rows': 10, 'columns': 10, 'bombs': 10}
        }
        self.current_difficulty_level = None
        self.stored_settings = self.load_settings(SETTINGS_FILE)
        self.best_times = self.read_best_times(BEST_TIMES_FILE)
        # Load Sounds
        pygame.init()
        self.sounds = {
            'bomb': Sound('minesweeper/sounds/bomb.wav'),
            'clock': Sound('minesweeper/sounds/clock.wav'),
            'win': Sound('minesweeper/sounds/win.wav')
        }
        self.channels = {0: Channel(0), 1: Channel(1), 2: Channel(2)}
        # Initialize Tkinter Window
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.root.resizable(False, False)
        self.root.iconbitmap('minesweeper/icon.ico')
        self.root.title('Minesweeper')
        self.create_menu()
        self.load_images(colour=self.colour_is_on())
        self.create_ui()
        # Start game with default settings
        self.start_game()
    
    @staticmethod
    def load_settings(filename):
        """
        Read saved settings from json file and return a dict.
        
        :param str filename: filename to read settings from
        :return: settings
        :rtype: dict
        """
        with open(filename, 'r') as file_in:
            settings = json.loads(file_in.read().strip())
        return settings
    
    def save_game_settings(self, filename):
        """
        Write current game settings to json file.
        
        :param filename: file to write settings to
        """
        settings = {
            'level': self.current_difficulty_level,
            'rows': len(self.game.rows),
            'columns': len(self.game.columns),
            'bombs': self.game.num_bombs,
            'marks': self.menu_vars['marks'].get(),
            'colour': self.menu_vars['colour'].get(),
            'sound': self.menu_vars['sound'].get()
        }

        with open(filename, 'w') as file_out:
            file_out.write(json.dumps(settings) + '\n')
    
    @staticmethod
    def read_best_times(filename):
        """
        Read best times from file and return a dict.
        
        :param str filename: filename to read best times from
        :return: best times
        :rtype: dict
        
        Best times file must be in format:
        beginner,name,time
        intermediate,name,time
        expert,name,time
        
        Dict returned is in format:
        {
            "beginner": (time, name)
            "intermediate": (time, name)
            "expert": (time, name)
        }
        """
        best_times = {}
        with open(filename, 'r') as file_in:
            for line in file_in:
                parts = line.strip().split(',')
                level = parts[0]
                time = int(parts[1])
                name = parts[2]
                best_times[level] = (time, name)
        return best_times
    
    @staticmethod
    def write_best_times(filename, best_times):
        """
        Write best times to a file.
        
        :param str filename: file to write best times to
        :param dict best_times: best times to write
        
        Best times will be written in format:
        beginner,name,time
        intermediate,name,time
        expert,name,time
        """
        with open(filename, 'w') as file_out:
            for level, (time, name) in best_times.items():
                file_out.write(f'{level},{time},{name}\n')
    
    def sound_is_on(self):
        """Return true if game sound is on, otherwise return false."""
        return self.menu_vars['sound'].get() == 1
    
    def q_marks_are_on(self):
        """Return true if "?" marks are on, otherwise return false."""
        return self.menu_vars['marks'].get() == 1
    
    def colour_is_on(self):
        """Return true if colour is on, otherwise return false."""
        return self.menu_vars['colour'].get() == 1
        
    def start_game(self):
        """Initialize game with difficulty level from saved settings."""
        if self.stored_settings['level'] == 'custom':
            # Configure custom difficulty level.
            rows = self.stored_settings['rows']
            columns = self.stored_settings['columns']
            bombs = self.stored_settings['bombs']
            self.difficulty_levels['custom']['rows'] = rows
            self.difficulty_levels['custom']['columns'] = columns
            self.difficulty_levels['custom']['bombs'] = bombs
        self.change_difficulty(self.stored_settings['level'])
    
    def run(self):
        """Start the Tkinter GUI."""
        self.root.mainloop()
    
    def create_ui(self, remove=False):
        """
        Create the main GUI widgets.
        
        :param bool remove: whether or not to remove widgets before creating
        
        Step 1. Create the widget objects
        Step 2. Pack them to the screen
        Step 3. Bind press and release events
        Step 4. Add them to self.widgets
        Step 5. Global bindings
        """
        remove_buttons = False
        if remove:
            remove_buttons = True
            self.widgets['main_container'].pack_forget()
            
        main_container = LabelFrame(self.root, bd=0, bg='#c0c0c0')
        top_frame = LabelFrame(main_container, bd=6, relief=SUNKEN, bg='#c0c0c0')
        # Unmarked bombs
        unmarked_bombs = LabelFrame(top_frame, bd=3, relief=SUNKEN)
        for x in range(3):
            Label(unmarked_bombs, image=self.images['clock_0'], bd=0).grid(row=0, column=x)
        # Face button
        if self.is_frozen:
            if self.game.game_is_won():
                face_img = self.images['face_win']
            else:
                face_img = self.images['face_loss']
        else:
            face_img = self.images['face_up']
        face_button = Label(top_frame, bd=0, image=face_img, bg='#c0c0c0')
        # Time
        time = LabelFrame(top_frame, bd=3, relief=SUNKEN)
        for x in range(3):
            Label(time, image=self.images['clock_0'], bd=0).grid(row=0, column=x)
        
        bottom_frame = LabelFrame(main_container, bd=6, relief=SUNKEN, bg='#c0c0c0')
        # Pack widgets to the screen.
        main_container.pack(expand=True, fill=BOTH)
        top_frame.pack(expand=True, fill=BOTH, padx=15, pady=(15, 0))
        unmarked_bombs.pack(side=LEFT, padx=(10, 0), pady=10)
        face_button.pack(side=LEFT, expand=True, padx=2, pady=10)
        time.pack(side=RIGHT, padx=(0, 10), pady=10)
        bottom_frame.pack(expand=True, fill=BOTH, padx=15, pady=15)
        # Bindings for face button.
        face_button.bind('<ButtonPress-1>', self.face_button_l_hold)
        face_button.bind('<ButtonRelease-1>', self.face_button_l_release)
        # Add widgets to self.widgets
        self.widgets['main_container'] = main_container
        self.widgets['top_frame'] = top_frame
        self.widgets['unmarked_bombs'] = unmarked_bombs
        self.widgets['time'] = time
        self.widgets['face_button'] = face_button
        self.widgets['bottom_frame'] = bottom_frame
        # Create tile buttons, removing if necessary, then click buttons
        # (needed when colors have been changed during a game), then
        # update unmarked bombs and time.
        self.create_buttons(remove=remove_buttons)
        self.auto_click_buttons(all_bombs=self.game.game_is_lost())
        self.update_unmarked_bombs()
        self.update_time()
        # Global bindings
        self.root.bind_all('<ButtonPress-1>', self.l_hold)
        self.root.bind_all('<ButtonRelease-1>', self.l_release)
        self.root.bind_all("<Key>", self.handle_key_press)
        self.root.bind_all("<Escape>", lambda event: self.exit())

        self.update_time()
    
    def create_menu(self):
        """
        Create the Tkinter window menu.
        
        Layout: Game | Help
        Defaults:
            ? Marks -> ON
            Colour -> ON
            Sound -> OFF
        """
        # Top menu
        main_menu = Menu(self.root)
        self.root.configure(menu=main_menu)
        # Menu button: Game
        game_menu = Menu(main_menu, tearoff=False)
        main_menu.add_cascade(label='Game', menu=game_menu)
        game_menu.add_command(label=f'New {"F2":>30}', command=self.reset_game)
        game_menu.add_separator()
        # Difficulty level variables
        b = IntVar()
        i = IntVar()
        e = IntVar()
        c = IntVar()
        game_menu.add_checkbutton(label='Beginner', variable=b, command=lambda: self.change_difficulty('beginner'))
        game_menu.add_checkbutton(label='Intermediate', variable=i, command=lambda: self.change_difficulty('intermediate'))
        game_menu.add_checkbutton(label='Expert', variable=e, command=lambda: self.change_difficulty('expert'))
        game_menu.add_checkbutton(label='Custom...', variable=c, command=self.set_custom_difficulty)
        game_menu.add_separator()
        # Marks, colour and sound variables
        m = IntVar()
        cl = IntVar()
        s = IntVar()
        m.set(self.stored_settings['marks'])
        cl.set(self.stored_settings['colour'])
        s.set(self.stored_settings['sound'])
        game_menu.add_checkbutton(label='Marks (?)', variable=m, command=self.toggle_q_marks)
        game_menu.add_checkbutton(label='Color', variable=cl, command=self.toggle_colour)
        game_menu.add_checkbutton(label='Sound', variable=s)
        game_menu.add_separator()
        game_menu.add_command(label=f'Best Times... {"F3":>16}', command=self.show_best_times)
        game_menu.add_separator()
        game_menu.add_command(label='Exit', command=self.exit)
        # Menu button: Help
        help_menu = Menu(main_menu, tearoff=False)
        main_menu.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label=f'Contents {"F1":>35}')
        help_menu.add_command(label='Search for Help on...')
        help_menu.add_command(label='Using Help')
        help_menu.add_separator()
        help_menu.add_command(label=f'About Minesweeper... {"F4":>12}', command=self.open_about_game)
        # Store variables for global access.
        self.menu_vars = {
            'levels': {
                'beginner': b,
                'intermediate': i,
                'expert': e,
                'custom': c,
            },
            'marks': m,
            'colour': cl,
            'sound': s,
        }
    
    def create_buttons(self, remove=False):
        """
        Create tile button for each tile in core game.
        
        :param bool remove: if true, remove all buttons before creating.
        """
        if remove:
            for button in self.widgets['buttons']:
                button.grid_forget()
                
        self.widgets['buttons'] = []
        
        button_container = self.widgets['bottom_frame']
        column = 0
        row = 0
        
        for tile in self.game.tiles.values():
            
            button = Label(button_container, bd=0, image=self.images[f'tile_{tile.mark}'])
            self.widgets['buttons'].append(button)
            
            button.tile = tile
            button.is_disabled = False
            
            button.bind('<ButtonPress-1>', self.button_l_hold)
            button.bind('<ButtonRelease-1>', self.button_l_release)
            button.bind('<Button-3>', self.button_r_click)
            
            button.grid(row=row, column=column)
            
            column += 1
            if column % len(self.game.columns) == 0:
                column = 0
                row += 1
    
    def handle_key_press(self, event):
        """Handle key presses."""
        k = event.keysym
        if k == 'F2':
            self.reset_game()
        elif k == 'F1':
            self.open_help()
        elif k == 'F3':
            self.show_best_times()
    
    def assemble_number_images(self, num):
        """
        Turn an integer string into a list of number images.
        
        :param int num: number to convert into images.
        
        The time and unmarked bombs labels do not use text to display number,
        rather a series of images of numbers. To determine which number images
        to use and in what order, the num parameter is first zero-filled
        (3 -> "003"), then an image is chosen for each character.
        "0" -> clock_0.png
        "0" -> clock_0.png
        "3" -> clock_3.png
        E.G. num=-1 -> "0-1" -> [clock_0, clock_-, clock_1]
        """
        return [self.images[f'clock_{char}'] for char in f'{num:03}']
    
    def update_unmarked_bombs(self):
        """Update unmarked bombs counter with number from core game."""
        unmarked_bombs = self.widgets['unmarked_bombs']
        image_labels = list(unmarked_bombs.children.values())
        image_list = self.assemble_number_images(self.game.unmarked_bombs)
        for x in range(3):
            image_labels[x].configure(image=image_list[x])
    
    def update_time(self):
        """Update time counter with number from core game."""
        time = self.widgets['time']
        image_labels = list(time.children.values())
        image_list = self.assemble_number_images(self.game.time)
        for x in range(3):
            image_labels[x].configure(image=image_list[x])
    
    def change_difficulty(self, difficulty):
        """
        Change difficulty level of core game.
        
        :param difficulty: level name
        
        After changing difficulty, delete and re-create all tile buttons and
        re-start game.
        """
        self.current_difficulty_level = difficulty
        levels = self.menu_vars['levels']
        # Set checkbox values for other dificulty levels to 0,
        # there can only be one difficulty level selected.
        for level in levels:
            if level != difficulty:
                levels[level].set(0)
            else:
                levels[level].set(1)
        # Reset the game with new difficulty settings.
        rows = self.difficulty_levels[difficulty]['rows']
        columns = self.difficulty_levels[difficulty]['columns']
        bombs = self.difficulty_levels[difficulty]['bombs']
        self.unfreeze()
        self.first_btn_clicked = False
        self.game.setup(rows=rows, columns=columns, bombs=bombs)
        self.update_unmarked_bombs()
        self.update_time()
        self.create_buttons(remove=True)
    
    def set_custom_difficulty(self):
        """
        Get rows, columns, and bombs from custom difficulty dialog.
        
        If user presses OK, update custom difficulty and change game difficulty
        to custom. If user presses cancel, reset checkboxes to previous values.
        """
        # Open dialog.
        dialog_values = dialogs.ask_custom_difficulty(self.root, self.difficulty_levels[self.current_difficulty_level])
        if dialog_values is not None:
            self.difficulty_levels['custom'] = dialog_values
            self.change_difficulty('custom')
        # If user tried to change from another level to custom but
        # cancelled, set custom checkbox back to 0. If user tried to
        # change from custom to custom and but cancelled, set custom
        # checkbox back to 1.
        elif self.current_difficulty_level != 'custom':
            self.menu_vars['levels']['custom'].set(0)
        else:
            self.menu_vars['levels']['custom'].set(1)
    
    def show_best_times(self):
        """
        Open best times dialog.
        
        If reset is pressed, reset best times.
        """
        # Open dialog.
        will_reset = dialogs.ask_should_reset(self.root, self.best_times)
        if will_reset:
            self.best_times = {'beginner': (999, 'Anonymous'), 'intermediate': (999, 'Anonymous'), 'expert': (999, 'Anonymous')}
    
    def exit(self):
        """Write best times to file and quit game."""
        self.write_best_times(BEST_TIMES_FILE, self.best_times)
        self.save_game_settings(SETTINGS_FILE)
        self.root.quit()
    
    @staticmethod
    def open_help():
        """Open help link in browser."""
        webbopen(HELP_LINK)
    
    def open_about_game(self):
        """Open about game dialog."""
        dialogs.show_about_game(self.root)
    
    def tick(self):
        """Advance game time."""
        time = self.widgets['time']
        if self.first_btn_clicked:
            if self.sound_is_on():
                self.channels[0].play(self.sounds['clock'])
            self.game.tick()
            self.update_time()
            time.after(1000, self.tick)
        
    def l_hold(self, event):
        """Trigger surprised face upon holding down LMB."""
        face_button = self.widgets['face_button']
        x = face_button.winfo_rootx()
        y = face_button.winfo_rooty()
        if not (x < event.x_root < x + 52) or not (y < event.y_root < y + 52):
            if not self.is_frozen:
                face_button.configure(image=self.images['face_danger'])
    
    def l_release(self, event):
        """Trigger up face button upon releasing LMB."""
        assert event
        face_button = self.widgets['face_button']
        if not self.is_frozen:
            face_button.configure(image=self.images['face_up'])
        
    def face_button_l_hold(self, event):
        """Trigger down face upon holding down LMB on face button."""
        face_button = event.widget
        face_button.configure(image=self.images['face_down'])
    
    def face_button_l_release(self, event):
        """Reset game upon releasing LMB on face button."""
        face_button = event.widget
        if self.is_frozen:
            if self.game.game_is_won():
                face_button.configure(image=self.images['face_win'])
            else:
                face_button.configure(image=self.images['face_loss'])
        else:
            face_button.configure(image=self.images['face_up'])
        x = face_button.winfo_rootx()
        y = face_button.winfo_rooty()
        if (x < event.x_root < x + 52) and (y < event.y_root < y + 52):
            self.reset_game()
    
    def button_l_hold(self, event):
        """Trigger down tile upon holding LMB on tile button."""
        button = event.widget
        if not self.is_frozen and not button.is_disabled:
            if button.tile.mark == 'question':
                image = self.images['tile_question_down']
            else:
                image = self.images['tile_down']
            button.configure(image=image)
    
    def button_l_release(self, event):
        """
        Click tile upon releasing LMB on tile button.
        
        If tile is the first to be clicked, scatter bombs and avoid clicked
        tile. This ensures that the first tile clicked will never be a bomb.
        Clicking the first tile also starts the game timer.
        """
        time = self.widgets['time']
        button = event.widget
        tile = button.tile
        if not self.is_frozen and not button.is_disabled:
            if 0 < event.x <= 32 and 0 < event.y <= 32:
                if tile.mark != 'flag':
                    if not self.first_btn_clicked:
                        self.game.scatter_bombs(tile_to_avoid=tile)
                        self.first_btn_clicked = True
                        time.after(0, self.tick)
                    self.click_button(button)
            else:
                button.configure(image=self.images[f'tile_{tile.mark}'])
    
    def button_r_click(self, event):
        """Mark tile upon clicking RMB on tile button."""
        button = event.widget
        if not self.is_frozen and not button.tile.is_clicked:
            self.mark_button(button)
    
    def click_button(self, button):
        """
        Click a tile button, update its image and handle win/loss.
        
        :param button: button to click
        
        If player wins, freeze the game and check for fastest time. If player
        got a fastest time, ask for their name and overwrite best_times.
        If player loses, show all the bombs and freeze the game.
        """
        face_button = self.widgets['face_button']
        tile = button.tile
        multiple = self.game.click_tile(tile)
        button.is_disabled = True
        
        if self.game.game_is_won():  # Win
            if self.sound_is_on():
                self.channels[1].play(self.sounds['win'])
            face_button.configure(image=self.images['face_win'])
            self.freeze()
            # If time is fastest for the difficulty level, save it.
            if self.game.time < self.best_times[self.current_difficulty_level][0]:
                name = dialogs.ask_fastest_name(self.root, self.current_difficulty_level)
                self.best_times[self.current_difficulty_level] = (self.game.time, name)
        elif not tile.is_safe:  # Loss
            if self.sound_is_on():
                self.channels[2].play(self.sounds['bomb'])
            self.game.click_all_bombs()
            self.auto_click_buttons(red=button, all_bombs=True)
            face_button.configure(image=self.images['face_loss'])
            self.freeze()
        elif multiple:  # multiple buttons were automatically clicked
            self.auto_click_buttons()
        else:  # Single button
            image = self.images[f'tile_{tile.number}']
            button.configure(image=image)
    
    def freeze(self):
        """Freeze the game, disabling all buttons and stopping time."""
        self.is_frozen = True
        self.first_btn_clicked = False
    
    def unfreeze(self):
        """Unfreeze game, re-enabling all buttons."""
        self.is_frozen = False
    
    def auto_click_buttons(self, red=None, all_bombs=False):
        """
        Update all buttons whose tiles were clicked automatically.
        
        :param Tile red: bomb tile to mark red if game is over else None
        :param bool all_bombs: if True, reveal all bomb tiles (game end)
        
        In the original Minesweeper, when a bomb is clicked, it turns red and
        all other bombs are revealed. All incorrectly flagged bombs are marked
        with a cross.
        """
        for button in self.widgets['buttons']:
            tile = button.tile
            if tile.is_clicked or (not tile.is_safe and all_bombs) or (tile.mark == 'flag' and all_bombs):
                if tile.is_safe:
                    if all_bombs and tile.mark == 'flag':
                        image = self.images['tile_x']
                    else:
                        image = self.images[f'tile_{tile.number}']
                elif button == red:
                    image = self.images['tile_red']
                else:
                    image = self.images['tile_bomb']
                button.configure(image=image)
                button.is_disabled = True
    
    def mark_button(self, button):
        """Mark a tile, alternating between flag, question, and none."""
        tile = button.tile
        self.game.mark_tile(tile)
        # If "?" marks are off, skip "?" by marking tile again.
        if tile.mark == 'question' and not self.q_marks_are_on():
            self.game.mark_tile(tile)
        self.update_unmarked_bombs()
        button.configure(image=self.images[f'tile_{tile.mark}'])
        button.is_disabled = tile.mark == 'flag'
    
    def reset_game(self):
        """Reset core game and GUI buttons."""
        self.first_btn_clicked = False
        self.unfreeze()
        self.game.reset()
        self.update_unmarked_bombs()
        self.update_time()
        for button in self.widgets['buttons']:
            button.is_disabled = False
            button.configure(image=self.images['tile_up'])
    
    def toggle_colour(self):
        """
        Switch between colour and black-and-white images.
        
        This requires a re-load of the entire UI.
        """
        self.load_images(colour=self.colour_is_on())
        self.create_ui(remove=True)
    
    def toggle_q_marks(self):
        """
        Clear all tiles marked with "?".
        
        When ? marks are turned off, unlike in the original Minesweeper, the
        currently marked "?" tiles are reset instead of left.
        """
        for button in self.widgets['buttons']:
            if button.tile.mark == 'question':
                self.mark_button(button)
    
    def load_images(self, colour):
        """
        Load all images, creating and storing Tk PhotoImage objects.
        
        :param colour: if true, load colour images, else load b & w.
        
        All images must have a global storage method, e.g. self.images, so that
        Tkinter can constantly reference them, otherwise they won't be
        displayed.
        """
        prefix = 'nm' if colour else 'bw'
        keys = ['face_up', 'face_down', 'face_danger', 'face_win', 'face_loss', 'tile_up', 'tile_down', 'tile_bomb', 'tile_red', 'tile_x', 'tile_none', 'tile_flag', 'tile_question', 'tile_question_down', 'tile_0', 'tile_1', 'tile_2', 'tile_3', 'tile_4', 'tile_5', 'tile_6', 'tile_7', 'tile_8', 'clock_-', 'clock_0', 'clock_1', 'clock_2', 'clock_3', 'clock_4', 'clock_5', 'clock_6', 'clock_7', 'clock_8', 'clock_9']
        for key in keys:
            self.images[key] = ImageTk.PhotoImage(Img.open(f'minesweeper/images/{prefix}_{key}.png'))


if __name__ == '__main__':
    MinesweeperApp().run()
