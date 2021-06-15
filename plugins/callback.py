#MIT License

#Copyright (c) 2021 SUBIN

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, emoji
from utils import mp
from config import Config
playlist=Config.playlist

HELP = """

<b> ربات و یوزر اکانت را به گروهتون اضافه کنید

ویس چت (vc) را آغاز کنید

با استفاده از `/play` <song name> یا با ریپلای کردن `/play` رو یک لینک یوتوب و یا فایل آن را پلی کنید.

همیچنین می توانید با `/dplay <song name>` از Deezer آهنگ خود را پخش کنید.</b>

**دستورات اولیه**:

`/play`  رو یک فایل صوتی ریلای کنید یا به صورت /play <song name> استفاده کنید.
`/dplay` رو یک لینک دیزر ریپلا کنید , همچنین می توانید /dplay <song name>
`/player`  موزیک در حال پخش را به شما نشان می دهد.
`/help` 
`/playlist` پلی لیست نشان داده می شود.

**دستورات ادمین**:
`/skip` [n] ...  رد کردن آهنگ فعلی یا n >= 2 تا آهنگ
`/join`  به VC جوین می شود.
`/leave`  از ویس چت فعلی خارج می شود
`/vc`  در کدام ویس چت است؟
`/stop`  توقف
`/radio` شروع کردن رادیو
`/stopradio` متوقف کردن استریم رادیو
`/replay` پخش کردن از اول
`/clean` پاک سازی
`/pause` مکث
`/resume` ادامه
`/mute`  سکوت در ویس چت
`/unmute`  با صدا
`/restart` ری استارت کردن ربات
"""


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.from_user.id not in Config.ADMINS and query.data != "help":
        await query.answer(
            "Who the hell you are",
            show_alert=True
            )
        return
    else:
        await query.answer()
    if query.data == "replay":
        group_call = mp.group_call
        if not playlist:
            return
        group_call.restart_playout()
        if not playlist:
            pl = f"{emoji.NO_ENTRY} Empty Playlist"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await query.edit_message_text(
                f"{pl}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🔄", callback_data="پخش مجدد"),
                            InlineKeyboardButton("⏯", callback_data="مکث"),
                            InlineKeyboardButton("⏩", callback_data="رد کردن")
                            
                        ],
                    ]
                )
            )

    elif query.data == "pause":
        if not playlist:
            return
        else:
            mp.group_call.pause_playout()
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await query.edit_message_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Paused\n\n{pl}",
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🔄", callback_data="پخش مجدد"),
                            InlineKeyboardButton("⏯", callback_data="ادامه"),
                            InlineKeyboardButton("⏩", callback_data="رد کردن")
                            
                        ],
                    ]
                )
            )

    
    elif query.data == "resume":   
        if not playlist:
            return
        else:
            mp.group_call.resume_playout()
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await query.edit_message_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Resumed\n\n{pl}",
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🔄", callback_data="پخش کردن"),
                            InlineKeyboardButton("⏯", callback_data="مکث"),
                            InlineKeyboardButton("⏩", callback_data="رد کردن")
                            
                        ],
                    ]
                )
            )

    elif query.data=="skip":   
        if not playlist:
            return
        else:
            await mp.skip_current_playing()
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        try:
            await query.edit_message_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Skipped\n\n{pl}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="پخش مجدد"),
                        InlineKeyboardButton("⏯", callback_data="مکث"),
                        InlineKeyboardButton("⏩", callback_data="رد کردن")
                            
                    ],
                ]
            )
        )
        except:
            pass
    elif query.data=="help":
        buttons = [
            [
                InlineKeyboardButton('Test', callback_data="1"),
                InlineKeyboardButton('Test', callback_data="2"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(
            HELP,
            reply_markup=reply_markup

        )
