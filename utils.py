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
import os
from config import Config
import ffmpeg
from pyrogram import emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pytgcalls import GroupCall
import signal
from pyrogram import Client
from youtube_dl import YoutubeDL
from os import path
from user import USER
import wget
STREAM_URL=Config.STREAM_URL
CHAT=Config.CHAT
GROUP_CALLS = {}
FFMPEG_PROCESSES = {}
RADIO={6}
LOG_GROUP=Config.LOG_GROUP
DURATION_LIMIT=Config.DURATION_LIMIT
playlist=Config.playlist
msg=Config.msg

bot = Client(
    "Musicplayervc",
    Config.API_ID,
    Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)
bot.start()

class DurationLimitError(Exception):
    pass

ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)
def youtube(url: str) -> str:
    info = ydl.extract_info(url, False)
    duration = round(info["duration"] / 60)

    if duration > DURATION_LIMIT:
        raise DurationLimitError(
            f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {duration} minute(s)"
        )
    try:
        ydl.download([url])
    except:
        raise DurationLimitError(
            f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {duration} minute(s)"
        )
    return path.join("downloads", f"{info['id']}.{info['ext']}")

class MusicPlayer(object):
    def __init__(self):
        self.group_call = GroupCall(USER, path_to_log_file='')
        self.chat_id = None

    async def send_playlist(self):
        if not playlist:
            pl = f"{emoji.NO_ENTRY} Empty playlist"
        else:       
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}\n"
                for i, x in enumerate(playlist)
            ])
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await self.send_text(pl)

    async def skip_current_playing(self):
        group_call = self.group_call
        if not playlist:
            return
        if len(playlist) == 1:
            await mp.start_radio()
            return
        client = group_call.client
        download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
        group_call.input_filename = os.path.join(
            download_dir,
            f"{playlist[1][1]}.raw"
        )
        # remove old track from playlist
        old_track = playlist.pop(0)
        print(f"- START PLAYING: {playlist[0][1]}")
        if LOG_GROUP:
            await self.send_playlist()
        os.remove(os.path.join(
            download_dir,
            f"{old_track[1]}.raw")
        )
        if len(playlist) == 1:
            return
        await self.download_audio(playlist[1])

    async def send_text(self, text):
        group_call = self.group_call
        client = group_call.client
        chat_id = LOG_GROUP
        message = await bot.send_message(
            chat_id,
            text,
            disable_web_page_preview=True,
            disable_notification=True
        )
        return message

    async def download_audio(self, song):
        group_call = self.group_call
        client = group_call.client
        raw_file = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                                f"{song[1]}.raw")
        if not os.path.isfile(raw_file):
            if song[3] == "telegram":
                original_file = await bot.download_media(f"{song[2]}")
                ffmpeg.input(original_file).output(
                    raw_file,
                    format='s16le',
                    acodec='pcm_s16le',
                    ac=2,
                    ar='48k',
                    loglevel='error'
                ).overwrite_output().run()
                os.remove(original_file)
            elif song[3] == "youtube":
                original_file = youtube(song[2])
                ffmpeg.input(original_file).output(
                    raw_file,
                    format='s16le',
                    acodec='pcm_s16le',
                    ac=2,
                    ar='48k',
                    loglevel='error'
                ).overwrite_output().run()
                os.remove(original_file)
            else:
                original_file=wget.download(song[2])
                ffmpeg.input(original_file).output(
                    raw_file,
                    format='s16le',
                    acodec='pcm_s16le',
                    ac=2,
                    ar='48k',
                    loglevel='error'
                ).overwrite_output().run()
                os.remove(original_file)


    async def start_radio(self):
        group_call = mp.group_call
        if group_call.is_connected:
            playlist.clear()   
            group_call.input_filename = ''
        process = FFMPEG_PROCESSES.get(CHAT)
        if process:
            process.send_signal(signal.SIGTERM)
        station_stream_url = STREAM_URL
        group_call.input_filename = f'radio-{CHAT}.raw'
        if not group_call.is_connected:
            await mp.start_call()
        try:
            RADIO.remove(0)
        except:
            pass
        try:
            RADIO.add(1)
        except:
            pass
        process = ffmpeg.input(station_stream_url).output(
            group_call.input_filename,
            format='s16le',
            acodec='pcm_s16le',
            ac=2,
            ar='48k'
        ).overwrite_output().run_async()
        FFMPEG_PROCESSES[CHAT] = process


    
    async def stop_radio(self):
        if 0 in RADIO:
            return
        group_call = mp.group_call
        if group_call:
            playlist.clear()   
            group_call.input_filename = ''
            try:
                RADIO.remove(1)
            except:
                pass
            try:
                RADIO.add(0)
            except:
                pass
        process = FFMPEG_PROCESSES.get(CHAT)
        if process:
            process.send_signal(signal.SIGTERM)

    async def start_call(self):
        group_call = mp.group_call
        await group_call.start(CHAT)
        
    async def startupradio(self):
        group_call = mp.group_call
        if group_call:
            group_call.stop_playout()
            playlist.clear()
        group_call.input_filename = f'radio-{CHAT}.raw'
        process = FFMPEG_PROCESSES.get(CHAT)
        if process:
            process.send_signal(signal.SIGTERM)
        station_stream_url = STREAM_URL
        await group_call.start(CHAT)
        try:
            RADIO.add(1)
        except:
            pass
        process = ffmpeg.input(station_stream_url).output(
            group_call.input_filename,
            format='s16le',
            acodec='pcm_s16le',
            ac=2,
            ar='48k'
        ).overwrite_output().run_async()
        FFMPEG_PROCESSES[CHAT] = process


mp = MusicPlayer()


# pytgcalls handlers

@mp.group_call.on_network_status_changed
async def network_status_changed_handler(gc: GroupCall, is_connected: bool):
    if is_connected:
        mp.chat_id = int("-100" + str(gc.full_chat.id))
    else:
        mp.chat_id = None


@mp.group_call.on_playout_ended
async def playout_ended_handler(_, __):
    if not playlist:
        await mp.start_radio()
    else:
        await mp.skip_current_playing()
