import glob
import os.path
import re
from os.path import dirname
from typing import List, Dict, Optional

from loguru import logger
from pydantic import BaseModel

from api.client.p0_script_api_client import p0_script_client_from_http
from api.settings import Settings
from gui.celery import notification_window
from lib.ableton.ableton import is_ableton_focused
from lib.ableton.get_set import (
    _get_window_title_from_filename,
    get_launched_sets,
    get_last_launched_track_set,
)
from lib.enum.NotificationEnum import NotificationEnum
from lib.window.window import get_focused_window_title
from protocol0.application.command.ActivateSetCommand import ActivateSetCommand

settings = Settings()


class AbletonSet(BaseModel):
    def __repr__(self):
        star = "*" if self.active else ""
        return f"AbletonSet('{star}{self.title}')"

    def __str__(self):
        return self.__repr__()

    id: str
    active: bool
    path: Optional[str]  # computed only by the backend
    title: Optional[str]  # computed only by the backend
    muted: bool
    current_track_name: str
    current_track_type: str
    current_track_is_grouped: bool
    drum_rack_visible: bool
    room_eq_enabled: bool

    @property
    def is_unknown(self):
        return self.title is None or self.title == "Untitled"

    @property
    def set_folder(self):
        return dirname(self.path)

    @property
    def has_backup(self) -> bool:
        sub_folder_path = self.set_folder.replace(settings.ableton_set_directory, "")
        backup_sets = glob.glob(
            f"{settings.ableton_set_directory}\\Backup\\{sub_folder_path}\\*.als"
        )
        return len(backup_sets) != 0

    @property
    def saved_tracks(self) -> List:
        tracks_folder = f"{self.set_folder}\\tracks"
        if not os.path.exists(tracks_folder):
            notification_window.delay(
                "No track folder",
                notification_enum=NotificationEnum.ERROR.value,
                centered=True,
            )
            return []

        return glob.glob(f"{tracks_folder}\\*.als")

    @property
    def last_saved_track(self) -> str:
        return max(self.saved_tracks, key=os.path.getatime)

    def set_path(self, path: str):
        self.path = path
        self.title = _get_window_title_from_filename(path)


class AbletonSetManager:
    DEBUG = True

    @classmethod
    async def register(cls, ableton_set: AbletonSet):
        if ableton_set.is_unknown:
            ableton_set.set_path(get_last_launched_track_set())

        # cleaning here in case a closed set didn't notify
        launched_sets = get_launched_sets()
        for ss in cls.all():
            if next(filter(lambda s: ss.title in s, launched_sets), None) is None:  # type: ignore
                await cls.remove(ss.id)

        # deduplicate on set title
        existing_set = cls.from_title(str(ableton_set.title))

        _ableton_set_registry[ableton_set.id] = ableton_set
        if cls.DEBUG:
            logger.info(f"registering set {ableton_set}, existing: {existing_set is not None}")

        if existing_set is not None and existing_set.id != ableton_set.id:
            await cls.remove(existing_set.id)
        if existing_set is None:
            # it's an update
            await cls.sync(active_set=ableton_set)

    @classmethod
    async def remove(cls, id: str):
        if cls.DEBUG:
            logger.info(f"removing {id}")

        if id in _ableton_set_registry:
            del _ableton_set_registry[id]

            # pass the active state to another set
            other_set = next(iter(cls.all()), None)
            if other_set is not None:
                await cls.sync(other_set, force_log=True)

    @classmethod
    def get(cls, id: str) -> AbletonSet:
        return _ableton_set_registry[id]

    @classmethod
    def active(cls) -> Optional[AbletonSet]:
        active_set = next(filter(lambda s: s.active, cls.all()), None)  # type: ignore

        if active_set is None:
            notification_window.delay("No active set")

        return active_set

    @classmethod
    def from_title(cls, title: str) -> Optional[AbletonSet]:
        return next(filter(lambda s: s.title == title, cls.all()), None)  # type: ignore

    @classmethod
    def all(cls) -> List[AbletonSet]:
        return list(_ableton_set_registry.values())

    @classmethod
    def clear(cls):
        for set in cls.all():
            cls.remove(set.id)

    @classmethod
    async def sync(cls, active_set: AbletonSet = None, force_log=False) -> None:
        active_set = active_set or get_focused_set()

        if active_set is None:
            notification_window.delay("No set focused", NotificationEnum.WARNING.value)
            return

        for ss in cls.all():
            ss.active = ss == active_set
            command = ActivateSetCommand(ss.active)
            command.set_id = ss.id
            p0_script_client_from_http().dispatch(command, log=False)

        from api.http_server.ws import ws_manager

        await ws_manager.broadcast_server_state()

        if len(cls.all()) > 1 or force_log:
            logger.info(f"Activated '{active_set.title}'")
        else:
            logger.info("Only one set launched")


# in-memory registry
_ableton_set_registry: Dict[str, AbletonSet] = {}


def get_focused_set_title() -> Optional[str]:
    if not is_ableton_focused():
        return None

    title = get_focused_window_title()

    match = re.match("([^[*]*)\*?\s*(\[[^[]*])? - Ableton Live.*", title)

    if match is None:
        return None

    return match.group(1).strip()


def get_focused_set() -> Optional[AbletonSet]:
    set_title = get_focused_set_title()
    if set_title is None:
        return None

    return AbletonSetManager.from_title(set_title)
