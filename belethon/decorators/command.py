import asyncio
import re 
import os
import sys
import traceback
from functools import wraps
from html import escape
from time import gmtime, strftime
from traceback import format_exc

from telethon import Button
from telethon import __version__ as telever
from telethon import events
from telethon.errors.common import AlreadyInConversationError
from telethon.errors.rpcerrorlist import (
    AuthKeyDuplicatedError,
    BotInlineDisabledError,
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageDeleteForbiddenError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserIsBotError,
)
from telethon.events import MessageEdited, NewMessage
from telethon.tl.custom import Message
from telethon.utils import get_display_name

from belethon import *

from resources import DEVLIST, LIST
from ..helper import bash, make_html_telegraph as mkgraph
from ..core.helper import time_formatter as tf
from . import fullsudos, owner_and_sudos, StatsHolder
from . import should_allow_sudos as allow_sudo
from .manager import eod

TAKE_EDITS = jmdB.get_key("TAKE_EDITS")
black_list_chats = jmdB.get_key("BLACKLIST_CHATS")



def compile_pattern(data, hndlr):
    if data.startswith("^"):
        data = data[1:]
    if data.startswith("."):
        data = data[1:]
    if hndlr in [" ", "NO_HNDLR"]:
        return re.compile(f"^{data}")
    return re.compile("\\" + hndlr + data)


