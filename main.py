import asyncio
import random
import os
import time
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from googleapiclient.discovery import build
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO

# retrieves discord and youtube token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YT_TOKEN')

# allows all intents, makes bot command prefixes start with '!',sets up youtube api
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


@client.event
async def on_ready():
    """
    sends a message in console when discord bot is ready and sets the discord status to 'playing !help'
    """
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name='!help'))


@client.event
async def on_message(message):
    """
    checks if a message contains a specified string and sends a message when there is
    """
    if message.author == client.user:
        return
    # num_list is a list of strings because it was a simple fix to the bot saying 8283732 has the number 28
    num_list = [' 1 ', ' 2 ', ' 3 ', ' 4 ', ' 5 ']
    word_list = ['hi', 'howdy', 'hello', 'hey', 'wassup', 'yo']

    def check_word_in_list(word, content):
        """
        this makes it so that capitals won't be affected when looking for messages
        """
        return word.lower() in content.lower()

    for x in num_list:
        if check_word_in_list(x, message.content):
            await message.channel.send(f'the number{x}was mentioned! thats one of my favorite numbers!')
            break
    for x in word_list:
        if check_word_in_list(x, message.content):
            await message.channel.send(f'{message.content}, oh were you not talking to me?')
            break
    await client.process_commands(message)


# removes the default help command so custom one is able to be made
client.remove_command('help')


@client.command()
async def help(ctx):
    """
    a help command that displays information about the bot as well as current commands
    """
    embed = discord.Embed(title='Welcome to Vincent Bot!', description='', color=discord.Color.blue())
    embed.add_field(name='Current Commands:', value='!showinfo\n!favoritevideo\n!overlay @user'
                                                    '\n!boom\n!spam\n!stopspam\n!pickupme\n!pickup '
                                                    '@user\n!clearbot\n/announce "announcement"')
    file = discord.File('files/blue.jpg', filename='image.png')
    embed.set_image(url='attachment://image.png')
    embed.set_footer(text='blue is my favorite color!')
    await ctx.send(file=file, embed=embed)


@client.command()
async def showinfo(ctx):
    """
    short introduction to the bot, nothing too special
    """
    messages = ['Hello!', 'I am a bot created by Vincent Wang', 'I have many features that Vincent wanted to create',
                'I hope to be improved on in the future', 'There really isn\'t much use to me right now',
                'But I hope I get worked on more in the future!', 'Nice meeting you!']
    for x in messages:
        await ctx.send(x)
        await asyncio.sleep(1)
    file = discord.File('files/sunglasses.png')
    await ctx.send(file=file)


@client.command()
async def favoritevideo(ctx):
    """
    uses Google/YouTube api to display an embed of a YouTube video
    """
    video_id = 'y0sF5xhGreA'
    video_response = youtube.videos().list(part='snippet', id=video_id).execute()
    video_title = video_response['items'][0]['snippet']['title']
    video_description = video_response['items'][0]['snippet']['description']
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    # embed creation for discord message
    embed = discord.Embed(title=video_title, description=f'click to watch ^^^\n{video_description}', url=video_url,
                          color=discord.Color.red())
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    video_info = response['items'][0]['snippet']
    embed.set_image(url=video_info['thumbnails']['high']['url'])
    await ctx.send(embed=embed)


@client.command()
async def overlay(ctx, user: discord.User):
    """
    a simple(ish) image overlay command that overlays an image on the mentioned user
    """
    avatar_url = user.avatar_url_as(format='png') if hasattr(user, 'avatar_url_as') else user.avatar
    response = requests.get(str(avatar_url))
    avatar_image = Image.open(BytesIO(response.content)).convert('RGBA')
    overlay_image = Image.open('files/sparkles.png')
    overlay_image = overlay_image.resize(avatar_image.size)
    mask = Image.new('RGBA', avatar_image.size, (0, 0, 0, 0))
    mask.paste(overlay_image, (0, 0), overlay_image)
    result_image = Image.alpha_composite(avatar_image, mask)
    buffer = BytesIO()
    result_image.save(buffer, format='PNG')
    buffer.seek(0)
    await ctx.send(file=discord.File(buffer, filename='overlay.png'))


