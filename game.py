# Author: Mostafa Mahmoud Ibrahim
# Email: mostafa_mahmoud@protonmail.com

import random
import time
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput


class MineSweeperGame(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.intro_screen = IntroScreen(name='intro')
        self.game_screen = GameScreen(name='game')
        self.score_screen = ScoreScreen(name='score')

        self.game_screen.init(5, 5, 3)

        # self.add_widget(self.intro_screen)
        self.add_widget(self.game_screen)
        self.add_widget(self.score_screen)


class IntroScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.my_root_widget = BoxLayout(spacing=10, padding=100, orientation='vertical')
        self.play_button = Button(text="Play")
        self.play_button.bind(on_press=self.start_game)
        self.length_label = Label(text="Length")
        self.width_label = Label(text="Width")
        self.bombs_count_label = Label(text="Bombs Count")
        self.length_input = TextInput(text='', multiline=False)
        self.width_input = TextInput(text='', multiline=False)
        self.bombs_count_input = TextInput(text='', multiline=False)
        self.my_root_widget.add_widget(self.length_label)
        self.my_root_widget.add_widget(self.length_input)
        self.my_root_widget.add_widget(self.width_label)
        self.my_root_widget.add_widget(self.width_input)
        self.my_root_widget.add_widget(self.bombs_count_label)
        self.my_root_widget.add_widget(self.bombs_count_input)
        self.my_root_widget.add_widget(self.play_button)
        self.add_widget(self.my_root_widget)

    def start_game(self, _):
        print("Play Button Was clicked")
        print("Length: " + self.length_input.text)
        print("Width: " + self.width_input.text)
        print("Bombs Count: " + self.bombs_count_input.text)
        length = self.length_input.text
        width = self.width_input.text
        bombs_count = self.bombs_count_input.text
        if not length.isnumeric() or not width.isnumeric() or not bombs_count.isnumeric() \
                or int(length) <= 0 or int(width) <= 0 or int(bombs_count) <= 0:
            return
        length = int(length)
        width = int(width)
        bombs_count = int(bombs_count)
        game_screen_name = 'game'
        game_screen = self.manager.get_screen(game_screen_name)

        # testing
        # print(type(length), length)
        # print(type(width), width)
        # game_screen.init(6, 6)

        game_screen.init(length, width, bombs_count)
        self.manager.current = game_screen_name


class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.my_root_widget = None
        self.tile_list = None
        self.rows = None
        self.cols = None
        self.remaining_tiles_count = None
        self.bombs_count = None
        self.game_started = False
        self.start_time = None

    def init(self, length, width, bombs_count):
        self.rows = length
        self.cols = width
        self.remaining_tiles_count = width * length
        # create root layout
        self.my_root_widget = GridLayout(cols=width, rows=length)
        # generate the random bombs
        self.bombs_count = bombs_count
        bombs = list(range(width * length))
        random.shuffle(bombs)
        bombs = bombs[:self.bombs_count]

        # testing
        print("Bomb locations: " + " ".join(map(str, bombs)))

        # create list of tiles
        self.tile_list = [Tile(self, i) for i in range(width * length)]
        for bomb_index in bombs:
            # set tile as bomb
            self.tile_list[bomb_index].set_bomb()
            # increment the number of the neighbour tiles
            top, bottom, left, right = bomb_index-1, bomb_index+1, bomb_index-length, bomb_index+length
            if top >= 0 and top % self.rows != self.rows - 1:
                self.tile_list[top].number += 1
            if bottom <= width * length-1 and bottom % self.rows != 0:
                self.tile_list[bottom].number += 1
            if left >= 0:
                self.tile_list[left].number += 1
            if right <= width * length - 1:
                self.tile_list[right].number += 1
        # populate the layout
        for tile in self.tile_list:
            self.my_root_widget.add_widget(tile)
        self.add_widget(self.my_root_widget)

    def on_press_callback(self, index):
        score_screen_name = 'score'
        # start the timer
        if not self.game_started:
            self.start_time = time.time()
            self.game_started = True

        if self.tile_list[index].is_bomb():
            # user lost the game
            game_screen = self.manager.get_screen(score_screen_name)
            game_screen.init_lost_screen(time.time() - self.start_time)
            self.manager.current = score_screen_name
        else:
            self.expand(self.tile_list[index], self.rows, root=True)
            if self.remaining_tiles_count == self.bombs_count:
                # user won the game
                game_screen = self.manager.get_screen(score_screen_name)
                game_screen.init_win_screen(time.time() - self.start_time)
                self.manager.current = score_screen_name

    def expand(self, tile, length, root=False):
        if tile.is_visited():
            return
        elif tile.is_neighbour() and not root:
            tile.show_number()
            tile.set_visited()
            self.remaining_tiles_count -= 1
            return
        else:
            tile.show_number()
            tile.set_visited()
            self.remaining_tiles_count -= 1
            index = tile.get_tile_index()
            top, bottom, left, right = index-1, index+1, index-length, index+length
            if top >= 0 and top % self.rows != self.rows - 1 and not self.tile_list[top].is_bomb():
                self.expand(self.tile_list[top], length)
            if bottom <= self.cols * length-1 and bottom % self.rows != 0 and not self.tile_list[bottom].is_bomb():
                self.expand(self.tile_list[bottom], length)
            if left >= 0 and not self.tile_list[left].is_bomb():
                self.expand(self.tile_list[left], length)
            if right <= self.cols * length - 1 and not self.tile_list[right].is_bomb():
                self.expand(self.tile_list[right], length)


class Tile(Button):
    def __init__(self, game, index, is_bomb_flag=False, number=0, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.tile_index = index
        self.is_bomb_flag = is_bomb_flag
        self.number = number
        self.text = ''
        self.visited = False

    def set_bomb(self):
        self.is_bomb_flag = True

    def is_bomb(self):
        return self.is_bomb_flag

    def on_press(self):
        self.game.on_press_callback(self.tile_index)

    def get_tile_index(self):
        return self.tile_index

    def show_number(self):
        self.text = '' if self.number == 0 else str(self.number)
        self.disabled = True

    def is_visited(self):
        return self.visited

    def set_visited(self):
        self.visited = True

    def is_neighbour(self):
        return True if self.number > 0 else False


class ScoreScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def init_lost_screen(self, score):
        my_root_layout = BoxLayout(spacing=10, padding=200, orientation='vertical')
        my_root_layout.add_widget(Label(text="YOU LOST"))
        my_root_layout.add_widget(Label(text="Your Score is " + str(score)))
        self.add_widget(my_root_layout)

    def init_win_screen(self, score):
        my_root_layout = BoxLayout(spacing=10, padding=200, orientation='vertical')
        my_root_layout.add_widget(Label(text="Congrats"))
        my_root_layout.add_widget(Label(text="You Finished Them All In " + str(score)))
        self.add_widget(my_root_layout)


class MineSweeperApp(App):
    def build(self):
        return MineSweeperGame()


if __name__ == '__main__':
    MineSweeperApp().run()
