import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os

TOKEN = ''
BOT_PREFIX = '>'
BOT_PLAYING = ''

bot = commands.bot(command_prefix=BOT_PREFIX)

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + "\n")
    
bot.run(TOKEN)
