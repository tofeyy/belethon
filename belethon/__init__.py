import logging
import time
import sys
import belethon.core.ubclient
from .config import Var
from .core.client import belethonClient
from .core.session import both_session
from .core.logger import *
from database import jmdB, JmdB

version = "1.0.0"
start_time = time.time()
bot_token = JmdB.get_config("BOT_TOKEN")


jmubot = belethon_bot = belethonClient(
        session=both_session(Var.SESSION, LOGS),
        app_version=version,
        device_model="belethon",
       )


tgbot = asst = belethonClient("Tgbot", bot_token=bot_token)

del bot_token


HNDLR = jmdB.get_key("HNDLR") or "."
SUDO_HNDLR = jmdB.get_key("SUDO_HNDLR") or HNDLR
