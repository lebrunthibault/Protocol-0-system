from typing import Tuple

from lib.enum.abstract_enum import AbstractEnum

RGBColor = Tuple[int, int, int]


class PixelColorEnum(AbstractEnum):
    """used when doing dynamic color detection"""

    @classmethod
    def hex_to_rgb(cls, color):
        # type: (str) -> RGBColor
        return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))

    @property
    def rgb(self):
        # type: () -> RGBColor
        return PixelColorEnum.hex_to_rgb(self.value)

    BUTTON_ACTIVATED = "FFA608"
    BUTTON_NOT_SHOWN = "C3C3C3"
    BUTTON_DEACTIVATED = "A5A5A5"

    BROWSER = "878787"
    BROWSER_SELECTED_DIM = "BFAB7A"
    BROWSER_SELECTED_DIMMER = "A8BBC4"

    TRACK_FOCUSED = "FF39D4"
    TRACK_SELECTED = "C7EDFF"
    TRACK_CONTEXT_MENU_BACKGROUND = "C3C3C3"

    EXPLORER_ABLETON_SET_ICON = "222222"

    # needed for closest color detection
    SEPARATOR = "4B4B4B"
    LEFT_SIZE = "6E6E6E"

    @property
    def is_button_activated(self) -> bool:
        return self in (PixelColorEnum.BUTTON_ACTIVATED, PixelColorEnum.BUTTON_NOT_SHOWN)

    @property
    def is_browser_shown(self) -> bool:
        return self in (
            PixelColorEnum.BROWSER,
            PixelColorEnum.BROWSER_SELECTED_DIM,
            PixelColorEnum.BROWSER_SELECTED_DIMMER,
        )