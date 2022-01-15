from typing import List, Tuple

import PySimpleGUI as sg
from PySimpleGUI import Button, BLUES

from gui.window.window import Window


class Select(Window):
    def __init__(self, message: str, options: List[str], buttons: List[List[Button]], arrow_keys: Tuple[str]):
        layout = [
            [sg.Text(message, key="question")],
            [sg.Input(key="input", visible=False)],
            *buttons
        ]
        self.arrow_keys = arrow_keys

        self.sg_window = sg.Window(
            "Select Window",
            layout,
            modal=True,
            return_keyboard_events=True,
            keep_on_top=True,
            no_titlebar=True,
            element_justification='c'
        )
        self.options = options
        self.selected_option = options[0]

    def display(self):
        while True:
            event, values = self.sg_window.read()

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if isinstance(event, str):
                key = event.split(":")[0]
                if key == "Escape":
                    break
                elif key in self.arrow_keys:
                    self._scroll_selected_option(go_next=key == self.arrow_keys[1])
                elif event in self.options:
                    break
                elif len(event) == 1 and ord(event) == 13:
                    break

        self.notify(self.selected_option)

    def _scroll_selected_option(self, go_next=True):
        increment = 1 if go_next else -1
        index = (self.options.index(self.selected_option) + increment) % len(self.options)
        self.sg_window[self.selected_option].update(button_color=('white', BLUES[0]))
        self.selected_option = self.options[index]
        self.sg_window[self.selected_option].update(button_color=('white', BLUES[1]))