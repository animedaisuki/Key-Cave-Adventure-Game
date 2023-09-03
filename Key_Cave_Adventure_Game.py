import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk

GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "
TASK_ONE = 1
TASK_TWO = 2
POS_TASK = 3

DIRECTIONS = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1)
}

INVESTIGATE = "I"
QUIT = "Q"
HELP = "H"

VALID_ACTIONS = [INVESTIGATE, QUIT, HELP, *DIRECTIONS.keys()]

HELP_MESSAGE = f"Here is a list of valid actions: {VALID_ACTIONS}"

INVALID = "That's invalid."

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."


class Display:
    """Display of the dungeon."""

    def __init__(self, game_information, dungeon_size):
        """Construct a view of the dungeon.

        Parameters:
            game_information (dict<tuple<int, int>: Entity): Dictionary
                containing the position and the corresponding Entity
            dungeon_size (int): the width of the dungeon.
        """

        self._game_information = game_information
        self._dungeon_size = dungeon_size

    def display_game(self, player_pos):
        """Displays the dungeon.

        Parameters:
            player_pos (tuple<int, int>): The position of the Player
        """

        dungeon = ""

        for i in range(self._dungeon_size):
            rows = ""
            for j in range(self._dungeon_size):
                position = (i, j)
                entity = self._game_information.get(position)

                if entity is not None:
                    char = entity.get_id()
                elif position == player_pos:
                    char = PLAYER
                else:
                    char = SPACE
                rows += char
            if i < self._dungeon_size - 1:
                rows += "\n"
            dungeon += rows
        return dungeon

    def display_moves(self, moves):
        """Displays the number of moves the Player has left.

        Parameters:
            moves (int): THe number of moves the Player can preform.
        """

        return f"{moves} moves remaining"


