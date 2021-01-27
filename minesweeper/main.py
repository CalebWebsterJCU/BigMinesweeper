"""
Minesweeper App
2021
A 2x scale replica of the original Windows Minesweeper.
Github: https://www.github.com/CalebWebsterJCU/Minesweeper
"""

from minesweeper.core import MineSweeper
from pygame.mixer import Channel, Sound
from webbrowser import open as webbopen
from PIL import ImageTk, Image as Img
from minesweeper import dialogs
from tkinter import *
import pygame
import os

DEFAULT_LEVEL = 'expert'
BEST_TIMES_FILE = 'best_times.csv'
HELP_LINK = 'https://www.instructables.com/How-to-play-minesweeper/'


class MinesweeperApp:
    """Minesweeper game."""
    
    def __init__(self):
        """Initialize core game, load images, sounds, and best times, create tkinter window and GUI."""
        os.chdir('minesweeper')
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
        self.current_difficulty_level = DEFAULT_LEVEL
        self.best_times = {'beginner': (999, 'Anonymous'), 'intermediate': (999, 'Anonymous'), 'expert': (999, 'Anonymous')}
        self.read_best_times(BEST_TIMES_FILE)
        # Load Sounds
        pygame.init()
        self.sound_bomb = Sound('sounds/bomb.wav')
        self.sound_clock = Sound('sounds/clock.wav')
        self.sound_win = Sound('sounds/win.wav')
        self.channel0 = Channel(0)
        self.channel1 = Channel(1)
        self.channel2 = Channel(2)
        # Initialize Tkinter Window
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.root.resizable(False, False)
        self.root.iconbitmap('icon.ico')
        self.root.title('Minesweeper')
        self.load_images(colour=True)
        self.create_menu()
        self.create_ui()
        # Start game with default settings
        self.start_game()
    
    def read_best_times(self, filename):
        """Read best times from file and update self.best_times."""
        with open(filename, 'r') as file_in:
            for line in file_in:
                parts = line.strip().split(',')
                level = parts[0]
                time = int(parts[1])
                name = parts[2]
                self.best_times[level] = (time, name)
    
    def write_best_times(self, filename):
        """Write best times to file if time is not None."""
        with open(filename, 'w') as file_out:
            for level, (time, name) in self.best_times.items():
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
        """Initialize minesweeper game, setting difficulty level to default."""
        self.change_difficulty(DEFAULT_LEVEL)
    
    def run(self):
        """Start the Tkinter GUI."""
        self.root.mainloop()
    
    def create_ui(self, remove=False):
        """
        Create the semi-static widgets.
        All widgets are contained within main_container.
        main_container is divided into two sections, top_frame and bottom_frame.
        :param remove: if true, remove all widgets before creating.
        """
        remove_buttons = False
        if remove:
            remove_buttons = True
            self.widgets['main_container'].pack_forget()
        main_container = LabelFrame(self.root, bd=0, bg='#c0c0c0')
        top_frame = LabelFrame(main_container, bd=6, relief=SUNKEN, bg='#c0c0c0')
        unmarked_bombs = LabelFrame(top_frame, bd=3, relief=SUNKEN)
        for x in range(3):
            Label(unmarked_bombs, image=self.images['clock_0'], bd=0).grid(row=0, column=x)
        if self.is_frozen:
            if self.game.game_is_won():
                face_img = self.images['face_win']
            else:
                face_img = self.images['face_loss']
        else:
            face_img = self.images['face_up']
        face_button = Label(top_frame, bd=0, image=face_img, bg='#c0c0c0')
        time = Label(top_frame, bd=3, relief=SUNKEN)
        for x in range(3):
            Label(time, image=self.images['clock_0'], bd=0).grid(row=0, column=x)
        
        bottom_frame = LabelFrame(main_container, bd=6, relief=SUNKEN, bg='#c0c0c0')
        main_container.pack(expand=True, fill=BOTH)
        top_frame.pack(expand=True, fill=BOTH, padx=15, pady=(15, 0))
        unmarked_bombs.pack(side=LEFT, padx=(10, 0), pady=10)
        face_button.pack(side=LEFT, expand=True, padx=2, pady=10)
        time.pack(side=RIGHT, padx=(0, 10), pady=10)
        bottom_frame.pack(expand=True, fill=BOTH, padx=15, pady=15)
        
        face_button.bind('<ButtonPress-1>', self.face_button_l_hold)
        face_button.bind('<ButtonRelease-1>', self.face_button_l_release)
        
        self.widgets['main_container'] = main_container
        self.widgets['top_frame'] = top_frame
        self.widgets['unmarked_bombs'] = unmarked_bombs
        self.widgets['time'] = time
        self.widgets['face_button'] = face_button
        self.widgets['bottom_frame'] = bottom_frame
        
        self.create_buttons(remove=remove_buttons)
        self.click_buttons(all_bombs=self.game.game_is_lost())
        self.update_unmarked_bombs()
        self.update_time()
        
        self.root.bind_all('<ButtonPress-1>', self.l_hold)
        self.root.bind_all('<ButtonRelease-1>', self.l_release)
        self.root.bind_all("<Key>", self.handle_key_press)
        self.root.bind_all("<Escape>", lambda event: self.exit())

        self.update_time()
    
    def create_menu(self):
        """
        Create the Tkinter window menu.
        Layout: Game | Help
        Default: Marks (?) -> ON, Colour -> ON, Sound -> OFF
        """
        # Top menu
        main_menu = Menu(self.root)
        self.root.configure(menu=main_menu)
        # Menu button: Game
        game_menu = Menu(main_menu, tearoff=False)
        main_menu.add_cascade(label='Game', menu=game_menu)
        # Options
        game_menu.add_command(label=f'New {"F2":>30}', command=self.reset_game)
        game_menu.add_separator()
        b = IntVar()
        i = IntVar()
        e = IntVar()
        c = IntVar()
        game_menu.add_checkbutton(label='Beginner', variable=b, command=lambda: self.change_difficulty('beginner'))
        game_menu.add_checkbutton(label='Intermediate', variable=i, command=lambda: self.change_difficulty('intermediate'))
        game_menu.add_checkbutton(label='Expert', variable=e, command=lambda: self.change_difficulty('expert'))
        game_menu.add_checkbutton(label='Custom...', variable=c, command=self.set_custom_difficulty)
        game_menu.add_separator()
        m = IntVar()
        cl = IntVar()
        s = IntVar()
        m.set(1)
        cl.set(1)
        s.set(0)
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
        :param remove: if true, remove all buttons before creating.
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
        Return a list of numbered images corresponding to the characters
        in a zero-filled string of a number.
        E.G. num=3 -> [image0, image0, image3]
        :param num: number to convert into images.
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
        Change difficulty level of core game, creating new tiles
        and re-creating tile buttons.
        :param difficulty: level name, one of: Beginner, Intermediate, Expert, Custom.
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
        Open custom difficulty dialog, getting rows, columns, and bombs from user.
        If user presses OK, update custom difficulty and change game difficulty to custom.
        If user presses cancel, reset checkboxes to previous values.
        """
        dialog_values = dialogs.ask_custom_difficulty(self.root, self.difficulty_levels[self.current_difficulty_level])
        if dialog_values is not None:
            self.difficulty_levels['custom'] = dialog_values
            self.change_difficulty('custom')
        # If user tried to change from another level to custom but cancelled,
        # set custom checkbox back to 0. If user tried to change from custom
        # to custom and but cancelled, set custom checkbox back to 1.
        elif self.current_difficulty_level != 'custom':
            self.menu_vars['levels']['custom'].set(0)
        else:
            self.menu_vars['levels']['custom'].set(1)
    
    def show_best_times(self):
        """Open best times dialog. If user presses Reset button, reset best times."""
        will_reset = dialogs.ask_should_reset(self.root, self.best_times)
        if will_reset:
            self.best_times = {'beginner': (999, 'Anonymous'), 'intermediate': (999, 'Anonymous'), 'expert': (999, 'Anonymous')}
    
    def exit(self):
        """Write best times to file and quit game."""
        self.write_best_times(BEST_TIMES_FILE)
        self.root.quit()
    
    @staticmethod
    def open_help():
        """Open help link in browser."""
        webbopen(HELP_LINK)
    
    def open_about_game(self):
        """Open about game dialog."""
        dialogs.show_about_game(self.root)
    
    def tick(self):
        """
        If game is being played, increment core game time, play clock sound,
        and update time counter.
        """
        time = self.widgets['time']
        if self.first_btn_clicked:
            if self.sound_is_on():
                self.channel0.play(self.sound_clock)
            self.game.tick()
            self.update_time()
            time.after(1000, self.tick)
        
    def l_hold(self, event):
        """Universal lms button hold event to trigger surprised face."""
        face_button = self.widgets['face_button']
        x = face_button.winfo_rootx()
        y = face_button.winfo_rooty()
        if not (x < event.x_root < x + 52) or not (y < event.y_root < y + 52):
            if not self.is_frozen:
                face_button.configure(image=self.images['face_danger'])
    
    def l_release(self, event):
        """
        Universal LMB release event to reset smile face and reset game
        if face button is clicked on.
        """
        assert event
        face_button = self.widgets['face_button']
        if not self.is_frozen:
            face_button.configure(image=self.images['face_up'])
        
    def face_button_l_hold(self, event):
        """LMB click/hold event on face button to trigger smile down."""
        face_button = event.widget
        face_button.configure(image=self.images['face_down'])
    
    def face_button_l_release(self, event):
        """LMB click/hold event on face button to trigger smile down."""
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
        """LMB click/hold event on tile button to trigger button down."""
        button = event.widget
        if not self.is_frozen and not button.is_disabled:
            if button.tile.mark == 'question':
                image = self.images['tile_question_down']
            else:
                image = self.images['tile_down']
            button.configure(image=image)
    
    def button_l_release(self, event):
        """
        LMB release event on tile button to trigger button up or click
        button if mouse is hovering over it. If button is the first to
        be clicked, scatter bombs and start game timer.
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
        """RMB click event on tile button to trigger button mark."""
        button = event.widget
        if not self.is_frozen and not button.tile.is_clicked:
            self.mark_button(button)
    
    def click_button(self, button):
        """
        Click on a button, disabling it to future clicks, then disable all
        other buttons that were automatically clicked after it.
        """
        face_button = self.widgets['face_button']
        tile = button.tile
        multiple = self.game.click_tile(tile)
        button.is_disabled = True
        
        if self.game.game_is_won():  # Win
            if self.sound_is_on():
                self.channel1.play(self.sound_win)
            face_button.configure(image=self.images['face_win'])
            self.freeze()
            # If time is fastest recorded for the difficulty level, save it.
            if self.game.time < self.best_times[self.current_difficulty_level][0]:
                name = dialogs.ask_fastest_name(self.root, self.current_difficulty_level)
                self.best_times[self.current_difficulty_level] = (self.game.time, name)
        elif not tile.is_safe:  # Loss
            if self.sound_is_on():
                self.channel2.play(self.sound_bomb)
            self.game.click_all_bombs()
            self.click_buttons(red=button, all_bombs=True)
            face_button.configure(image=self.images['face_loss'])
            self.freeze()
        elif multiple:  # multiple buttons were automatically clicked
            self.click_buttons()
        else:  # Single button
            image = self.images[f'tile_{tile.number}']
            button.configure(image=image)
    
    def freeze(self):
        """Disable all buttons."""
        self.is_frozen = True
        self.first_btn_clicked = False
    
    def unfreeze(self):
        """Enable all buttons"""
        self.is_frozen = False
    
    def click_buttons(self, red=None, all_bombs=False):
        """
        Iterate through tile buttons, updating the images of all whose tile
        has been clicked and disabling them.
        :param red: stores Tile. If not None, set image of this tile's button to red bomb.
        :param all_bombs: if True, click on all bomb tiles and tiles with flag mark.
        Set image of all mistakenly flagged safe tiles to crossed-out bomb.
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
        """
        Mark a button's tile, updating unmarked_bombs and disabling
        the button if mark is flag.
        """
        tile = button.tile
        self.game.mark_tile(tile)
        # If "?" marks are off, skip "?" by marking tile again.
        if tile.mark == 'question' and not self.q_marks_are_on():
            self.game.mark_tile(tile)
        self.update_unmarked_bombs()
        button.configure(image=self.images[f'tile_{tile.mark}'])
        button.is_disabled = tile.mark == 'flag'
    
    def reset_game(self):
        """
        Reset core game, clearing all tiles, resetting and enabling
        all buttons.
        """
        self.first_btn_clicked = False
        self.unfreeze()
        self.game.reset()
        self.update_unmarked_bombs()
        self.update_time()
        for button in self.widgets['buttons']:
            button.is_disabled = False
            button.configure(image=self.images['tile_up'])
    
    def toggle_colour(self):
        """Switch between colour and black-and-white images, reloading the entire UI."""
        self.load_images(colour=self.colour_is_on())
        self.create_ui(remove=True)
    
    def toggle_q_marks(self):
        """Find all tiles with question marks, and mark them to remove it."""
        for button in self.widgets['buttons']:
            if button.tile.mark == 'question':
                self.mark_button(button)
    
    def load_images(self, colour):
        """
        Load all images, creating Tk PhotoImage objects. These images must
        have a static storage method, such as dict: self.images, so that Tkinter can constantly
        reference them, otherwise they won't be displayed.
        :param colour: if true, load colour images, else load black-and-white images.
        """
        prefix = 'nm' if colour else 'bw'
        keys = ['face_up', 'face_down', 'face_danger', 'face_win', 'face_loss', 'tile_up', 'tile_down', 'tile_bomb', 'tile_red', 'tile_x', 'tile_none', 'tile_flag', 'tile_question', 'tile_question_down', 'tile_0', 'tile_1', 'tile_2', 'tile_3', 'tile_4', 'tile_5', 'tile_6', 'tile_7', 'tile_8', 'clock_-', 'clock_0', 'clock_1', 'clock_2', 'clock_3', 'clock_4', 'clock_5', 'clock_6', 'clock_7', 'clock_8', 'clock_9']
        for key in keys:
            self.images[key] = ImageTk.PhotoImage(Img.open(f'images/{prefix}_{key}.png'))


if __name__ == '__main__':
    MinesweeperApp().run()
