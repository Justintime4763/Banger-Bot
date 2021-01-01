import discord, youtube_dl, os, time, sys, re, time, asyncio
from discord.ext import commands
from discord.utils import get
import urllib.request

# INITIALIZATION, SETTING TOKENS, PREFIXES ETC.

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

queue = {}


def check_queue_and_play(ctx):
    
    guild_id = ctx.guild.id
    
    if queue[guild_id] == [] or queue[guild_id] is None or queue is None or len(queue[guild_id]) == 1:
        return
    
    del queue[guild_id][0]
    
    coro = play(ctx, queue[guild_id][0])
    fut = asyncio.run_coroutine_threadsafe(coro)
    try:
        fut.result()
    except:
        print("coroutine error")


async def add_to_queue(ctx, url: str):
    global queue
    if not queue:
        queue = {}
    try:
        queue[ctx.guild.id].append(url)
    except:
        queue[ctx.guild.id] = [url]
    
    return


def video_size(url):
    with youtube_dl.YoutubeDL() as ydl:
        dictMeta = ydl.extract_info(url, download=False)
        return dictMeta['duration']


def video_name(url):
    with youtube_dl.YoutubeDL() as ydl:
        dictMeta = ydl.extract_info(url, download=False)
        return dictMeta['title']


def yt_firstresult(s):
    link = urllib.request.urlopen('https://www.youtube.com/results?search_query=' 
                                  +(s.replace(" ", "+")).replace("/", "\\"))
    video_ids = re.findall(r"watch\?v=(\S{11})", link.read().decode())
    return "https://www.youtube.com/watch?v=" + video_ids[0]


def is_url(s):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, s) is not None


src = os.path.abspath('../src/')
if not os.path.isdir(src):
    os.mkdir(src)
 
try:
    TOKEN = open('token.txt', 'r').read()
except:
    print("File does not exist; a token.txt file will be created; put in your token there")
    if not os.path.isfile(token.txt):
        token_file = open("token.txt", 'w+')
        token_file.close()
        del token_file
    time.sleep(5)
    sys.exit(1)
     
BOT_PREFIX = '>'
BOT_PLAYING = discord.Game("some bangers")

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


# TODO/ QUEUE
@bot.command(brief="Joins user's voice channel", description="Makes the bot join the voice channel "
                    +"the user is in.", aliases=['j', 'J', 'Join'])
async def join(ctx):
    global voice
    
    try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
    except:
        await ctx.send("**You're not in any voice channels** :man_facepalming:")
        print("User tried to request voice bot, but was not in a voice channel")
        return 0
    
    if voice and voice.is_connected() and not channel == voice.channel:
        await voice.move_to(channel)
    elif voice and voice.is_connected():
        await ctx.send("**Bot already in that channel** :shrug:")
        return
    else:
        voice = await channel.connect()
        print(f"[{ctx.guild}] Joined channel\n")
        
    voice.stop()
    await ctx.send(f"**Joined {channel}!** :wave: :speaking_head:")
    return 1


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
        print(f"[{ctx.guild}] Left channel\n")
        await ctx.send(f"**Left {channel}!** :wave:")
    else:
        print("Bot attempted to leave voice channel, was not in any to leave")
        await ctx.send("**Not in any voice channels** :shrug:")


@bot.command(brief="Play a youtube video", description="Makes the bot join the voice channel "
                    +"you're in and plays a youtube video.", aliases=['p', 'P', 'Play'], category="Music")
async def play(ctx, *args):
    
    url = args[0]
    
    if not (is_url(url)):
        await search(ctx, " ".join(args))
        return
    
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    # ## TODO ADD QUEUE HERE
    if not voice:
        try:
            if await join(ctx) == 0:
                return
        except:
            pass
    else:
        if voice.is_playing():
            # CALL Q FUNCTION HERE
            await add_to_queue(ctx, url)
            await ctx.send(f"**Added {video_name(url)} to queue!** :speaking_head:")
            return
        
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    try:
        if os.path.isfile(os.path.join(src, str(ctx.guild.id) + "/", "song.mp3")):
            os.remove(os.path.join(src, str(ctx.guild.id) + "/", "song.mp3"))
            print("Removed cached song\n")
    except:
        await ctx.send("ERROR; song currently playing; queueing is currently being developed")
        return
     
    # Checking if audio is longer than 6 minutes
    if video_size(url) > (6 * 60):
        await ctx.send("Error; video larger than 6 minutes. This cap is in place "
                +"because each video needs to downloaded to the computer, and large videos take up too much space.")
        return
    
    await add_to_queue(ctx, url)
    # TODO debug statement remove when finished with section 
    await ctx.send("**Downloading neccesary files...**")
     
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
         
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            if not os.path.isdir(os.path.join(src, str(ctx.guild.id) + "/")):
                os.mkdir(os.path.join(src, str(ctx.guild.id) + "/"))
            os.rename(file, os.path.join(src, str(ctx.guild.id) + "/", "song.mp3"))
         
    voice.play(discord.FFmpegPCMAudio(os.path.join(src, str(ctx.guild.id) + "/", "song.mp3")),
               after=check_queue_and_play(ctx))
     
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 1.0
     
    await ctx.send(f"**Playing** :notes: `{(video_name(url))}`** in {voice.channel}!**")
    print(f"[{ctx.guild}] Playing {video_name(url)} in {voice.channel}")

    
@bot.command(brief="Pauses music", description="Pauses currently playing video in channel.")
async def pause(ctx):
    
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print(f"[{ctx.guild}] Music paused")
        voice.pause()
        await ctx.send("**Music paused!** :pause_button:")
    else:
        await ctx.send("**Nothing playing!** :shrug:")


@bot.command(brief="Resumes music", description="Resumes previously paused video")
async def resume(ctx):
    
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused:
        print(f"[{ctx.guild}] Resumed music")
        await ctx.send("**Resuming music!** :notes:")
        voice.resume()
    else:
        await ctx.send("**Nothing playing!** :shrug:")

    
@bot.command(brief="Stops music", description="Stops currently playing video")
async def stop(ctx):
    
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print(f" [{ctx.guild}] Music stopped")
        voice.stop()
        await ctx.send("**Music stopped!** :mute:")
    else:
        await ctx.send("**Nothing playing!** :shrug:")


@bot.command(brief="Search for video to play", description="Searching for any youtube video to play")
async def search(ctx, *args):
    
    keywords = " ".join(args)
    
    link = yt_firstresult(keywords)
    
    await play(ctx, link)

        
@bot.command(brief="Set volume for bot", description="Updates bot volume.")
async def volume(ctx, vol: str):
    
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    if not voice:
        await ctx.send("**Bot not in any voice channels** :shrug:")
        return 

    try:
        if int(vol.strip("%")) / 100 < 2.01:
            voice.source.volume = int(vol.strip("%")) / 100
        else:
            await ctx.send("**Volume too high... listening above 200% may damage your hearing**")
    except:
        await ctx.send("**Volume invalid** :shrug:")


bot.run(TOKEN)