def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.

    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the
            dungeon.
    """

    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout


def load_game_for_saved(filename):
    """Create a 2D array of string representing the dungeon to display.

    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the
            dungeon.
    """

    dungeon_layout = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines[5:]:
            line = line.strip()
            dungeon_layout.append(list(line))
    return dungeon_layout


class Entity:
    """A generic Entity within the game"""

    _id = "Entity"

    def __init__(self):
        """
        Something the player can interact with
        """

        self._collidable = True

    def get_id(self):
        """Returns a string that represents the Entity’s (special type's) ID"""

        return self._id

    def set_collide(self, collidable):
        """Set the collision state for the Entity to be True
        """

        self._collidable = collidable

    def can_collide(self):
        """Returns True if the Entity can be collided with (another
        Entity can share the position that this one is in) and False otherwise"""

        return self._collidable

    def __str__(self):
        """Returns the string representation of the Entity."""

        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        """Returns the string representation of the Entity."""

        return str(self)


class Wall(Entity):
    """a special type of an Entity within the game"""

    _id = WALL

    def __init__(self):
        """Constructor of the Wall class."""

        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """a special type of an Entity within the game"""

    def on_hit(self, game):
        """Raises the NotImplementedError"""

        raise NotImplementedError


class Key(Item):
    """a special type of Item within the game"""

    _id = KEY

    def on_hit(self, game):
        """When the player takes the Key the Key should be added to the Player’s inventory.
        The Key should then be removed from the dungeon once it’s in the Player’s inventory.
        """

        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """a special type of Item within the game"""

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """Constructor of the MoveIncrease class.

        Parameters:
            moves (int): The number of extra moves the Player will be granted when they
            collect this Item.
        """

        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """When the player hits the MoveIncrease (M) item the number of moves for the player
        increases and the M item is removed from the game. These actions are implemented
        via the on_hit method. Specifically, extra moves should be granted to the Player
        and the M item should be removed from the game."""

        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """a special type of an Entity within the game"""
    _id = DOOR

    def on_hit(self, game):
        """If the Player’s inventory contains a Key Entity then this method
        should set the ‘game over’ state to be True."""

        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                return


class Player(Entity):
    """a special type of an Entity within the game"""

    _id = PLAYER

    def __init__(self, move_count):
        """Constructor of the Player class.

        Parameters:
            move_count (int): represents how many moves a Player can have for the given
            dungeon they are in.
        """

        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None


    def set_position(self, position):
        """Sets the position of the Player"""

        self._position = position

    def get_position(self):
        """Returns a tuple of ints representing the position of the Player.
        If the Player’s position has not been set yet then this method should
        return None."""

        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """

        self._move_count += number

    def moves_remaining(self):
        """Returns an int representing how many moves the Player has left before
        they reach the maximum move count"""

        return self._move_count

    def adjust_moves(self, moves):
        """Adjust how many moves the Player has left before they reach the maximum
        move count"""

        self._move_count = moves

    def add_item(self, item):
        """Adds item (Item) to inventory
        """

        self._inventory.append(item)

    def get_inventory(self):
        """Returns a list that represents the Player’s inventory.
        If the Player has nothing in their inventory then an empty list should
        be returned."""

        return self._inventory


class GameLogic:
    """Contains all the game information and how the game should play out"""

    def __init__(self, dungeon_name="game1.txt"):
        """Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of the level.
        """

        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()

        self._win = False
        self._mode = None

    def adjust_game_logic(self, new_dungeon):
        """Adjust constructor of the GameLogic class."""

        self._dungeon = new_dungeon
        self._dungeon_size = len(self._dungeon)
        self._game_information = self.init_game_information()

        self._win = False
        self._mode = None

    def get_positions(self, entity):
        """ Returns a list of tuples containing all positions of a given Entity
             type.

        Parameters:
            entity (str): the id of an entity.

        Returns:
            list(<tuple<int, int>>): Returns a list of tuples representing the
            positions of a given entity id.
        """

        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """Return a dictionary containing the position and the corresponding Entity as the
        keys and values respectively, and sets the Player’s position."""

        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)
        door_position = self.get_positions(DOOR)
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)

        self._player.set_position(player_pos)

        information = {}

        for key in key_position:
            information[key] = Key()

        for door in door_position:
            information[door] = Door()

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """Returns the Player object within the game"""

        return self._player

    def get_entity(self, position):
        """Returns an Entity at a given position in the dungeon. Entity in the given
        direction or if the position is off map then this function should return None.
        """

        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """Returns an Entity in the given direction of the Player’s position. If there is
        no Entity in the given direction or if the direction is off map then this function
        should return None."""

        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """Returns a dictionary containing the position and the corresponding Entity,
        as the keys and values, for the current dungeon."""

        return self._game_information

    def get_dungeon_size(self):
        """Returns the width of the dungeon as an integer"""

        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True

        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """Returns a tuple of integers that represents the new position given the direction."""

        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """Return True if the game has been lost and False otherwise."""

        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """Set the game’s win state to be True or False."""

        self._win = win

    def won(self):
        """Return game’s win state."""

        return self._win


class AbstractGrid(tk.Canvas):
    """Abstract grid used for further map drawing."""

    def __init__(self, master, rows, cols, width, height, **kwargs):
        """Constructor of the AbstractGrid class."""

        super().__init__(master, **kwargs)
        self._box = None
        self._width = width / rows
        self._height = height / cols

    def get_bbox(self, position):
        """Returns the bounding box for the (row, col) position."""

        y1 = position[0]
        x1 = position[1]
        y2 = position[0] + 1
        x2 = position[1] + 1
        box_y1 = y1 * self._width
        box_x1 = x1 * self._height
        box_y2 = y2 * self._width
        box_x2 = x2 * self._height
        return box_x1, box_y1, box_x2, box_y2

    def pixel_to_position(self, pixel):
        """Converts the x, y pixel position (in graphics units) to a (row, col) position."""

        x, y = pixel
        row = x // self._width
        col = y // self._height
        return row, col

    def get_position_center(self, position):
        """Gets the graphics coordinates for the center of the cell at the given (row, col) position."""

        y1 = position[0]
        x1 = position[1]
        y2 = position[0] + 1
        x2 = position[1] + 1
        box_y1 = y1 * self._width
        box_x1 = x1 * self._width
        box_y2 = y2 * self._width
        box_x2 = x2 * self._width
        y_center = (box_y2 - box_y1) / 2 + box_y1
        x_center = (box_x2 - box_x1) / 2 + box_x1
        return x_center, y_center

    def annotate_position(self, position, text):
        """Annotates the cell at the given (row, col) position with the provided text."""

        self.create_text(self.get_position_center(position), text=text, font=('Calibri', 15))

    def get_width(self):
        """Gets the width of every single rectangle"""

        return self._width

    def get_height(self):
        """Gets the height of every single rectangle"""

        return self._height


class DungeonMap(AbstractGrid):
    """Draws the dungeon map, every entity is represented by a rectangle."""

    def __init__(self, master, size, width=600, **kwargs):
        """Constructor of the DungeonMap class."""

        super().__init__(master, rows=size, cols=size, width=width, height=width, **kwargs)
        self.config(width=width, height=width)
        self._dungeon_size = size

    def draw_grid(self, dungeon, player_position):
        """Draws the dungeon on the DungeonMap based on dungeon, and draws the player at the
         specified (row, col) position."""

        self.redraw()

        for i in range(self._dungeon_size):
            for j in range(self._dungeon_size):
                position = (i, j)
                entity = dungeon.get(position)

                if entity is not None:
                    char = entity.get_id()
                    if char == WALL:
                        self.create_rectangle(self.get_bbox(position), fill='Dark grey')
                    elif char == KEY:
                        self.create_rectangle(self.get_bbox(position), fill='Yellow')
                        self.annotate_position(position, 'Trash')
                    elif char == DOOR:
                        self.create_rectangle(self.get_bbox(position), fill='Red')
                        self.annotate_position(position, 'Nest')
                    elif char == MOVE_INCREASE:
                        self.create_rectangle(self.get_bbox(position), fill='Orange')
                        self.annotate_position(position, 'Banana')

                elif position == player_position:
                    self.create_rectangle(self.get_bbox(position), fill='Medium spring green')
                    self.annotate_position(position, 'Ibis')
                else:
                    pass

    def redraw(self):
        """Delete everything on the dungeon map."""
        self.delete(tk.ALL)



class KeyPad(AbstractGrid):
    """Key pads used represented by rectangles, used for controlling the move directions of game """

    def __init__(self, master, width=200, height=100, **kwargs):
        super().__init__(master, rows=3, cols=2, width=width, height=height, **kwargs)
        self.config(width=width, height=height)
        self._width = width / 3
        self._height = height / 2

    def draw_key_grid(self):
        """Draws the rectangles which represent key pads."""

        self.create_rectangle(2 * self._width, self._height, 3 * self._width, 2 * self._height, fill='dark grey')
        self.create_text((self._width / 2 + 2 * self._width, self._height / 2 + self._height), text='E')

        self.create_rectangle(self._width, self._height, 2 * self._width, 2 * self._height, fill='dark grey')
        self.create_text((self._width / 2 + self._width, self._height / 2 + self._height), text='S')

        self.create_rectangle(0, self._height, self._width, 2 * self._height, fill='dark grey')
        self.create_text((self._width / 2, self._height / 2 + self._height), text='W')

        self.create_rectangle(self._width, 0, 2 * self._width, self._height, fill='dark grey')
        self.create_text((self._width/2 + self._width, self._height / 2), text='N')

    def pixel_to_direction(self, pixel):
        """Converts the x, y pixel position to the direction of the arrow depicted at that position."""

        x, y = pixel
        row = x // self._width
        col = y // self._height
        if row == 0 and row == 0:
            return None
        if row == 2 and col == 0:
            return None
        if row == 1 and col == 0:
            return 'N'
        if row == 0 and col == 1:
            return 'W'
        if row == 1 and col == 1:
            return 'S'
        if row == 2 and col == 1:
            return 'E'


class StatusBar(tk.Frame):
    """A status bar showing the game status loacted at bottom."""

    def __init__(self, master, **kw):
        """Constructor of the StatusBar class."""
        super().__init__(master, **kw)

        self._master = master

        self._second = 1
        self._minute = 0
        self._time_used = '0 m 0 s'
        self._mode = None

        self.button_frame = tk.Frame(self._master)
        self.button_frame.pack(side=tk.LEFT, padx=55)
        self.new_game_button = tk.Button(self.button_frame, text='New Game', font=('Calibri', 12))
        self.new_game_button.pack(side=tk.TOP)
        self.quit_button = tk.Button(self.button_frame, text='Quit', font=('Calibri', 12))
        self.quit_button.pack(side=tk.TOP)

        self.time_frame = tk.Frame(self._master)
        self.time_frame.pack(side=tk.LEFT)
        self.clock_img = Image.open('images/clock.png').resize((50, 75))
        self.clock_img = ImageTk.PhotoImage(self.clock_img)
        self.clock_img_label = tk.Label(self.time_frame, image=self.clock_img)
        self.clock_img_label.pack(side=tk.LEFT)

        self.time_label = tk.Label(self.time_frame, text='Time elapsed', font=('Calibri', 12))
        self.time_label.pack(pady=(15, 0))
        self.time_number_label = tk.Label(self.time_frame, text=self._time_used, font=('Calibri', 12))
        self.time_number_label.pack()

        self.moves_frame = tk.Frame(self._master)
        self.moves_frame.pack(side=tk.LEFT, padx=100)
        self.moves_img = Image.open('images/lightning.png').resize((50, 75))
        self.moves_img = ImageTk.PhotoImage(self.moves_img)
        self.moves_img_label = tk.Label(self.moves_frame, image=self.moves_img)
        self.moves_img_label.pack(side=tk.LEFT)

        self.moves_label = tk.Label(self.moves_frame, text='Moves left', font=('Calibri', 12))
        self.moves_label.pack(pady=(15, 0))
        self.remains_label = tk.Label(self.moves_frame,
                                      font=('Calibri', 12))
        self.remains_label.pack()

        self._time = self.after(1000, self.update_time)

    def update_moves(self, moves):
        """Updates player moves showing on the label when the player moves."""

        self.remains_label.config(text=f"{moves} moves remaining")

    def update_time(self):
        """Updates time of the game play."""

        self._time_used = f'{self._minute} m {self._second} s'
        self._time = self.after(1000, self.update_time)
        self._second += 1
        if self._second // 60:
            self._minute += 1
            self._second = 0
        self.time_number_label.config(text=self._time_used)


    def reset_time(self):
        """Resets the time at initial value."""

        self._second = 1
        self._minute = 0

    def adjust_time(self, new_second, new_minute):
        """Resets the value of the time."""

        self._second = new_second
        self._minute = new_minute

    def get_second(self):
        """Returns the seconds of the game play."""

        return self._second

    def get_minute(self):
        """Returns the minutes of the game play."""

        return self._minute

class PostStatusBar(tk.Frame):
    """A status bar showing the game status loacted at bottom."""

    def __init__(self, master, **kw):
        """Constructor of the PostStatusBar class."""
        super().__init__(master, **kw)

        self._master = master

        self._second = 1
        self._minute = 0
        self._time_used = '0 m 0 s'
        self._mode = None

        self.button_frame = tk.Frame(self._master)
        self.button_frame.pack(side=tk.LEFT, padx=55)
        self.new_game_button = tk.Button(self.button_frame, text='New Game', font=('Calibri', 12))
        self.new_game_button.pack(side=tk.TOP)
        self.quit_button = tk.Button(self.button_frame, text='Quit', font=('Calibri', 12))
        self.quit_button.pack(side=tk.TOP)

        self.time_frame = tk.Frame(self._master)
        self.time_frame.pack(side=tk.LEFT)
        self.clock_img = Image.open('images/clock.png').resize((50, 65))
        self.clock_img = ImageTk.PhotoImage(self.clock_img)
        self.clock_img_label = tk.Label(self.time_frame, image=self.clock_img)
        self.clock_img_label.pack(side=tk.LEFT)

        self.time_label = tk.Label(self.time_frame, text='Time elapsed', font=('Calibri', 12))
        self.time_label.pack(pady=(15, 0))
        self.time_number_label = tk.Label(self.time_frame, text=self._time_used, font=('Calibri', 12))
        self.time_number_label.pack()

        self.moves_frame = tk.Frame(self._master)
        self.moves_frame.pack(side=tk.LEFT, padx=20)
        self.moves_img = Image.open('images/lightning.png').resize((50, 65))
        self.moves_img = ImageTk.PhotoImage(self.moves_img)
        self.moves_img_label = tk.Label(self.moves_frame, image=self.moves_img)
        self.moves_img_label.pack(side=tk.LEFT)

        self.moves_label = tk.Label(self.moves_frame, text='Moves left', font=('Calibri', 12))
        self.moves_label.pack(pady=(15, 0))
        self.remains_label = tk.Label(self.moves_frame,
                                      font=('Calibri', 12))
        self.remains_label.pack()

        self.life_frame = tk.Frame(self._master)
        self.life_frame.pack(side=tk.LEFT)
        self.life_img = Image.open('images/lives.png').resize((50, 65))
        self.life_img = ImageTk.PhotoImage(self.life_img)
        self.life_img_label = tk.Label(self.life_frame, image=self.life_img)
        self.life_img_label.pack(side=tk.LEFT, padx=10)

        self.life_label = tk.Label(self.life_frame, text='Lives remaining: 3', font=('Calibri', 12))
        self.life_label.pack(pady=(15, 0))
        self.use_life_button = tk.Button(self.life_frame, text='Use life', font=('Calibri', 12))
        self.use_life_button.pack(pady=(0, 5))

        self._time = self.after(1000, self.update_time)

    def update_moves(self, moves):
        """Updates player moves showing on the label when the player moves."""

        self.remains_label.config(text=f"{moves} moves remaining")

    def update_time(self):
        """Updates time of the game play."""

        self._time_used = f'{self._minute} m {self._second} s'
        self._time = self.after(1000, self.update_time)
        self._second += 1
        if self._second // 60:
            self._minute += 1
            self._second = 0
        self.time_number_label.config(text=self._time_used)


    def reset_time(self):
        """Resets the time at initial value."""

        self._second = 1
        self._minute = 0

    def adjust_time(self, new_second, new_minute):
        """Resets the value of the time."""

        self._second = new_second
        self._minute = new_minute

    def get_second(self):
        """Returns the seconds of the game play."""

        return self._second

    def get_minute(self):
        """Returns the minutes of the game play."""

        return self._minute


class AdvancedDungeonMap(AbstractGrid):
    """Draws the advanced dungeon map, every entity is represented by pictures."""

    def __init__(self, master, size, width=600, **kwargs):
        """Constructor of AdvancedDungeonMap class."""
        super().__init__(master, rows=size, cols=size, width=width, height=width, **kwargs)
        self.config(width=width, height=width)
        self._dungeon_size = size
        self._master = master
        self._width = width / size

        grass_img = Image.open('images/empty.gif').resize((int(self._width), int(self._width)))
        self.grass_img = ImageTk.PhotoImage(grass_img)

        wall_img = Image.open('images/wall.gif').resize((int(self._width), int(self._width)))
        self.wall_img = ImageTk.PhotoImage(wall_img)

        key_img = Image.open('images/key.gif').resize((int(self._width), int(self._width)))
        self.key_img = ImageTk.PhotoImage(key_img)

        door_img = Image.open('images/door.gif').resize((int(self._width), int(self._width)))
        self.door_img = ImageTk.PhotoImage(door_img)

        move_increase_img = Image.open('images/moveIncrease.gif').resize((int(self._width), int(self._width)))
        self.move_increase_img = ImageTk.PhotoImage(move_increase_img)

    def draw_grid(self, dungeon, player_position):
        """Draws the dungeon on the AdvancedDungeonMap based on dungeon, and draws the player at the
         specified (row, col) position."""
        self.redraw()

        for i in range(self._dungeon_size):
            for j in range(self._dungeon_size):
                position = (i, j)
                entity = dungeon.get(position)

                self.create_image(self.get_position_center(position), image=self.grass_img)

                if entity is not None:
                    char = entity.get_id()
                    if char == WALL:
                        self.create_image(self.get_position_center(position), image=self.wall_img)
                    elif char == KEY:
                        self.create_image(self.get_position_center(position), image=self.key_img)
                    elif char == DOOR:
                        self.create_image(self.get_position_center(position), image=self.door_img)
                    elif char == MOVE_INCREASE:
                        self.create_image(self.get_position_center(position), image=self.move_increase_img)

                elif position == player_position:
                    player_img = Image.open('images/player.gif').resize((int(self._width), int(self._width)))
                    self.player_img = ImageTk.PhotoImage(player_img)
                    self.create_image(self.get_position_center(position), image=self.player_img)
                else:
                    pass

    def redraw(self):
        """Delete everything on the advanced dungeon map."""
        self.delete(tk.ALL)


class GameApp:
    """Acts as a communicator between the GameLogic and the Display."""

    def __init__(self, master, task=TASK_TWO, dungeon_name="game2.txt"):

        """Constructor of the GameApp class."""
        self._game = GameLogic(dungeon_name)
        self._key_positon = list(self._game.get_game_information().keys())[0]
        self._key = self._game.get_entity(self._key_positon)

        self._master = master
        self._frame = tk.Frame

        map_pad_frame = tk.Frame(master)
        map_pad_frame.pack()

        self._display = None
        self._task = task

        self._dungeon_name = dungeon_name

        self._time_stop = False
        

        if task == TASK_ONE:
            self._dungeon_map = DungeonMap(map_pad_frame, self._game.get_dungeon_size(), bg='light grey')
            self._dungeon_map.pack(side=tk.LEFT)
            self._key_pad = KeyPad(map_pad_frame)
            self._key_pad.pack(side=tk.LEFT)

            self._key_pad.draw_key_grid()
            self._key_pad.bind('<Button-1>', lambda e: self.click_direction(e))
            self.bind_keyboard()

            self._direction = None
            self.draw()

        if task == TASK_TWO:
            self._dungeon_map = AdvancedDungeonMap(map_pad_frame, self._game.get_dungeon_size())
            self._dungeon_map.pack(side=tk.LEFT)

            self._key_pad = KeyPad(map_pad_frame)
            self._key_pad.pack(side=tk.LEFT)

            self._key_pad.draw_key_grid()
            self._key_pad.bind('<Button-1>', lambda e: self.click_direction(e))
            self.bind_keyboard()

            self._direction = None
            self.draw()

            self._status = StatusBar(self._master)
            self._status.pack()
            self._status.update_moves(self._game.get_player().moves_remaining())

            self._status.quit_button.config(command=self.press_quit)
            self._status.new_game_button.config(command=self.press_new_game)

            menubar = tk.Menu(self._master)
            self._master.config(menu=menubar)
            filemenu = tk.Menu(menubar)
            menubar.add_cascade(label='File', menu=filemenu)
            filemenu.add_command(label='New game', command=self.press_new_game)
            filemenu.add_command(label='Load game', command=self.load_saved_game)
            filemenu.add_command(label='Save game', command=self.save_game)
            filemenu.add_command(label='Quit', command=self.press_quit)

            self._filename = None

            game_information = self._game.get_game_information()
            dungeon_size = self._game.get_dungeon_size()
            self._display = Display(game_information, dungeon_size)

        if task == POS_TASK:
            self._dungeon_map = AdvancedDungeonMap(map_pad_frame, self._game.get_dungeon_size())
            self._dungeon_map.pack(side=tk.LEFT)

            self._key_pad = KeyPad(map_pad_frame)
            self._key_pad.pack(side=tk.LEFT)

            self._key_pad.draw_key_grid()
            self._key_pad.bind('<Button-1>', lambda e: self.click_direction(e))
            self.bind_keyboard()

            self._direction = None
            self.draw()

            self._status = PostStatusBar(self._master)
            self._status.pack()
            self._status.update_moves(self._game.get_player().moves_remaining())

            self._status.quit_button.config(command=self.press_quit)
            self._status.new_game_button.config(command=self.press_new_game)
            self._status.use_life_button.config(command=self.use_life)

            menubar = tk.Menu(self._master)
            self._master.config(menu=menubar)
            filemenu = tk.Menu(menubar)
            menubar.add_cascade(label='File', menu=filemenu)
            filemenu.add_command(label='New game', command=self.press_new_game)
            filemenu.add_command(label='Load game', command=self.load_saved_game)
            filemenu.add_command(label='Save game', command=self.save_game)
            filemenu.add_command(label='High scores', command=self.load_high_score)
            filemenu.add_command(label='Quit', command=self.press_quit)

            self._filename = None

            game_information = self._game.get_game_information()
            dungeon_size = self._game.get_dungeon_size()
            self._display = Display(game_information, dungeon_size)

    def bind_keyboard(self):
        """Bind key board with directions."""

        self._master.bind('w', lambda e: self.press('w'))
        self._master.bind('a', lambda e: self.press('a'))
        self._master.bind('s', lambda e: self.press('s'))
        self._master.bind('d', lambda e: self.press('d'))

    def press(self, text):
        """Sets directions for bind key board."""

        if not self._game.won() and not self._game.check_game_over():
            if text == 'w':
                self._direction = 'N'
            if text == 'a':
                self._direction = 'W'
            if text == 's':
                self._direction = 'S'
            if text == 'd':
                self._direction = 'E'
        if self._game.won() or self._game.check_game_over():
            self._direction = None
            raise KeyError('The game has been finished!')
        self.play()

    def click_direction(self, e):
        """Sets directions for key pad."""

        if not self._game.won() and not self._game.check_game_over():
            if e.x > 200/3 and e.x < 2*200/3 and e.y > 0 and e.y < 100/2:
                self._direction = 'N'
            if e.x > 0 and e.x < 200/3 and e.y > 100/2 and e.y < 2*100/2:
                self._direction = 'W'
            if e.x > 200/3 and e.x < 2*200/3 and e.y > 100/2 and e.y < 2 * 100/2:
                self._direction = 'S'
            if e.x > 2*200/3 and e.x < 3*200/3 and e.y > 100/2 and e.y < 2 * 100/2:
                self._direction = 'E'
            if e.x >= 0 and e.x < 200/3 and e.y > 0 and e.y < 100/2:
                self._direction = None
                raise KeyError('Invalid action!')
            if e.x > 2*200/3 and e.x <= 3*200 / 3 and e.y > 0 and e.y < 100 / 2:
                self._direction = None
                raise KeyError('Invalid action!')
        if self._game.won() or self._game.check_game_over():
            self._direction = None
            raise KeyError('The game has been finished!')
        self.play()

    def play(self):
        """Handles the player interaction."""

        player = self._game.get_player()
        if not self._game.collision_check(self._direction):
            self._game.move_player(self._direction)
            entity = self._game.get_entity(player.get_position())
            player.change_move_count(-1)
            if entity is not None:
                entity.on_hit(self._game)
                if self._game.won():
                    self.draw()

                    if self._task == TASK_ONE:
                        messagebox.showinfo('You won!', 'You have finished the level!')

                    if self._task == TASK_TWO:
                        self._status.update_moves(self._game.get_player().moves_remaining())
                        self._status.after_cancel(self._status._time)

                        if messagebox.askyesno('You won!', 'You have finished the level with a score of ' +
                                               f'{int(self._status.get_minute())*60+int(self._status.get_second())}' + '\n' + 'Would you like to play again?'):
                            self.press_new_game()
                            self._status.update_time()
                        else:
                            self._time_stop = True

                    if self._task == POS_TASK:
                        self._status.update_moves(self._game.get_player().moves_remaining())
                        self._status.after_cancel(self._status._time)

                        self._time_stop = True

                        self._win_window = tk.Toplevel(self._master)
                        self._win_window.title('You win!')

                        win_label = tk.Label(self._win_window,
                                             text=f'You won in {self._status.get_minute()}m '
                                                  f'and {self._status.get_second()}s! Enter your name:',
                                             font=('Calibri', 15))
                        win_label.pack(side=tk.TOP)

                        self._name_input_box = tk.Entry(self._win_window)
                        self._name_input_box.pack(side=tk.TOP, expand=1)

                        finish_button = tk.Button(self._win_window, text='Enter', font=('Calibri', 12))
                        finish_button.pack(side=tk.TOP)
                        finish_button.config(command=self.save_high_score)

                    return

            if self._game.check_game_over():
                self.draw()
                if self._task == TASK_ONE:
                    messagebox.showinfo('You fail!', 'You have lost all your strength and honour.')
                if self._task == TASK_TWO or self._task == POS_TASK:
                    self._status.update_moves(self._game.get_player().moves_remaining())
                    self._status.after_cancel(self._status._time)
                    if messagebox.askyesno('You fail!',
                                           'You have lost all your strength and honour.' + '\n'
                                           + 'Would you like to play again?'):
                        self.press_new_game()
                        self._status.update_time()
                    else:
                        self._time_stop = True
                return

        else:
            player.change_move_count(-1)
            if self._game.check_game_over():
                self.draw()
                if self._task == TASK_ONE:
                    messagebox.showinfo('You fail!', 'You have lost all your strength and honour.')
                if self._task == TASK_TWO or self._task == POS_TASK:
                    self._status.update_moves(self._game.get_player().moves_remaining())
                    self._status.after_cancel(self._status._time)
                    if messagebox.askyesno('You fail!',
                                           'You have lost all your strength and honour.' + '\n'
                                           + 'Would you like to play again?'):
                        self.press_new_game()
                        self._status.update_time()
                    else:
                        self._time_stop = True
                return

        self.draw()


        if self._task == TASK_TWO or self._task == POS_TASK:
            self._status.update_moves(self._game.get_player().moves_remaining())

    def draw(self):
        """Displays the dungeon with all Entities in their positions."""

        self._dungeon_map.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())

    def press_quit(self):
        """Quits the game."""

        if messagebox.askyesno('Quit?', 'Are you sure you want to quit?'):
            self._master.destroy()

    def press_new_game(self):
        """Restarts a new game."""

        self._game = GameLogic(self._dungeon_name)
        self._status.reset_time()
        if self._time_stop == True:
            self._status.update_time()
            self._time_stop = False
        self._status.update_moves(self._game.get_player().moves_remaining())
        self._dungeon_map.redraw()
        self._dungeon_map.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())
        game_information = self._game.get_game_information()
        dungeon_size = self._game.get_dungeon_size()
        self._display = Display(game_information, dungeon_size)

    def save_game(self):
        """Save the current game data."""

        file_format = [('Text Files', '*.txt')]
        if not self._game.won() and not self._game.check_game_over():
            filename = filedialog.asksaveasfilename(filetypes=file_format, defaultextension=file_format)
            if filename:
                self._filename = filename
            if self._filename:
                fd = open(self._filename, 'w')
                fd.write(f'game name: {self._dungeon_name}' + '\n')
                fd.write(f'second: {self._status.get_second()}' + '\n')
                fd.write(f'minute: {self._status.get_minute()}' + '\n')
                fd.write(f'moves remaining: {self._game.get_player().moves_remaining()}' + '\n')
                fd.write(f'player inventory: {self._game.get_player().get_inventory()}' + '\n')
                fd.write(self._display.display_game(self._game.get_player().get_position()))
        else:
            messagebox.showerror('Error', 'The game is finished! ' + '\n'
                                'You can only save your game while the game is running(when you are playing)!')

    def read_saved_game(self, filename):
        """Read from saved game data."""
        player = self._game.get_player()

        if filename:
            self._filename = filename
            fd = open(filename, 'r')

            lines = fd.readlines()

            second = int(lines[1].split(':')[1].strip())
            minute = int(lines[2].split(':')[1].strip())
            moves_remaining = int(lines[3].split(':')[1].strip())
            player_inventory = lines[4].split(':')[1].strip()

            if player_inventory != []:
                self._game.get_player().add_item(self._key)

            new_dungeon = load_game_for_saved(filename)
            new_dungeon_name = lines[0].split(':')[1].strip()

            if new_dungeon_name != self._dungeon_name:
                messagebox.showerror('Error',
                                     'You have selected a file which has a different dungeon map!')

            if new_dungeon_name == self._dungeon_name:
                self._status.adjust_time(second, minute)
                player.adjust_moves(moves_remaining)
                self._status.update_moves(self._game.get_player().moves_remaining())
                self._game.adjust_game_logic(new_dungeon)
                self.draw()

            fd.close()


    def load_saved_game(self):
        """Load from saved game data and replace current data with them."""

        player = self._game.get_player()

        if not self._game.won() and not self._game.check_game_over():
            filename = filedialog.askopenfilename()

            self.read_saved_game(filename)

        if self._game.won():

            self._game.set_win(False)
            filename = filedialog.askopenfilename()

            self.read_saved_game(filename)

            if self._time_stop == True:
                self._status.update_time()
                self._time_stop = False

        if self._game.check_game_over():
            self._game.check_game_over()
            filename = filedialog.askopenfilename()

            self.read_saved_game(filename)

            if self._time_stop == True:
                self._status.update_time()
                self._time_stop = False

    def save_high_score(self):
        """Saves high score data into high_scores.txt."""

        player_name = self._name_input_box.get()

        filename = 'high_scores.txt'

        if filename:
            fd = open(filename, 'a')
            fd.write(f'{player_name}: ' + f'{self._status.get_second() + 60 * self._status.get_minute()}' + '\n')
            fd.close()
        else:
            self.create_score_file()

        self._win_window.destroy()

    def create_score_file(self):
        """Creates a txt file if the high_scores.txt does not exists."""

        filename = 'high_scores.txt'
        fd = open(filename, 'w')
        fd.close()

    def read_high_scores(self):
        """Reads high score data from high_scores.txt."""

        filename = 'high_scores.txt'

        players_and_scores = {}
        fd = open(filename, 'r')
        i = 0
        player_score_less_than_three = ''
        player_score = []

        lines = fd.readlines()

        if len(lines) <= 3:
            for line in lines[0:]:
                player_score_less_than_three += line
            return player_score_less_than_three

        if len(lines) > 3:
            for line in lines:
                player_name = str(lines[i].strip().split(':')[0])
                player_score.append(int(lines[i].strip().split(':')[1].strip()))
                single_player_score = int(lines[i].strip().split(':')[1].strip())
                single_name_and_score = {player_name: single_player_score}
                players_and_scores.update(single_name_and_score)
                i += 1

            player_score.sort()
            ordered_name_and_scores = sorted(players_and_scores.items(), key=lambda item: item[1])
            top_players = ordered_name_and_scores[0:3]
            first_player_name = top_players[0][0]
            first_player_score = top_players[0][1]
            second_player_name = top_players[1][0]
            second_player_score = top_players[1][1]
            third_player_name = top_players[2][0]
            third_player_score = top_players[2][1]

            high_scores = first_player_name + ': ' + str(first_player_score) +'\n' \
                        + second_player_name + ': ' + str(second_player_score) +'\n' \
                        +third_player_name + ': ' + str(third_player_score) +'\n'

            return high_scores

    def load_high_score(self):
        """Loads and shows high score."""

        high_score_window = tk.Toplevel(self._master)
        high_score_window.resizable(0, 0)
        high_score_window.title('High scores')
        top_label = tk.Label(high_score_window, text='High scores', bg='Medium spring green', font=('Calibri', 28))
        top_label.pack(side=tk.TOP)
        score_label = tk.Label(high_score_window, font=('Calibri', 15))
        score_label.pack(side=tk.TOP)
        score_label.config(text=self.read_high_scores())

    def use_life(self):
        """Using life to let player go back to last step."""
        pass


def main():
    root = tk.Tk()
    root.title('Key Cave Adventure Game')
    root.resizable(0, 0)
    label = tk.Label(root, text='Key Cave Adventure Game', bg='Medium spring green', font=('Calibri', 28))
    label.pack(fill=tk.X)
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

