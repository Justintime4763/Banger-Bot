import discord, youtube_dl, os, time, sys
from discord.ext import commands
from discord.utils import get

#INITIALIZATION, SETTING TOKENS, PREFIXES ETC.

src = os.path.abspath('../src/')
 
try:
    TOKEN = open('token.txt', 'r').read()
except:
    print("File does not exist; use your own token by deleting this try/except"
          + " statement and just making the TOKEN variable equal to your own token")
    time.sleep(5)
    sys.exit(1)
     
BOT_PREFIX = '>'
BOT_PLAYING = ''

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
) 
bot = commands.Bot(command_prefix=BOT_PREFIX, help_command=help_command)

# ON READY

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + "\n")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("some banger music bro"))

# COMMANDS
@bot.command(brief = "When the imposter is sus :joy:", description = "Meme command for testing out embedding images")
async def mfw(ctx):
    with open(os.path.join(src, "sus.jpg"), 'rb') as f:
        image = discord.File(f)
        await ctx.send("when the imposter is sus :joy:", file=image)

#TODO// FINISH PLAY COMMAND AND ADD VOLUME FUNCTIONALITY, PAUSE, SKIP, QUEUE ETC.
@bot.command(brief = "Joins user's voice channel", description = "Makes the bot join the voice channel "
                    +  "the user is in.", aliases=['j', 'J', 'Join'])

async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    if voice and voice.isConnected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        
    await voice.disconnect()
    
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")
        
    await ctx.send(f"Joined {channel}.")

@bot.command(brief="Bot leaves active voice channel.", description="Makes bot leave the voice channel, "
             + "if it's in one", aliases=['Leave'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}.")
    else:
        print("Bot attempted to leave voice channel, was not in any to leave")
        await ctx.send("Bot not in any channel.")

@bot.command(brief = "Play a youtube video", description = "Makes the bot join the voice channel "
                    +  "you're in and plays a youtube video.", aliases=['p', 'P', 'Play'], category="Music")

async def play(ctx):
    pass

async def skip(ctx):
    pass
        
bot.run(TOKEN)
