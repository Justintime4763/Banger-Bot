import discord, youtube_dl, os, time, sys
from discord.ext import commands
from discord.utils import get

# INITIALIZATION, SETTING TOKENS, PREFIXES ETC.

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


def video_size(url):
    with youtube_dl.YoutubeDL() as ydl:
        dictMeta = ydl.extract_info(url, download=False)
        return dictMeta['duration']


src = os.path.abspath('../src/')
 
try:
    TOKEN = open('token.txt', 'r').read()
except:
    print("File does not exist; use your own token by deleting this try/except"
          +" statement and just making the TOKEN variable equal to your own token")
    time.sleep(5)
    sys.exit(1)
     
BOT_PREFIX = '>'
BOT_PLAYING = discord.Game("some banger music bro")

help_command = commands.DefaultHelpCommand(
    no_category='Commands'
) 
bot = commands.Bot(command_prefix=BOT_PREFIX, help_command=help_command)

# ON READY


@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + "\n")
    await bot.change_presence(status=discord.Status.online, activity=BOT_PLAYING)

# COMMANDS


@bot.command(brief="When the imposter is sus :joy:", description="Meme command for testing out embedding images")
async def mfw(ctx):
    with open(os.path.join(src, "sus.jpg"), 'rb') as f:
        await ctx.send("when the imposter is sus :joy:", file=discord.File(f))


# TODO// FINISH PLAY COMMAND AND ADD VOLUME FUNCTIONALITY, PAUSE, SKIP, QUEUE ETC.
@bot.command(brief="Joins user's voice channel", description="Makes the bot join the voice channel "
                    +"the user is in.", aliases=['j', 'J', 'Join'])
async def join(ctx):
    global voice
    
    try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
    except:
        await ctx.send("You are not connected to a voice channel.")
        print("User tried to request voice bot, but was not in a voice channel")
        return
    
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
             +"if it's in one", aliases=['Leave', 'disconnect', 'Disconnect'])
async def leave(ctx):
    try:
        channel = ctx.message.author.voice.channel
    except:
        channel = None
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    if voice and voice.is_connected():
        if channel is None:
            channel = voice.channel
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}.")
    else:
        print("Bot attempted to leave voice channel, was not in any to leave")
        await ctx.send("Bot not in any channel.")


@bot.command(brief="Play a youtube video", description="Makes the bot join the voice channel "
                    +"you're in and plays a youtube video.", aliases=['p', 'P', 'Play'], category="Music")
async def play(ctx, url: str):
    
    try:
        await join(ctx)
    except:
        pass
    
    try:
        if os.path.isfile(os.path.join(src, "song.mp3")):
            os.remove(os.path.join(src, "song.mp3"))
            print("Removed cached song\n")
    except:
        await ctx.send("ERROR; song currently playing; queueing is currently being developed")
        return
     
    # Checking if audio is longer than 6 minutes
    if video_size(url) > (6 * 60):
        await ctx.send("Error; video larger than 6 minutes. This cap is in place "
                +"because each video needs to downloaded to the computer, and large videos take up too much space.")
        return
     
    await ctx.send("Downloading neccesary files...")
     
    voice = get(bot.voice_clients, guild=ctx.guild)
     
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
         
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, os.path.join(src, "song.mp3"))
             
    voice.play(discord.FFmpegPCMAudio(os.path.join(src, "song.mp3")),
               after=lambda e: print(f"{name} has finished playing"))
     
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07
     
    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing `{url}` in {voice.channel}!")
    print(f"Playing `{url}` in {voice.channel}")

async def skip(ctx):
    pass

        
bot.run(TOKEN)
