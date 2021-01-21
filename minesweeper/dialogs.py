from tkinter import Toplevel, Label, Button, Entry, Frame, LEFT, RIGHT, SOLID, W, E, ACTIVE
from tkinter.simpledialog import Dialog
from webbrowser import open as webb_open


class CustomDialog(Dialog):
    
    def __init__(self, parent, title='', icon='', i_h=0, i_w=0, i_m=0):
        
        self.height = i_h
        self.width = i_w
        self.mines = i_m
        self.widgets = {}
        
        Toplevel.__init__(self, parent)
        
        self.withdraw()
        
        if parent.winfo_viewable():
            self.transient(parent)
        
        if title:
            self.title(title)
        
        if icon:
            self.iconbitmap(icon)
        
        self.parent = parent
        
        self.result = None
        
        body = Frame(self)
        
        self.initial_focus = self.body(body)
        
        body.pack(side=LEFT, padx=(15, 10), pady=30)
        
        self.buttonbox()
        
        if not self.initial_focus:
            self.initial_focus = self
        
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))
        
        self.deiconify()  # become visible now
        
        self.initial_focus.focus_set()
        
        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)
    
    def body(self, master):
        
        height_label = Label(master, bd=0, text='Height:', anchor=W)
        width_label = Label(master, bd=0, text='Width:', anchor=W)
        mines_label = Label(master, bd=0, text='Mines:', anchor=W)
        height_input = Entry(master, bd=1, width=5, relief=SOLID)
        width_input = Entry(master, bd=1, width=5, relief=SOLID)
        mines_input = Entry(master, bd=1, width=5, relief=SOLID)
        
        height_input.insert(0, self.height)
        width_input.insert(0, self.width)
        mines_input.insert(0, self.mines)
        
        height_label.grid(row=0, column=0, sticky=W + E, padx=(0, 10))
        width_label.grid(row=1, column=0, sticky=W + E, padx=(0, 10))
        mines_label.grid(row=2, column=0, sticky=W + E, padx=(0, 10))
        
        height_input.grid(row=0, column=1, ipady=1, ipadx=1)
        width_input.grid(row=1, column=1, pady=4, ipady=1, ipadx=1)
        mines_input.grid(row=2, column=1, ipady=1, ipadx=1)
        
        self.widgets['height_input'] = height_input
        self.widgets['width_input'] = width_input
        self.widgets['mines_input'] = mines_input
        
        return 0
    
    def buttonbox(self):
        button_frame = Frame(self)
        ok_btn = Button(button_frame, text="OK", width=7, command=self.ok, default=ACTIVE)
        cancel_btn = Button(button_frame, text="Cancel", width=7, command=self.cancel)
        
        button_frame.pack(side=RIGHT, padx=(10, 15), pady=30)
        ok_btn.pack(pady=(0, 6))
        cancel_btn.pack(pady=(6, 0))
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
    
    def validate(self):
        height = self.widgets['height_input'].get()
        width = self.widgets['width_input'].get()
        mines = self.widgets['mines_input'].get()
        try:
            height = int(height)
            width = int(width)
            mines = int(mines)
            
            max_mines = (height - 1) * (width - 1)
            
            if height > 24:
                height = 24
            elif height < 9:
                height = 9
            if width > 30:
                width = 30
            elif width < 9:
                width = 9
            if mines > max_mines:
                mines = max_mines
            elif mines < 10:
                mines = 10
        except ValueError:
            if not isinstance(height, int):
                height = 9
            if not isinstance(width, int):
                width = 9
            if not isinstance(mines, int):
                mines = 10
        
        self.height = height
        self.width = width
        self.mines = mines
        
        return True
    
    def apply(self):
        if self.validate():
            self.result = {'rows': self.height, 'columns': self.width, 'bombs': self.mines}
        return True


class NameDialog(Dialog):
    
    def __init__(self, parent, title='', icon='', level=''):
        
        self.level = level
        self.message = f'You have the fastest time \nfor {self.level} level. \nPlease enter your name.'
        self.name = 'Anonymous'
        self.widgets = {}
        
        Toplevel.__init__(self, parent)
        
        self.withdraw()
        
        if parent.winfo_viewable():
            self.transient(parent)
        
        if title:
            self.title(title)
        
        if icon:
            self.iconbitmap(icon)
        
        self.parent = parent
        
        self.result = None
        
        body = Frame(self, padx=15, pady=15)
        
        self.initial_focus = self.body(body)
        
        body.pack()
        
        self.buttonbox()
        
        if not self.initial_focus:
            self.initial_focus = self
        
        self.protocol("WM_DELETE_WINDOW", self.ok)
        
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.deiconify()  # become visible now
        
        self.initial_focus.focus_set()
        
        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)
    
    def body(self, master):
        message = Label(master, text=self.message)
        name_input = Entry(master, width=20, bd=1, relief=SOLID)
        name_input.insert(0, self.name)
        
        message.pack(pady=(0, 30))
        name_input.pack(ipady=1, ipadx=1)
        
        self.widgets['message'] = message
        self.widgets['name_input'] = name_input
        
        return name_input
    
    def buttonbox(self):
        ok_btn = Button(self, text="OK", width=7, command=self.ok, default=ACTIVE)
        ok_btn.pack(pady=(0, 15))
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
    
    def validate(self):
        self.name = self.widgets['name_input'].get()
        return True
    
    def apply(self):
        self.result = self.name
        return True


