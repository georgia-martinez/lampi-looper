from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from enum import Enum

class Color(Enum):
    GRAY = (0.5, 0.5, 0.5, 1)
    RED = (1, 0, 0, 1)
    GREEN = (0, 1, 0, 1)
    BLUE = (0, 0, 1, 1)

class BeatButton(Button):
    def __init__(self, **kwargs):
        super(BeatButton, self).__init__(**kwargs)

        self.colors = [
            Color.GRAY,
            Color.RED,
            Color.GREEN,
            Color.BLUE,
        ]

        print(Color.GRAY.value)

        self.color_id = 0
        self.curr_color = Color.GRAY
        self._toggle_color()

    def on_press(self):
        if self.color_id != len(self.colors) - 1:
            self.color_id += 1
        else:
            self.color_id = 0

        self._toggle_color()

    def _toggle_color(self):
        new_color = self.colors[self.color_id]

        self.background_color = new_color.value
        self.curr_color = new_color

class GridLayoutExample(GridLayout):
    def __init__(self, **kwargs):
        super(GridLayoutExample, self).__init__(**kwargs)
        self.cols = 4
        self.spacing = 5

        for i in range(16):
            btn = BeatButton(background_color=(1, 1, 1, 1))
            self.add_widget(btn)

class LampiApp(App):
    def build(self):
        return GridLayoutExample()
