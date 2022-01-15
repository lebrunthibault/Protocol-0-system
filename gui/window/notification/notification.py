from typing import Optional

import PySimpleGUI as sg
import pyautogui

from gui.window.window import Window
from lib.enum.ColorEnum import ColorEnum


class Notification(Window):
    def __init__(
        self,
        message: str,
        background_color: Optional[ColorEnum],
        no_titlebar=True
    ):
        background_color = background_color.hex_value if background_color else None
        self.message = message

        self.sg_window = sg.Window("Message window",
                                layout=[[sg.Text(message, background_color=background_color)]],
                                no_titlebar=no_titlebar,
                                location=(pyautogui.size()[0] - (80 + 7 * len(message)), 10),
                                background_color=background_color,
                                keep_on_top=True,
                                modal=False,
                                )

    def display(self):
        self.sg_window.read(timeout=0)
