import tkinter as tk
import random
from dir_consts import *
from gamelib import Sprite, GameApp, Text
from maze import Maze

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

UPDATE_DELAY = 33

PACMAN_SPEED = 5


class Pacman(Sprite):
    def __init__(self, app, maze, r, c):
        self.r = r
        self.c = c
        self.maze = maze

        self.direction = DIR_STILL
        self.next_direction = DIR_STILL

        x, y = maze.piece_center(r, c)
        super().__init__(app, 'images/pacman.png', x, y)
        self.dot_eaten_observers = []

        self.state = NormalPacmanState(self)

    def update(self):
        if self.maze.is_at_center(self.x, self.y):
            r, c = self.maze.xy_to_rc(self.x, self.y)

            if self.maze.has_dot_at(r, c):
                self.maze.eat_dot_at(r, c)
                for i in self.dot_eaten_observers:
                    i()

                # we randomly set is_super_speed with probability 0.1, we also restart the counter
                self.state.random_upgrade()

            if self.maze.is_movable_direction(r, c, self.next_direction):
                self.direction = self.next_direction
            else:
                self.direction = DIR_STILL
        
        # we update the location with the new speed variable
        self.state.move_pacman()


    def set_next_direction(self, direction):
        self.next_direction = direction


class PacmanGame(GameApp):
    def init_game(self):
        self.maze = Maze(self, CANVAS_WIDTH, CANVAS_HEIGHT)

        self.pacman1 = Pacman(self, self.maze, 1, 1)
        self.pacman2 = Pacman(self, self.maze, self.maze.get_height() - 2, self.maze.get_width() - 2)

        self.pacman1_score_text = Text(self, 'P1: 0', 100, 20)
        self.pacman2_score_text = Text(self, 'P2: 0', 600, 20)

        self.elements.append(self.pacman1)
        self.elements.append(self.pacman2)

        self.pacman1_score = 0
        self.pacman2_score = 0
        self.pacman1.dot_eaten_observers.append(self.dot_eaten_by_pacman1)
        self.pacman2.dot_eaten_observers.append(self.dot_eaten_by_pacman2)

        self.command_map = {
            'W' : self.get_pacman_next_direction_function(self.pacman1, DIR_UP),
            'A' : self.get_pacman_next_direction_function(self.pacman1, DIR_LEFT),
            'S' : self.get_pacman_next_direction_function(self.pacman1, DIR_DOWN),
            'D' : self.get_pacman_next_direction_function(self.pacman1,DIR_RIGHT),
            'I' : self.get_pacman_next_direction_function(self.pacman2, DIR_UP),
            'J' : self.get_pacman_next_direction_function(self.pacman2, DIR_LEFT),
            'K' : self.get_pacman_next_direction_function(self.pacman2, DIR_DOWN),
            'L' : self.get_pacman_next_direction_function(self.pacman2, DIR_RIGHT),
        }

    def update_scores(self):
        self.pacman1_score_text.set_text(f'P1: {self.pacman1_score}')
        self.pacman2_score_text.set_text(f'P2: {self.pacman2_score}')

    def dot_eaten_by_pacman1(self):
        self.pacman1_score += 1
        self.update_scores()

    def dot_eaten_by_pacman2(self):
        self.pacman2_score += 1
        self.update_scores()

    def pre_update(self):
        pass

    def post_update(self):
        pass

    def on_key_pressed(self, event):
        ch = event.char.upper()
        if ch in self.command_map:
            self.command_map[ch]()
    
    def get_pacman_next_direction_function(self, pacman, next_direction):

        def f():
            pacman.set_next_direction(next_direction)

        return f


class NormalPacmanState:
    def __init__(self, pacman):
        self.pacman = pacman

    def random_upgrade(self):
        if random.random() < 0.1:
            self.pacman.state = SuperPacmanState(self.pacman)

    def move_pacman(self):
        pacman = self.pacman
        speed = PACMAN_SPEED
        pacman.x += speed * DIR_OFFSET[pacman.direction][0]
        pacman.y += speed * DIR_OFFSET[pacman.direction][1]


class SuperPacmanState:
    def __init__(self, pacman):
        self.pacman = pacman
        self.super_speed_counter = 0

    def random_upgrade(self):
        pass

    def move_pacman(self):
        pacman = self.pacman
        speed = 2 * PACMAN_SPEED
        pacman.x += speed * DIR_OFFSET[pacman.direction][0]
        pacman.y += speed * DIR_OFFSET[pacman.direction][1]

        self.super_speed_counter += 1
        
        if self.super_speed_counter > 50:
            self.pacman.state = NormalPacmanState(pacman)
        

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Monkey Banana Game")

    # do not allow window resizing
    root.resizable(False, False)
    app = PacmanGame(root, CANVAS_WIDTH, CANVAS_HEIGHT, UPDATE_DELAY)
    app.start()
    root.mainloop()
