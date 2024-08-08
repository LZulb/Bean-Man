import discord
from discord import Intents, app_commands
from discord.ext import commands
import os, time, random, sqlite3, asyncio, re
import utils
import datetime
from datetime import datetime
from datetime import timedelta

def random_color(amount, difficulty):
    if difficulty < 4:
        difficulty = 3
    if difficulty > 8:
        difficulty = 8
    colors = ["red_square", "green_square", "blue_square", "purple_square", "brown_square", "orange_square", "yellow_square", "white_large_square"][:difficulty]
    color_list = [random.choice(colors) for n in range(amount)]
    randColor = random.randint(0, len(color_list) - 1)
    return [color_list, randColor, color_list[randColor]]    

def format_colors(colors):
    loop = (len(colors) // 6) + 1
    msg = ""
    count = 0
    while count != loop:
        if len(colors) <= 6:
            for n in range(len(colors)):
                msg += f":{colors[0]}: "
                colors.pop(0)
        else:
            for n in range(6):
                msg += f":{colors[0]}: "
                colors.pop(0)
        msg += "\n"
        count += 1
    return msg

async def pre_game(ctx):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT game_playing FROM main WHERE id = {ctx.author.id}")
    is_playing = cursor.fetchone()
    if is_playing[0] == "playing":
        await ctx.reply("<:Error:957349442514718800>┃You are already playing a game!")
        return False
    utils.playing_set(ctx.author, "playing")
    return True
    
async def makeTurn(ctx, user, bot):
    count = 0
    while count < 2:
        try:
            start = await user.send("Pick **Rock**, **Paper**, or **Scissors**:")
        except discord.Forbidden:
            return "DM"
            
        msg = await utils.response(start.channel, user, bot, 15)
        if msg == "timeout":
            count += 1
            continue
        Newmsg = msg.content
        if Newmsg.lower() not in ["rock", "paper", 'scissors']:
            await msg.add_reaction("❌")
            await user.send("<:Error:957349442514718800>┃Enter a valid choice:")
            count += 1
            continue
        await msg.add_reaction("✅")
            
        return Newmsg.lower()
        
    return False

async def responses(location: discord.TextChannel, bot, timeout, team1, team2, team=True):
    """
    Returns the response of the user after the bot sends a message
    """
    if team:
        check = lambda m: m.channel == location and utils.get_user_team(m.author) in [team1, team2]
    else:
        check = lambda m: m.channel == location and (m.author in team1 or m.author in team2)
    try:
        option = await bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        return "timeout"
    return option

def mathQuestion(round:int) -> list:
    difficulty = round // 5
    if difficulty < 1:
        difficulty += 1
    min = 1 + difficulty
    max = 5 + difficulty
    answer = 0
    numbers = [random.randint(min, max) for n in range(2)]
    sign = random.choice(["+","-","*"])
    if sign == "+":
        answer += numbers[0] + numbers[1]
    if sign == "-":
        answer += numbers[0] - numbers[1]
    if sign == "*":
        answer += numbers[0] * numbers[1]
    return [f"{numbers[0]} {sign} {numbers[1]}", [str(answer)]]

def randomSend() -> list:
    items = ["CD", "ornament", "acorn", "apple", "bag", "cotton", "popcorn", "rubber", "yarn", "balloon", "banana", "bananas", "bandana", "bracelet", "soap", "baseball", "bat", "hat", "basketball", "bracelet", "necklace", "bed", "beef", "bell", "belt", "blouse", "blowdryer", "bonesaw", "book", "jokes", "matches", "bookmark", "boom", "bottle", "cap", "glue", "honey", "ink", "lotion", "polish", "oil", "paint", "perfume", "pills", "soda", "sunscreen", "syrup", "water", "flowers", "bow", "tie", "bowl", "box", "Q-tips", "baking", "chalk", "chocolates", "crayons", "markers", "tissues", "bracelet", "bread", "broccoli", "brush", "buckle", "knife", "button", "camera", "beans", "chili", "peas", "cream", "candle", "candlestick", "candy", "cane", "wrapper", "canteen", "canvas", "car", "card", "carrot", "carrots", "cars", "ice", "cat", "catalogue", "phone", "cellphone", "cement", "chain", "chair", "chalk", "book", "check", "chenille", "chicken", "book", "chocolate", "ring", "clay", "clock", "clothes", "pin", "mug", "pot", "comb", "comic", "computer", "conditioner", "pudding", "cookie", "tin", "cork", "couch", "cow", "hat", "craft", "card", "crow", "crowbar", "cucumber", "cup", "dagger", "deodorant", "desk", "dictionary", "dog", "dolphin", "domino", "door", "dove", "drawer", "drill", "egg", "beater", "timer", "empty", "jar", "tin", "eraser", "extension", "liner", "wash", "flowers", "feather", "duster", "batteries", "fish", "hook", "flag", "flashlight", "floor", "flowers", "flyswatter", "food", "football", "fork", "fridge", "pan", "game", "cartridge", "spade", "giraffe", "glass", "glasses", "glow", "paper", "grocery", "brush", "clip", "pin", "ribbon", "tie", "hammer", "hamster", "bag", "fan", "mirror", "handbasket"]
    randItem = random.choice(items)
    return [f'Send "**{randItem}**"', [randItem]]

def randomQuestions():
    questionSet = [
        ["How many colors are in a rainbow?", ["7"]],
        ["How many sides does a hexagon have?", ["6"]],
        ["What is the largest planet in our solar system?", ["jupiter"]],
        ["Who was the Greek god of thunder?", ["zeus"]],
        ["What is the largest organ in the human body?", ["skin"]],
        ["How many bones are usually in a human skeleton?", ["206"]],
        ["What year did Barry Bonds hit 73 Home Runs in a season?", ["2001"]],
        ["How many days are there in a leap year?", ["366"]],
        ['Which planet is known as the "Red Planet"?', ["mars"]],
        ["What is the largest country in the world by land area?", ["russia"]],
        ["What is the chemical symbol for the element oxygen?", ["o"]],
        ["What is the chemical symbol for the element hydrogen?", ["h"]],
        ['What is the chemical symbol for calcium?', "ca"],
        ['What is the chemical symbol for iron?', ["fe"]],
        ['What is the chemical symbol for the element copper?', "cu"],
        ['What is the chemical symbol for magnesium?', "mg"],
        ['Which animal is known as "man\'s best friend"?', ["dog", "dogs"]],
        ["How many legs does a spider have?", ["8"]],
        ['What is the national bird of the United States?', ["bald eagle", "eagle"]],
        ['What is the opposite of "day"?', ["night"]],
        ['What is the opposite of "up"?', ["down"]],
        ['What is the opposite of "hot"?', ["cold", "chilly", "mild"]],
        ['What is the opposite of "in"?', ["out"]],
        ['What is the opposite of "fast"?', ["slow", "loose"]],
        ['What is the opposite of "high"?', ['low', 'short', 'light']],
        ['What is the opposite of "empty"?', ["full"]],
        ['What is the opposite of "small"?', ["big", "large", "major", "ample", "generous", "substantial"]],
        ['What is the opposite of "happy"?', ["sad"]],
        ['What is the opposite of "start"?', ['end', 'finish']],
        ['What is the opposite of "light"?', ['dark', 'darkness', 'gloomy', 'heavy']],
        ['What is the opposite of "true"?', ['false']],
        ['What is the main language spoken in France?', "french"],
        ['What is the main language spoken in Spain?', ['spanish']],
        ['What is the largest star in our solar system?', ['the sun', 'sun']],
    ]
    randomQ = random.choice(questionSet)
    return [randomQ[0], randomQ[1]]