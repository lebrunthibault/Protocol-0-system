from typing import List, Dict

import mido
from loguru import logger
from p0_backend_client import P0BackendClient
from protocol0.application.command.SerializableCommand import SerializableCommand

from config import Config
from lib.utils import make_sysex_message_from_dict, make_sysex_message_from_command


class BackendClientMessageSender():
    AWAITING_MESSAGES: List[Dict] = []

    def send_message(self, message: Dict):
        from api.midi_server.main import get_output_port
        out_port = get_output_port(Config.P0_BACKEND_LOOPBACK_NAME)
        with mido.open_output(out_port, autoreset=False) as midi_port:
            msg = make_sysex_message_from_dict(message)
            midi_port.send(msg)
            logger.info(f"sent msg to p0_backend via P0_BACKEND_LOOPBACK: {message}")


backend_client = P0BackendClient(BackendClientMessageSender())


def dispatch_to_script(command: SerializableCommand):
    from api.midi_server.main import get_output_port
    out_port = get_output_port(Config.P0_BACKEND_LOOPBACK_NAME)
    with mido.open_output(out_port, autoreset=False) as midi_port:
        msg = make_sysex_message_from_command(command)
        midi_port.send(msg)
        logger.info(f"sent script command to p0_backend via P0_BACKEND_LOOPBACK: {command}")