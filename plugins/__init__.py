import requests
from telethon.tl import functions, types
from telethon import Button, events

from belethon.decorators.command import belethon_cmd
from belethon.decorators.asstbot import in_pattern, tgbot_cmd, callback
from belethon.decorators import eor, eod
from belethon.core.helper import time_formatter
from belethon.helper import inline_mention, fetch, create_quotly, download_yt, get_yt_link, is_url_work, mediainfo
from belethon import *


NAME = OWNER_NAME = JmdB.get_key("NAME")
LOG_CHAT = JmdB.get_config("LOG_CHAT")
DEV_CHAT = [-1001632670555]
DEVLIST = [7993030462]


def inline_pic(get=False):
    INLINE_PIC = JmdB.get_key("INLINE_PIC")
    if (INLINE_PIC is None) or get:
        return "https://f.top4top.io/p_3302n15i01.jpg"
    elif INLINE_PIC:
        return INLINE_PIC


def up_catbox(file_path, userhash=None):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "userhash": userhash}

    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