def belethon_cmd(pattern=None, tgbot=tgbot, **kwargs):
    reply_req = kwargs.get("replied", False)
    owner_only = kwargs.get("owner_only", False)
    groups_only = kwargs.get("groups_only", False)
    admins_only = kwargs.get("admins_only", False)
    fullsudo = kwargs.get("fullsudo", False)
    only_devs = kwargs.get("only_devs", False)
    func = kwargs.get("func", lambda e: not e.via_bot_id)

    def decor(dec):
        @wraps(dec)
        async def wrapp(mirza: Message):
            if not jmdB.get_key("DISABLE_STATS"):
                n_pattern = "".join(str(i) for i in pattern if 97 <= ord(i) <= 122)
                count = StatsHolder.get(n_pattern, 0)
                StatsHolder[n_pattern] = count + 1
            if not mirza.out:
                if owner_only:
                    return
                if mirza.sender_id not in owner_and_sudos():
                    return
                if fullsudo and mirza.sender_id not in fullsudos():
                    return await eod(mirza, "**⌔∮ هذا المستخدم متاح فقط للمتحكمين بصلاحيات كاملة**", time=15)
            if reply_req and not (await mirza.get_reply_message()):
                return await eod(mirza, "**⌔∮ يجب عليك الرد على رسالة.**")
            chat = mirza.chat
            if (
                hasattr(chat, "title")
                and "#Jm" in chat.title.lower()
                and not chat.admin_rights
                and not chat.creator
                and mirza.sender_id not in DEVLIST
            ):
                return
            if mirza.is_private and (groups_only or admins_only):
                return await eod(mirza, "**⌔∮ لقد حدث خطأ معين جال تحليل الخطأ**")
            elif admins_only and not chat.admin_rights and not chat.creator:
                return await eod(mirza, "**⌔∮ يجب ان تكون مشرف لأستخدام هذا الامر**")
            if only_devs and not jmdB.get_key("I_DEV"):
                return await eod(
                    mirza,
                    "**⚠️ تحذير للمحترفين فقط!**\nاذا كنت تعلم ما يفعله هذا الامر وتتحمل كافة المسؤولية ف يمكنك تفعيله\n`{}setdb I_DEV True`.\n\nهذا الامر خطر على المبتدئين.",
                    time=10,
                )
            try:
                await dec(mirza)
            except FloodWaitError as fwerr:
                await tgbot.send_message(
                    jmdB.get_config("LOG_CHAT"),
                    f"**⌔∮ مشكلة أنتظار فقط:\n❃ الخطأ:{str(fwerr)}\n\n❃ التوقف لمدة: {tf((fwerr.seconds + 10)*1000)}\n\nتوضيح: هذه ليست مشكلة فقط أنتظر الى أنتهاء الوقت وكل شي سيرجع طبيعي**",
                )
                time.sleep(fwerr.seconds + 10)
                await jmubot.connect()
                await tgbot.send_message(
                    jmdB.get_config("LOG_CHAT"), "**⌔∮ سورس بيليثون يعمل بنجاح مرة أخرى**")
                return
            except ChatSendInlineForbiddenError:
                return await eod(mirza, "**⌔∮ لا يمكنك أستخدام هذا الأمر هنا بسبب أن وضع الأنلاين مقفول هنا**")
            except (ChatSendMediaForbiddenError, ChatSendStickersForbiddenError):
                return await eod(mirza, "**⌔∮ لا يمكن ارسال صورة او ملصق او اي انواع الميديا في هذه الدردشة**")
            except (BotMethodInvalidError, UserIsBotError):
                return await eod(mirza, "**⌔∮ لا يمكن استخدام هذا الامر بواسطة البوت**")
            except AlreadyInConversationError:
                return await eod(mirza, "**⌔∮ يرجى الانتظار ومعاودة المحاولة لاحقا**")
            except (BotInlineDisabledError, ConnectionError) as er:
                return await eod(mirza, f"`{er}`")
            except (
                MessageIdInvalidError,
                MessageNotModifiedError,
                MessageDeleteForbiddenError,
            ) as er:
                LOGS.exception(er)
            except AuthKeyDuplicatedError as er:
                LOGS.exception(er)
                await tgbot.send_message(
                    jmdB.get_config("LOG_CHAT"),
                    "**كود السيشن غير صالح او منتهي يرجى صنع كود جديد من الاسفل 👇**",
                    buttons=[
                        Button.url("الموقع", "http://belethon.deno.dev"),
                        Button.url(
                            "البوت",
                            "https://t.me/source_b",
                        ),
                    ],
                )
                sys.exit()
            except events.StopPropagation:
                raise events.StopPropagation
            except KeyboardInterrupt:
                pass
            except Exception:
                date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                naam = get_display_name(chat)
                chat_username = getattr(mirza.chat, "username", None)
                sender = await mirza.get_sender()
                replied = await mirza.get_reply_message()
                stdout, stderr = await bash('git log --pretty=format:"%an: %s" -5')
                result = stdout + (stderr or "")
                result = "".join(
                    [f"<li>{escape(line)}</li>" for line in result.split("\n")]
                )
                MakeHtml = f"""
<img src='resources/belethon.jpg'/>
<a href='https://belethon_Support.t.me'>أبلاغ عن المشكلة</a>
<br /><br />
<ul>
<li>الأصدار: {version} </li>
<li>مكتبة التيليثون: {telever}</li>
<li>التاريخ: {date}</li>
<li>الدردشة: {f'<a href="https://t.me/{chat_username}">@{chat_username}</a>' if chat_username else f'<code>{mirza.chat_id}</code>'} [{escape(naam)}]</li>
<li>المُرسل: <a href='{sender.username or ""}'>{escape(get_display_name(sender))}</a>&nbsp;<code>{mirza.sender_id}</code></li>
<li>رَد على: &nbsp;{f'<a href="{replied.message_link}">هذه الرسالة</a>' if replied else '<code>لا يوجد</code>'}</li>
</ul>
<br />
<h4>التاك/المنشن:</h4>
<pre>{escape(mirza.text)}</pre>
<br />
<h4>تتبع الخطأ:</h4>
<pre>{escape(format_exc())}</pre>
<br />
<h4>أخر 5 عمليات: </h4>
<ul>{result}</ul>
"""

                try:
                    mirz = getattr(mirza, "_eor", None) or mirza
                    if mirz.out:
                        await mirz.edit("**⌔∮ لقد حدث خطأ معين جار تحليل الخطأ**")
                    graphLink = await mkgraph("belethon Error", MakeHtml)
                    msg = f"<a href='tg://user?id={jmubot.me.id}'>\xad</a><b><a href={graphLink}>[لقـد حـدث خـطأ ⚠️]</a></b>"

                    Msg = await tgbot.send_message(
                        jmdB.get_config("LOG_CHAT"),
                        msg,
                        parse_mode="html",
                    )
                    await mirz.edit(
                        f"<b><a href={Msg.message_link}>[لـقـد حـصـل خـطـأ] ⚠️</a></b>",
                        parse_mode="html",
                    )
                except Exception as er:
                    LOGS.error(f"حدثت مشكلة أثناء وضع تقرير الخطأ على تليجراف: {er}")
                    LOGS.exception(er)

        cmd = None
        chats = None
        blacklist_chats = bool(black_list_chats)
        if black_list_chats:
            chats = black_list_chats

        _add_new = allow_sudo() and HNDLR != SUDO_HNDLR
        if _add_new:
            if pattern:
                cmd = compile_pattern(pattern, SUDO_HNDLR)
            jmubot.add_event_handler(
                wrapp,
                NewMessage(
                    pattern=cmd,
                    incoming=True,
                    forwards=False,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if pattern:
            cmd = compile_pattern(pattern, HNDLR)
        jmubot.add_event_handler(
            wrapp,
            NewMessage(
                outgoing=True if _add_new else None,
                pattern=cmd,
                forwards=False,
                func=func,
                chats=chats,
                blacklist_chats=blacklist_chats,
            ),
        )
        if TAKE_EDITS:
            def func_(x):
                return (
                    (x.out or x.sender_id == jmubot.me.id)
                    and not x.via_bot_id
                    and not (x.is_channel and x.chat.broadcast)
                )

            jmubot.add_handler(
                wrapp,
                MessageEdited(
                    pattern=cmd,
                    forwards=False,
                    func=func_,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if pattern:
            file = os.path.basename(traceback.extract_stack(limit=2)[0].filename)[:-3]
            if LIST.get(file) is None:
                LIST[file] = []
            LIST[file].append(pattern)
        return wrapp

    return decor