class ScoresDialog(Dialog):
    
    def __init__(self, parent, title='', icon='', scores=None):
        
        self.scores = scores
        self.will_reset = False
        self.widgets = {}
        
        Toplevel.__init__(self, parent)
        
        self.withdraw()
        
        if parent.winfo_viewable():
            self.transient(parent)
        
        if title:
            self.title(title)
        
        if icon:
            self.iconbitmap(icon)
        
        self.parent = parent
        
        self.result = None
        
        self.body_container = Frame(self)
        
        self.initial_focus = self.body(self.body_container)
        
        self.body_container.pack(padx=20, pady=(30, 20))
        
        self.buttonbox()
        
        if not self.initial_focus:
            self.initial_focus = self
        
        self.protocol("WM_DELETE_WINDOW", self.ok)
        
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))
        
        self.deiconify()  # become visible now
        
        self.initial_focus.focus_set()
        
        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)
    
    def body(self, master):
        self.widgets['labels'] = {}
        for i, (level, (time, name)) in enumerate(self.scores.items()):
            level_label = Label(master, bd=0, text=f'{level.title()}:', anchor=W)
            time_label = Label(master, bd=0, text=f'{time} seconds', anchor=W)
            name_label = Label(master, bd=0, text=f'{name}', anchor=W)
            level_label.grid(row=i, column=0, sticky=W+E)
            time_label.grid(row=i, column=1, sticky=W+E, padx=15)
            name_label.grid(row=i, column=2, sticky=W+E)
            self.widgets['labels'][level] = [level_label, time_label, name_label]
        return 0
    
    def reset(self):
        self.result = True
        self.scores = {'beginner': (999, 'Anonymous'), 'intermediate': (999, 'Anonymous'), 'expert': (999, 'Anonymous')}
        for i, (level, (time, name)) in enumerate(self.scores.items()):
            level_label = self.widgets['labels'][level][0]
            time_label = self.widgets['labels'][level][1]
            name_label = self.widgets['labels'][level][2]
            level_label.configure(text=f'{level.title()}:')
            time_label.configure(text=f'{time} seconds')
            name_label.configure(text=f'{name}')

    def buttonbox(self):
        reset_btn = Button(self, text="Reset Scores", command=self.reset)
        ok_btn = Button(self, text="OK", width=7, command=self.ok, default=ACTIVE)
        
        reset_btn.pack(side=LEFT, padx=(30, 0), pady=(0, 15))
        ok_btn.pack(side=RIGHT, padx=(0, 30), pady=(0, 15))
        
        self.bind("<Escape>", self.ok)
        
        self.widgets['reset_btn'] = reset_btn
        self.widgets['ok_btn'] = ok_btn
    
    def validate(self):
        return True
    
    def apply(self):
        return True


class AboutDialog(Dialog):
    
    GITHUB_LINK = 'https://www.github.com/CalebWebsterJCU/Minesweeper'
    
    def __init__(self, parent, title='', icon=''):
        
        Toplevel.__init__(self, parent)
        
        self.withdraw()
        
        if parent.winfo_viewable():
            self.transient(parent)
        
        if title:
            self.title(title)
        
        if icon:
            self.iconbitmap(icon)
        
        self.parent = parent
        
        self.result = None
        
        body = Frame(self, padx=15, pady=15)
        
        self.initial_focus = self.body(body)
        
        body.pack()
        
        self.buttonbox()
        
        if not self.initial_focus:
            self.initial_focus = self
        
        self.protocol("WM_DELETE_WINDOW", self.ok)
        
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.deiconify()  # become visible now
        
        self.initial_focus.focus_set()
        
        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)
    
    def body(self, master):
        title = Label(master, text='Minesweeper', font=('Goldman', 25))
        author = Label(master, text='by Caleb Webster', font=('Goldman', 14))
        year = Label(master, text='January, 2021', font=('Goldman', 11))
        github = Label(master, text=f'{self.GITHUB_LINK[8:]}', font=('Goldman', 10))
        
        title.pack()
        author.pack()
        year.pack()
        github.pack()
        
        return 0
    
    def buttonbox(self):
        ok_btn = Button(self, text='Close', width=7, command=self.ok, default=ACTIVE)
        github_btn = Button(self, text='Open Github', command=lambda: webb_open(self.GITHUB_LINK))
        github_btn.pack(side=LEFT, pady=15, padx=15)
        ok_btn.pack(side=RIGHT, pady=15, padx=15)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)


def ask_custom_difficulty(root, default_values):
    height = default_values['rows']
    width = default_values['columns']
    mines = default_values['bombs']
    return CustomDialog(parent=root, title='Custom Field', icon='icon.ico', i_h=height, i_w=width, i_m=mines).result


def ask_fastest_name(root, level):
    return NameDialog(parent=root, title='Fastest Time', icon='icon.ico', level=level).result


def ask_should_reset(root, scores):
    return ScoresDialog(parent=root, title='Fastest Mine Sweepers', icon='icon.ico', scores=scores).result


def show_about_game(root):
    return AboutDialog(parent=root, title='About Minesweeper', icon='icon.ico')
