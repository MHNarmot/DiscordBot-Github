import discord
import os
import asyncio
from pytube import YouTube
from discord.ext import commands
from discord import FFmpegPCMAudio

TOKEN = "OTAyMzIyMzE0NzQwNDAwMTI4.GtMZOC.IQS0bSbQ7reH5QPfSImQPuktvJ9QN54kBlEvWY"
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True


client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.guild:  # Eğer mesaj özel mesajda yazıldıysa
        await message.channel.send("Özel mesajlarda komut çalıştırmamaktayım, lütfen sunucudaki bir metin kanalında komut kullanın.")
        return

    await client.process_commands(message)


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@client.command()
async def cal(ctx, url):
    # Kullanıcının bir ses kanalında olup olmadığını kontrol et
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send("Bir ses kanalında olmanız gerekiyor.")
        return

    # Botun zaten bir ses kanalında olup olmadığını kontrol et
    if not ctx.voice_client or (ctx.voice_client and not ctx.voice_client.is_connected()):
        await channel.connect()

    # Pytube ve YouTube video indirme işlemi
    video = YouTube(url)
    stream = video.streams.get_audio_only()
    stream.download(filename="temp_audio")
    audio_source = FFmpegPCMAudio("temp_audio")

    # Oynatma işlemi
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ctx.voice_client.play(audio_source)

    # Ses dosyasını sildikten sonra komutun tamamlanmasını bekle
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    os.remove("temp_audio")


client.run(TOKEN)