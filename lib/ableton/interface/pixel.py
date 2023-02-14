from typing import List, Optional

from PIL import ImageGrab

from api.settings import Settings
from lib.ableton.interface.coords import Coords, RectCoords
from lib.ableton.interface.pixel_color_enum import PixelColorEnum
from lib.errors.Protocol0Error import Protocol0Error
from lib.window.window import get_window_position

settings = Settings()


def get_coords_for_color(
    colors: List[PixelColorEnum], bbox: RectCoords = None, box_boundary="left"
) -> Coords:
    assert box_boundary in ("left", "right"), "Invalid box boundary"
    screen = ImageGrab.grab(bbox=bbox)

    colors_rgb = [c.rgb for c in colors]
    x1, y1, x2, _ = bbox
    width = x2 - x1

    pixels = list(enumerate(screen.getdata()))
    for i, color in pixels[::20]:
        if color not in colors_rgb:
            continue

        if box_boundary == "right":
            while True:
                if color not in colors_rgb:
                    break
                i += 1
                color = pixels[i]

        return ((i % width) + x1, (i // width) + y1)

    raise Protocol0Error("color not found in screen")


def get_absolute_coords(handle: int, coords: Coords) -> Coords:
    (x, y, w, h) = get_window_position(handle)
    (x_coords, y_coords) = coords

    x_coords *= settings.display_resolution_factor
    y_coords *= settings.display_resolution_factor

    return (x + x_coords, y + y_coords)


def get_pixel_color_at(coords: Coords) -> Optional[PixelColorEnum]:
    image = ImageGrab.grab()
    pixel_color = image.getpixel(coords)

    for color_enum in PixelColorEnum:
        if color_enum.rgb == pixel_color:
            return color_enum

    return None


def get_pixel_having_color(
    coords_list: List[Coords], color_enum: PixelColorEnum
) -> Optional[Coords]:
    image = ImageGrab.grab()

    for coords in coords_list:
        if image.getpixel(coords) == color_enum.rgb:
            return coords

    return None