@client.command()
async def boom(ctx):
    """
    makes the bot join the users current discord voice channel and plays an .mp3 file
    you need ffmpeg.exe for this to work
    """
    if not ctx.author.voice:
        await ctx.send('You are not connected to a voice channel.')
        return
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.move_to(voice_channel)
    else:
        voice_client = await voice_channel.connect()
    await ctx.send('boom! :exploading_head:')
    mp3_path = os.path.join(os.getcwd(), 'files/boom.mp3')
    player = voice_client.play(discord.FFmpegPCMAudio(mp3_path))
    await player.wait()
    await voice_client.disconnect()


everyone_loop_running = False


@client.command()
async def spam(ctx):
    """
    message spam command, mentions that the author is making the bot spam a channel
    """
    global everyone_loop_running
    everyone_loop_running = True
    while everyone_loop_running:
        await ctx.send(f'{ctx.author.mention} is currently spamming this channel!')


@client.command()
async def stopspam(ctx):
    """
    stops the spam command
    """
    global everyone_loop_running
    if everyone_loop_running:
        everyone_loop_running = False
        await ctx.send('Stopped the spamming command')
    else:
        await ctx.send('The spam command is not currently running')


@client.command()
async def pickupme(ctx):
    """
    gets the discord bot to direct message you some messages alongside a pickupline from a text document
    """
    await ctx.author.send('hey~~')
    asyncio.sleep(7)
    await ctx.author.send('how are you doing...')
    asyncio.sleep(2)
    pickupline = open('files/pickuplines.txt', 'r')
    pickuplines = []
    temp = pickupline.read().splitlines()
    for x in temp:
        pickuplines.append(x)
    pickupline.close()
    await ctx.author.send(random.choice(pickuplines))
    asyncio.sleep(2)
    await ctx.author.send('hey did you like my pickup line?')
    asyncio.sleep(2)
    await ctx.author.send('if not, here is another :)')
    asyncio.sleep(2)
    await ctx.author.send(random.choice(pickuplines))


@client.command()
async def pickup(ctx):
    """
    gets the discord bot to direct message someone else in the server some messages
    alongside a pickupline from a text document
    """
    mentioned_user = ctx.message.mentions[0]
    await ctx.mentioned_user.send('hey~~')
    asyncio.sleep(7)
    await ctx.mentioned_user.send('how are you doing...')
    asyncio.sleep(2)
    pickupline = open('files/pickuplines.txt', 'r')
    pickuplines = []
    temp = pickupline.read().splitlines()
    for x in temp:
        pickuplines.append(x)
    pickupline.close()
    await ctx.mentioned_user.send(random.choice(pickuplines))
    asyncio.sleep(2)
    await ctx.mentioned_user.send('hey did you like my pickup line?')
    asyncio.sleep(2)
    await ctx.mentioned_user.send('if not, here is another :)')
    asyncio.sleep(2)
    await ctx.mentioned_user.send(random.choice(pickuplines))
    await mentioned_user.send(f'you just got hit on up by {ctx.author.mention}')


@client.command()
async def clearbot(ctx):
    """
    clear any messages that the bot previosuly had in that channel
    """
    channel = ctx.channel
    bot_messages = []
    async for message in channel.history():
        if message.author == client.user:
            bot_messages.append(message)
    for message in bot_messages:
        await message.delete()
    await ctx.send("Deleted all previous bot messages in this channel.")


@client.tree.command(name='announce', description='announce something !!')
@app_commands.describe(annoucement='what should i say?')
async def hey(interaction: discord.Interaction, annoucement: str):
    """
    simple slash command for discord developer profile badge
    """
    await interaction.response.send_message(f'{interaction.user.mention} said {annoucement}')


# runs the bot
client.run(TOKEN)
