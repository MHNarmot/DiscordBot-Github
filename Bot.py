import discord
import os
import asyncio
from pytube import YouTube
from discord.ext import commands
from discord import FFmpegPCMAudio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN = "OTAyMzIyMzE0NzQwNDAwMTI4.GtMZOC.IQS0bSbQ7reH5QPfSImQPuktvJ9QN54kBlEvWY"
YOUTUBE_API_KEY = "AIzaSyBfDTSv-bpA3TAguJ_QijPljuZPKOLruV4"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

def search_video(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    try:
        response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=1,
            type="video"
        ).execute()

        video_id = response["items"][0]["id"]["videoId"]
        return video_id

    except HttpError as e:
        print("An error occurred: {}".format(e))
        return None

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@client.command()
async def cal(ctx, *, query):
    if not query:
        await ctx.send("Lütfen çalmak istediğiniz şarkının adını girin.")
        return

    video_id = search_video(query)
    if not video_id:
        await ctx.send("Şarkı bulunamadı, lütfen başka bir şarkı adı girin.")
        return

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send("Bir ses kanalında olmanız gerekiyor.")
        return

    if not ctx.voice_client or (ctx.voice_client and not ctx.voice_client.is_connected()):
        await channel.connect()

    video = YouTube(video_url)
    stream = video.streams.get_audio_only()
    stream.download(filename="temp_audio")
    audio_source = FFmpegPCMAudio("temp_audio")

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ctx.voice_client.play(audio_source)

    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    os.remove("temp_audio")

client.run(TOKEN)
