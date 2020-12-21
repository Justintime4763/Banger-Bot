import discord, youtube_dl, os, time, sys
from discord.ext import commands
from discord.utils import get

#INITIALIZATION, SETTING TOKENS, PREFIXES ETC.
try:
    TOKEN = open("token.ini", "r").read()
except:
    print("File does not exist; use your own token by deleting this try/except statement and just setting token as"
          + " your own token")
    time.sleep(5)
    sys.exit(1)
    
BOT_PREFIX = '>'
BOT_PLAYING = ''

print(f"token is {TOKEN}") 

# bot = commands.bot(command_prefix=BOT_PREFIX)
#  
# @bot.event
# async def on_ready():
#     print("Logged in as " + bot.user.name + "\n")
#      
# bot.run(TOKEN)
