import discord
from discord import Intents, app_commands
from discord.ext import commands
import os, time, random, sqlite3, asyncio, re
import datetime
from datetime import datetime
from datetime import timedelta

locked = False

buy_list = ["nitro", "butter", "darkness", "random", "hunger", "imposter", "beans"]
sabotage_list = ["butter", "darkness", "hunger", "imposter", "random"]
butter_lines = ["Don't hold butter with your hands!", "Butter is slippery.", "Butter has wings.", "If you throw butter, it's a butterfly!"]
badges = ["points", "buy", "sab", "daily"]
battle_chats = [1116851801011007588, 1116851825631563916, 1116851857579581480, 1109617362191253554]

def db_make(member:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO main(id, team, points, coins, total_points, rps_status, game_playing, ban, butter, darkness, random, hunger, imposter, spam, daily_cooldown, memory_cooldown, total_daily, beans, secret_bean_crew, secret_gamer, secret_nerd, secret_beans, secret_santa, secret_nice_lad, secret_funny_lad, secret_rep, secret_rps, secret_hm, secret_cake, secret_profile, total_sab, total_buy, total_points_level, total_buy_level, total_sab_level, total_daily_level, daily_streak, rps_wins, hm_wins, cake, cake_cooldown, rep, rep_cooldown, crate, diamond_crate, tickets, rod) VALUES({member.id}, 0, 250, 250, 0, 'able', 'not playing', 'False', 0, 0, 0, 0, 0, 0, 'None', 'None', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'None', 0, 'None', 0, 0, 0, 0)")
    cursor.execute(f"INSERT INTO profiles(id, background, aboutme, border_color, aboutme_color, aboutme_background_color, name_color, font, badge_1, badge_2, pfp_gear, background_have, gear_have, color_have, font_have) VALUES({member.id}, '21', 'I like beans!', '21', '21', '20', '20', '1', 0, 0, '0', '21', '0', '21', '1')")
    db.commit()
    cursor.close(); db.close()

def sab_time_check(user:discord.Member, team, name):
    sab_time = time_check(user, f"team{team}{name}", "teams")
    if sab_time < 1:
        with sqlite3.connect('main.sqlite') as cursor:
            cursor.execute(f"UPDATE teams SET team{team}{name} = 'Nothing'")
        cursor.close()
        return True
    else:
        return False

def butter_check(ctx):
    team = get_user_team(ctx.author)
    sabTime = sab_time_check(ctx.author, team, "butter")
    if sabTime is True:
        return True
    else:
        if random.randint(0, 4) == 1:
            return False
        else:
            return True

def bean_check(ctx):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    team = get_user_team(ctx.author)
    check = sab_time_check(ctx.author, team, "hunger")
    if check is True:
        return True
    else:
        try:
            cursor.execute(f"SELECT beans FROM main WHERE id = {ctx.author.id}")
            beans = cursor.fetchone()[0]
            if beans < 1:
                return False
            else:
                cursor.execute(f"UPDATE main SET beans = {beans - 1} WHERE id = {ctx.author.id}")
                db.commit()
                return True
        finally:
            cursor.close(); db.close()

async def verification(bot, ctx):
    team = get_user_team(ctx.author)
    check = sab_time_check(ctx.author, team, "imposter")
    if check is True or random.randint(1,2) != 1:
        return True 
    msg = await ctx.reply(":question:┃Are you a human?")
    buttons = ["✅", "❌"]
    for emoji in buttons:
        await msg.add_reaction(emoji)
    try:
        reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message.id == msg.id and reaction.emoji in buttons, timeout=10)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
        await msg.edit(content="❌┃You are not a human!")
        return False
    else:
        if reaction.emoji == "✅":
            await msg.clear_reactions()
            await msg.edit(content="✅┃You are a human!")
            return True
        if reaction.emoji == "❌":
            await msg.clear_reactions()
            await msg.edit(content="❌┃You are not a human!")
            return False

def banCheck(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT ban FROM main WHERE id = {user.id}")
    ban = cursor.fetchone()[0]
    try:
        if ban == "True":
            return False
        else:
            return True
    finally:
        cursor.close(); db.close()

async def generalCheck(bot, ctx, bypass=False):
    """
    Checks to see if the user is inside the server or not
    """
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    if ctx.author.id in [683886490211713176, 502183735484088340]:
        return True
    if not banCheck(ctx.author):
        await ctx.reply("<:BanHammer_:957349442573467708>┃You're banned from using Bean Man. If you wish to dispute this, refer to <#1109608389216043019>.")
        return False
    if locked:
        await ctx.reply("This command is currently locked!")
        return False
    if ctx.message.guild or await generalCheck(ctx) is True:
        if ctx.message.guild.id == 1109586411058901152:
            if bypass is True:
                return True
            if get_user_team(ctx.author) != 0:
                if bean_check(ctx) is True:
                    if butter_check(ctx) is True:
                        if await verification(bot, ctx) is True:
                            cursor.execute(f"UPDATE main SET spam = 0 WHERE id = {ctx.author.id}")
                            db.commit()
                            cursor.close(); db.close()
                            return True
                        else:
                            return False
                    else:
                        await ctx.reply(f":butter:┃{random.choice(butter_lines)}")
                        return False
                else:
                    await ctx.reply("<:Error:957349442514718800>┃I'm hungry! I won't let you use this command until you feed me beans!")
                    return False
            else:
                await ctx.reply("<:Error:957349442514718800>┃Sorry, you must be on a team to use certain commands!")
                return False
        else:
            await ctx.reply("<:Error:957349442514718800>┃Sorry, you can only use **Bean Man** inside the *Bean Man's Hub* server!")
            return False
    else:
        await ctx.reply("<:Error:957349442514718800>┃Sorry, you can only use **Bean Man** inside the *Bean Man's Hub* server!")
        return False

def codeCheck(team, bot):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT team{team}code FROM teams")
    codeAmt = cursor.fetchone()[0]
    if codeAmt >= 3:
        alert = bot.get_channel(1109613004091310120)
        alert.send(f"**Team {team}** has the full code. They may start Rock, Paper, Scissors!")
        cursor.execute(f"UPDATE teams SET winner = {team}")
        db.commit()
        cursor.close(); db.close()

def get_playing(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT game_playing FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_winner():
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT winner FROM teams")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_final_team(bot, top:int):
    winner = get_winner()
    if winner == 0:
        return "No data currently!"
    else:
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        msg = f"Top {top} Users RPS Available\n"
        cursor.execute(f"SELECT rps_status FROM main WHERE team = {winner}")
        stats = cursor.fetchmany(top)
        cursor.execute(f"SELECT id FROM main WHERE team = {winner}")
        members = cursor.fetchmany(top)
        cursor.close(); db.close()
        count = 1
        for member, stat in zip(members, stats):
            if stat[0] != "able":
                continue
            user = bot.get_user(member[0])
            msg += f"{count}. {user.display_name}\n"
            count += 1
        return msg

def get_rps_able(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT rps_status FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_background_have(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT background_have FROM profiles WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_gear_have(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT gear_have FROM profiles WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_color_have(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT color_have FROM profiles WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_font_have(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT font_have FROM profiles WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_team(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT team FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_points(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT points FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_coins(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT coins FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_streak(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT daily_streak FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_rps_wins(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT rps_wins FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_hm_wins(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT hm_wins FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_rep(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT rep FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_cake(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT cake FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_butter(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT butter FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_darkness(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT darkness FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_random(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT random FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_hunger(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT hunger FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_imposter(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT imposter FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_beans(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT beans FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_crate(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT crate FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_diamond_crate(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT diamond_crate FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_rod(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT rod FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_user_tickets(user:discord.Member):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT tickets FROM main WHERE id = {user.id}")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def get_lottery_pot():
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT lottery FROM global")
    fetch = cursor.fetchone()[0]
    cursor.close(); db.close()
    return fetch

def select_list(user:discord.Member, value:list, table:str):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    outputs = []
    for val in value:
        cursor.execute(f"SELECT {val} FROM {table} WHERE id = {user.id}")
        outputs.append(cursor.fetchone()[0])
    cursor.close(); db.close()
    return outputs

def channel_check(ctx):
    """
    Checks what channel the user is in
    """
    if ctx.message.channel.id == 1109591422631415948:
        return "global"
    elif ctx.message.channel.id == 1109591517166829658:
        return 1
    elif ctx.message.channel.id == 1109591557226635387:
        return 2
    elif ctx.message.channel.id == 1109591592756596746:
        return 3
    elif ctx.message.channel.id == 1109591625061113936:
        return 4
    elif ctx.message.channel.id == 1109591646041030799:
        return 5
    else:
        return "unknown"

def cooldown_help(ctx, full_time, just_number=False):
    """
    Helps display the time left of anything given seconds
    """
    days = 0
    hours = 0
    minutes = 0
    cycles = 0
    if just_number is False:
        msg = "<:TimeoutError:957349442598633552>┃You have "
    else:
        msg = ""
    try:
        if full_time >= 86400:
            days += full_time // 86400
            full_time -= (86400 * days)
            msg += f"{days}D "
            cycles += 1
        if full_time >= 3600:
            hours += full_time // 3600
            full_time -= (3600 * hours)
            msg += f"{hours}H "
            cycles += 1
        if full_time >= 60:
            minutes += full_time // 60
            full_time -= (60 * minutes)
            msg += f"{minutes}M "
            cycles += 1
        if full_time > 0 and full_time < 60:
            msg += f"{full_time}S " + "left!"
        else:
            msg += "None!"
        return str(msg)
    except:
        print("Error with cooldown command.")

def embed_help(user:discord.Member, title:str, description:str="", color:discord.Colour=discord.Colour.red(), author:bool=False, timestamp:bool=False, footer:str=None, thumbnail:str=None, image:str=None):
    """
    Makes embeds a lot easier
    """
    embed = discord.Embed(title = f'{title}', description = description, color = color)
    if timestamp is True:
        embed.timestamp = datetime.now()
    if author is True:
        embed.set_author(name=f"{user.display_name}", icon_url=f"{user.avatar}")
    if footer != None:
        embed.set_footer(text=footer)
    if thumbnail != None:
        embed.set_thumbnail(url=thumbnail)
    if image != None:
        embed.set_image(url=image)
    return embed

def spam_check(ctx):
    """
    Returns spam count of the user
    """
    if ctx.author.id == 683886490211713176:
        return 0
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT spam FROM main WHERE id = {ctx.author.id}")
    spam = cursor.fetchone()
    cursor.execute(f"UPDATE main SET spam = {spam[0] + 1} WHERE id = {ctx.author.id}")
    db.commit()
    cursor.close(); db.close()
    return spam[0]

def item_price(item, amount=1, user:discord.Member=None):
    """
    Returns the price of any item
    """
    if item == "butter":
        return 30 * amount
    elif item == "darkness":
        return 15 * amount
    elif item == "random":
        return 30 * amount
    elif item == "hunger":
        return 15 * amount
    elif item == "imposter":
        return 15 * amount
    elif item == "beans":
        return 5 * amount
    elif item == "nitro":
        return 20_000 * amount
    elif item == "solid":
        return 5_000
    elif item == "picture":
        return 10_000
    elif item == "gear":
        return 3_000
    elif item == "color":
        return 6_500
    elif item == "font":
        return 5_000
    elif item == "crate":
        return 8_000 * amount
    elif item == "diamond_crate":
        return 35_000 * amount
    elif item == "ticket":
        return 150 * amount
    elif item == "N/A" or item == None:
        return False
    elif item == "rod":
        rod = get_user_rod(user)
        if rod == 0:
            return 5_000
        elif rod == 1:
            return 25_000
        elif rod == 2:
            return 50_000
        elif rod == 3:
            return 100_000
        else:
            return False

rodEmoji = {
    0: "",
    1: "<:WoodRod:1130998787175895120>",
    2: "<:SilverRod:1130998788849414245>",
    3: "<:GoldRod:1130998789902176256>",
    4: "<:DiamondRod:1130998790917193739>"
}

def makeID():
    """
    Generates a random ID
    """
    characters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z", "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z", "0","1","2","3","4","5","6","7","8","9"]
    ID = "".join([random.choice(characters) for _ in range(16)])
    return ID

async def makeTurn(ctx, user):
    count = 0
    while count < 2:
        try:
            await user.send("Pick **Rock**, **Paper**, or **Scissors**: ")
        except discord.Forbidden:
            return "DM"
        
        def check(msg):
            return msg.author == ctx.author and msg.content.lower() in ["rock", "paper", "scissors"]

        try:
            msg = await ctx.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            count += 1
            continue

        return msg.content.lower()

    return False

async def response(location: discord.TextChannel, user: discord.Member, bot, timeout):
    """
    Returns the response of the user after the bot sends a message
    """
    check = lambda m: m.author == user and m.channel == location
    try:
        option = await bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        return "timeout"
    return option

def playing_set(user:discord.Member, state:str):
    """
    Changes the playing state of rps or games.
    """
    if state not in ["playing", 'not playing']:
        print("Not 'playing' or 'not playing'.")
        return
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"UPDATE main SET game_playing = '{state}' WHERE id = {user.id}")
    db.commit()

def main_database_update(id:list, value:list, amount:list, option:list):
    """
    Alters data inside the main table in the database
    """
    try:
        if len(value) != len(amount) or len(value) != len(option):
            print("All lists MUST be be the same length.")
            return
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        for id, val, amt, opt in zip(id, value, amount, option):
            cursor.execute(f"SELECT {val} FROM main WHERE id = {id}")
            result = cursor.fetchone()[0]
            if opt == "add":
                amt = int(result + amt)
            if opt == "sub":
                amt = int(result - amt)
            if opt == "set":
                cursor.execute(f"UPDATE main SET {val} = '{amt}' WHERE id = {id}")
                continue
            if opt not in ["add", "sub", "set"]:
                print('Option must be "add", "sub", or "set"')
                return
            cursor.execute(f"UPDATE main SET {val} = {amt} WHERE id = {id}")
        db.commit()
        cursor.close(); db.close()
    except Exception as e:
        cursor.close(); db.close()
        raise(f"Something went wrong inside the database update command!\n{e}")

def time_check(user:discord.Member, value, table):
    """
    Returns the time left in any value given the table
    """
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    if table in ["teams", "global"]:
        cursor.execute(f"SELECT {value} FROM {table}")
        time = cursor.fetchone()[0]
    else:
        cursor.execute(f"SELECT {value} FROM main WHERE id = {user.id}")
        time = cursor.fetchone()[0]
    if time in ["None", "Nothing"]:
        return 0
    now = datetime.now().replace(microsecond=0)
    then = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - now
    cursor.close(); db.close()
    return int(then.total_seconds())

def add_time(user:discord.Member, value:int, amount:int, type:str, db, cursor):
    if type == "days":
        until = timedelta(days=amount)
    elif type == "hours":
        until = timedelta(minutes=amount)
    elif type == "minutes":
        until = timedelta(minutes=amount)
    elif type == "seconds":
        until = timedelta(seconds=amount)
    else:
        print("Not a valid type of time!")
        return
    cursor.execute(f"SELECT {value} FROM main WHERE id = {user.id}")
    timer = cursor.fetchone()[0]
    if time_check(user, value, "main") < 1:
        now = datetime.now().replace(microsecond=0)
    else:
        now = datetime.strptime(timer, '%Y-%m-%d %H:%M:%S')
    then = now + until
    cursor.execute(f"UPDATE main SET {value} = '{then}' WHERE id = {user.id}")
    db.commit()

def darkness_text(user:discord.Member, msg):
    if not sab_time_check(user, get_user_team(user), "darkness"):
        return "||???||"
    else:
        return msg

async def secret_add(role_id, role_name, author, message, value):
    roleList = [r.id for r in author.roles if r != message.guild.default_role]
    with sqlite3.connect('main.sqlite') as cursor:
        if role_id not in roleList:
            role_add = discord.utils.get(author.guild.roles, name=role_name)
            await author.add_roles(role_add)
            cursor.execute(f"UPDATE main SET secret_{value} = 1 WHERE id = {author.id}")
            await author.send(f"<:V_PinkVerify:868218741882765412>┃Secret Found:\nYou earned the **{role_name}** badge!")
    cursor.close()

# "total_points", "total_buy", "total_sab", "total_daily"

def badgeUpdate(user:discord.Member, badgeType:str, amount:int):
    if badgeType not in badges:
        print(f"{badgeType} isn't valid!")
        return
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT total_{badgeType} FROM main WHERE id = {user.id}")
    badge = cursor.fetchone()[0]
    cursor.execute(f"UPDATE main SET total_{badgeType} = {badge + amount} WHERE id = {user.id}")
    db.commit()
    cursor.execute(f"SELECT total_{badgeType} FROM main WHERE id = {user.id}")
    badge = cursor.fetchone()[0]
    try:
        if badgeType == "points":
            for val, amt in zip(list(point_badges.values()), range(len(point_badges))):
                cursor.execute(f"SELECT total_{badgeType}_level FROM main WHERE id = {user.id}")
                badgeLevel = cursor.fetchone()[0]
                if badge >= val and badgeLevel < amt:
                    cursor.execute(f"UPDATE main SET total_{badgeType}_level = {badgeLevel + 1} WHERE id = {user.id}")
                    db.commit()
        elif badgeType == "buy":
            for val, amt in zip(list(buy_badges.values()), range(len(buy_badges))):
                cursor.execute(f"SELECT total_{badgeType}_level FROM main WHERE id = {user.id}")
                badgeLevel = cursor.fetchone()[0]
                if badge >= val and badgeLevel < amt:
                    cursor.execute(f"UPDATE main SET total_{badgeType}_level = {badgeLevel + 1} WHERE id = {user.id}")
                    db.commit()
        elif badgeType == "sab":
            for val, amt in zip(list(sab_badges.values()), range(len(sab_badges))):
                cursor.execute(f"SELECT total_{badgeType}_level FROM main WHERE id = {user.id}")
                badgeLevel = cursor.fetchone()[0]
                if badge >= val and badgeLevel < amt:
                    cursor.execute(f"UPDATE main SET total_{badgeType}_level = {badgeLevel + 1} WHERE id = {user.id}")
                    db.commit()
        elif badgeType == "daily":
            for val, amt in zip(list(daily_badges.values()), range(len(daily_badges))):
                cursor.execute(f"SELECT total_{badgeType}_level FROM main WHERE id = {user.id}")
                badgeLevel = cursor.fetchone()[0]
                if badge >= val and badgeLevel < amt:
                    cursor.execute(f"UPDATE main SET total_{badgeType}_level = {badgeLevel + 1} WHERE id = {user.id}")
                    db.commit()
        else:
            print("Something went wrong!")
            return
    finally:
        cursor.close(); db.close()

point_badges = {
    "Brokie": 0,
    "Rookie Numbers": 100,
    "Getting Started": 250,
    "Half Way": 500,
    "We Made It": 1_000,
    "Climbing Up": 5_000,
    "So Rich": 10_000,
    "Big Bucks": 15_000,
    "Too Rich": 30_000,
    "Mr. Money Bags": 50_000,
    "The Peak": 100_000,
    "MR. SQUIDWARD": 250_000
}

buy_badges = {
    "Homemade": 0,
    "I'll Take Those": 5,
    "I Need More": 25,
    "Can't Stop": 50,
    "Won't Stop": 100,
    "Must Have It All": 250,
    "Shiny": 500,
    "Collector": 1_1000,
    "They're Mine": 2_500,
    "Sold Out": 5_000,
    "All Gone": 15_000,
    "All Mine": 30_000,
    "Need A Hand?": 100_100,
    "Oh These?": 250_000,
    "My Honkers?": 500_000,
    "Fin.": 1_000_000
}

sab_badges = {
    "Angel": 0,
    "Naughty": 3,
    "Naughty Dog": 6,
    "Fear Me": 25,
    "The Devil": 50,
    "Bad Boy": 100
}

daily_badges = {
    "There's A Daily?": 0,
    "They Will Cower!": 1,
    "14.3 Billion Years": 2,
    "UwU": 3,
    "What's a Pokeman?👴🏻": 4,
    "Put It In Reverse Terry!": 5,
    "Everybody Thank Wingman!": 6,
    "Come On, Let's Hear It!": 7,
    "Open Up The Sky!": 8,
    "Here Comes The Party!": 9,
    "You Thought You Were Safe!": 10,
    "You Want To Play? Let's Play.": 11,
    "They Are So Dead!": 12,
    "You will not kill my allies!": 13,
    "It's All You, lil' homie!": 14,
    "Face Your Fear!": 15,
    "Oye! Monster On The Loose!": 16,
    "They Shot Thrash.😭": 17,
    "Blow 'Em Up, Mosh!": 18,
    "I've got your trail!": 19,
    "Joke's Over, You're Dead!": 20,
    "Scatter!": 21,
    "Resuming your termination.": 22,
    "Fire In The Hole!": 23,
    "Where Is Everyone Hiding?": 24,
    "You. Are. Powerless": 25,
    "I’ll Handle This": 26,
    "Welcome To My World!": 27,
    "Your Duty Is Not Over!": 28,
    "You Want More? Here’s More!": 29,
    "The Hunt Begins!": 30,
    "I Am The Hunter!": 31,
}

def badgeCreation(ctx):
    msg = ""
    for n in badges:
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT total_{n}_level FROM main WHERE id = {ctx.author.id}")
        badgeLevel = cursor.fetchone()[0]
        cursor.close(); db.close()
        if n == "points":
            for key, amt in zip(point_badges.keys(), range(len(point_badges))):
                if amt == badgeLevel:
                    msg += f"- **Point**: __{key}__ ({badgeLevel}x)\n"
        elif n == "buy":
            for key, amt in zip(buy_badges.keys(), range(len(buy_badges))):
                if amt == badgeLevel:
                    msg += f"- **Buy**: __{key}__ ({badgeLevel}x)\n"
        elif n == "sab":
            for key, amt in zip(sab_badges.keys(), range(len(sab_badges))):
                if amt == badgeLevel:
                    msg += f"- **Sabotage**: __{key}__ ({badgeLevel}x)\n"
        elif n == "daily":
            for key, amt in zip(daily_badges.keys(), range(len(daily_badges))):
                if amt == badgeLevel:
                    msg += f"- **Daily**: __{key}__ ({badgeLevel}x)"
        else:
            print("Something went wrong!")
    return msg

pokemon_list = ['Bulbasaur', 'Ivysaur', 'Venusaur', 'Charmander', 'Charmeleon', 'Charizard', 'Squirtle', 'Wartortle', 'Blastoise', 'Caterpie', 'Metapod', 'Butterfree', 'Weedle', 'Kakuna', 'Beedrill', 'Pidgey', 'Pidgeotto', 'Pidgeot', 'Rattata', 'Raticate', 'Spearow', 'Fearow', 'Ekans', 'Arbok', 'Pikachu', 'Raichu', 'Sandshrew', 'Sandslash', 'Nidoran♀', 'Nidorina', 'Nidoqueen', 'Nidoran♂', 'Nidorino', 'Nidoking', 'Clefairy', 'Clefable', 'Vulpix', 'Ninetales', 'Jigglypuff', 'Wigglytuff', 'Zubat', 'Golbat', 'Oddish', 'Gloom', 'Vileplume', 'Paras', 'Parasect', 'Venonat', 'Venomoth', 'Diglett', 'Dugtrio', 'Meowth', 'Persian', 'Psyduck', 'Golduck', 'Mankey', 'Primeape', 'Growlithe', 'Arcanine', 'Poliwag', 'Poliwhirl', 'Poliwrath', 'Abra', 'Kadabra', 'Alakazam', 'Machop', 'Machoke', 'Machamp', 'Bellsprout', 'Weepinbell', 'Victreebel', 'Tentacool', 'Tentacruel', 'Geodude', 'Graveler', 'Golem', 'Ponyta', 'Rapidash', 'Slowpoke', 'Slowbro', 'Magnemite', 'Magneton', 'Farfetch’d', 'Doduo', 'Dodrio', 'Seel', 'Dewgong', 'Grimer', 'Muk', 'Shellder', 'Cloyster', 'Gastly', 'Haunter', 'Gengar', 'Onix', 'Drowzee', 'Hypno', 'Krabby', 'Kingler', 'Voltorb', 'Electrode', 'Exeggcute', 'Exeggutor', 'Cubone', 'Marowak', 'Hitmonlee', 'Hitmonchan', 'Lickitung', 'Koffing', 'Weezing', 'Rhyhorn', 'Rhydon', 'Chansey', 'Tangela', 'Kangaskhan', 'Horsea', 'Seadra', 'Goldeen', 'Seaking', 'Staryu', 'Starmie', 'Mr. Mime', 'Scyther', 'Jynx', 'Electabuzz', 'Magmar', 'Pinsir', 'Tauros', 'Magikarp', 'Gyarados', 'Lapras', 'Ditto', 'Eevee', 'Vaporeon', 'Jolteon', 'Flareon', 'Porygon', 'Omanyte', 'Omastar', 'Kabuto', 'Kabutops', 'Aerodactyl', 'Snorlax', 'Articuno', 'Zapdos', 'Moltres', 'Dratini', 'Dragonair', 'Dragonite', 'Mewtwo', 'Mew', 'Chikorita', 'Bayleef', 'Meganium', 'Cyndaquil', 'Quilava', 'Typhlosion', 'Totodile', 'Croconaw', 'Feraligatr', 'Sentret', 'Furret', 'Hoothoot', 'Noctowl', 'Ledyba', 'Ledian', 'Spinarak', 'Ariados', 'Crobat', 'Chinchou', 'Lanturn', 'Pichu', 'Cleffa', 'Igglybuff', 'Togepi', 'Togetic', 'Natu', 'Xatu', 'Mareep', 'Flaaffy', 'Ampharos', 'Bellossom', 'Marill', 'Azumarill', 'Sudowoodo', 'Politoed', 'Hoppip', 'Skiploom', 'Jumpluff', 'Aipom', 'Sunkern', 'Sunflora', 'Yanma', 'Wooper', 'Quagsire', 'Espeon', 'Umbreon', 'Murkrow', 'Slowking', 'Misdreavous', 'Unown', 'Wobbuffet', 'Girafarig', 'Pineco', 'Forretress', 'Dunsparce', 'Gligar', 'Steelix', 'Snubbull', 'Granbull', 'Qwilfish', 'Scizor', 'Shuckle', 'Heracross', 'Sneasel', 'Teddiursa', 'Ursaring', 'Slugma', 'Magcargo', 'Swinub', 'Piloswine', 'Corsola', 'Remoraid', 'Octillery', 'Delibird', 'Mantine', 'Skarmory', 'Houndour', 'Houndoom', 'Kingdra', 'Phanpy', 'Donphan', 'Porygon2', 'Stantler', 'Smeargle', 'Tyrogue', 'Hitmontop', 'Smoochum', 'Elekid', 'Magby', 'Miltank', 'Blissey', 'Raikou', 'Entei', 'Suicune', 'Larvitar', 'Pupitar', 'Tyranitar', 'Lugia', 'Ho-Oh', 'Celebi', 'Treecko', 'Grovyle', 'Sceptile', 'Torchic', 'Combusken', 'Blaziken', 'Mudkip', 'Marshtomp', 'Swampert', 'Poochyena', 'Mightyena', 'Zigzagoon', 'Linoone', 'Wurmple', 'Silcoon', 'Beautifly', 'Cascoon', 'Dustox', 'Lotad', 'Lombre', 'Ludicolo', 'Seedot', 'Nuzleaf', 'Shiftry', 'Taillow', 'Swellow', 'Wingull', 'Pelipper', 'Ralts', 'Kirlia', 'Gardevoir', 'Surskit', 'Masquerain', 'Shroomish', 'Breloom', 'Slakoth', 'Vigoroth', 'Slaking', 'Nincada', 'Ninjask', 'Shedinja', 'Whismur', 'Loudred', 'Exploud', 'Makuhita', 'Hariyama', 'Azurill', 'Nosepass', 'Skitty', 'Delcatty', 'Sableye', 'Mawile', 'Aron', 'Lairon', 'Aggron', 'Meditite', 'Medicham', 'Electrike', 'Manectric', 'Plusle', 'Minun', 'Volbeat', 'Illumise', 'Roselia', 'Gulpin', 'Swalot', 'Carvanha', 'Sharpedo', 'Wailmer', 'Wailord', 'Numel', 'Camerupt', 'Torkoal', 'Spoink', 'Grumpig', 'Spinda', 'Trapinch', 'Vibrava', 'Flygon', 'Cacnea', 'Cacturne', 'Swablu', 'Altaria', 'Zangoose', 'Seviper', 'Lunatone', 'Solrock', 'Barboach', 'Whiscash', 'Corphish', 'Crawdaunt', 'Baltoy', 'Claydol', 'Lileep', 'Cradily', 'Anorith', 'Armaldo', 'Feebas', 'Milotic', 'Castform', 'Kecleon', 'Shuppet', 'Banette', 'Duskull', 'Dusclops', 'Tropius', 'Chimecho', 'Absol', 'Wynaut', 'Snorunt', 'Glalie', 'Spheal', 'Sealeo', 'Walrein', 'Clamperl', 'Huntail', 'Gorebyss', 'Relicanth', 'Luvdisc', 'Bagon', 'Shelgon', 'Salamence', 'Beldum', 'Metang', 'Metagross', 'Regirock', 'Regice', 'Registeel', 'Latias', 'Latios', 'Kyogre', 'Groudon', 'Rayquaza', 'Jirachi', 'Deoxys', 'Turtwig', 'Grotle', 'Torterra', 'Chimchar', 'Monferno', 'Infernape', 'Piplup', 'Prinplup', 'Empoleon', 'Starly', 'Staravia', 'Staraptor', 'Bidoof', 'Bibarel', 'Kricketot', 'Kricketune', 'Shinx', 'Luxio', 'Luxray', 'Budew', 'Roserade', 'Cranidos', 'Rampardos', 'Shieldon', 'Bastiodon', 'Burmy', 'Wormadam', 'Mothim', 'Combee', 'Vespiquen', 'Pachirisu', 'Buizel', 'Floatzel', 'Cherubi', 'Cherrim', 'Shellos', 'Gastrodon', 'Ambipom', 'Drifloon', 'Drifblim', 'Buneary', 'Lopunny', 'Mismagius', 'Honchkrow', 'Glameow', 'Purugly', 'Chingling', 'Stunky', 'Skuntank', 'Bronzor', 'Bronzong', 'Bonsly', 'Mime Jr.', 'Happiny', 'Chatot', 'Spiritomb', 'Gible', 'Gabite', 'Garchomp', 'Munchlax', 'Riolu', 'Lucario', 'Hippopotas', 'Hippowdon', 'Skorupi', 'Drapion', 'Croagunk', 'Toxicroak', 'Carnivine', 'Finneon', 'Lumineon', 'Mantyke', 'Snover', 'Abomasnow', 'Weavile', 'Magnezone', 'Lickilicky', 'Rhyperior', 'Tangrowth', 'Electivire', 'Magmortar', 'Togekiss', 'Yanmega', 'Leafeon', 'Glaceon', 'Gliscor', 'Mamoswine', 'Porygon-Z', 'Gallade', 'Probopass', 'Dusknoir', 'Froslass', 'Rotom', 'Uxie', 'Mesprit', 'Azelf', 'Dialga', 'Palkia', 'Heatran', 'Regigigas', 'Giratina', 'Cresselia', 'Phione', 'Manaphy', 'Darkrai', 'Shaymin', 'Arceus', 'Victini', 'Snivy', 'Servine', 'Serperior', 'Tepig', 'Pignite', 'Emboar', 'Oshawott', 'Dewott', 'Samurott', 'Patrat', 'Watchog', 'Lillipup', 'Herdier', 'Stoutland', 'Purrloin', 'Liepard', 'Pansage', 'Simisage', 'Pansear', 'Simisear', 'Panpour', 'Simipour', 'Munna', 'Musharna', 'Pidove', 'Tranquill', 'Unfezant', 'Blitzle', 'Zebstrika', 'Roggenrola', 'Boldore', 'Gigalith', 'Woobat', 'Swoobat', 'Drilbur', 'Excadrill', 'Audino', 'Timburr', 'Gurdurr', 'Conkeldurr', 'Tympole', 'Palpitoad', 'Seismitoad', 'Throh', 'Sawk', 'Sewaddle', 'Swadloon', 'Leavanny', 'Venipede', 'Whirlipede', 'Scolipede', 'Cottonee', 'Whimsicott', 'Petilil', 'Lilligant', 'Basculin', 'Sandile', 'Krokorok', 'Krookodile', 'Darumaka', 'Darmanitan', 'Maractus', 'Dwebble', 'Crustle', 'Scraggy', 'Scrafty', 'Sigilyph', 'Yamask', 'Cofagrigus', 'Tirtouga', 'Carracosta', 'Archen', 'Archeops', 'Trubbish', 'Garbodor', 'Zorua', 'Zoroark', 'Minccino', 'Cinccino', 'Gothita', 'Gothorita', 'Gothitelle', 'Solosis', 'Duosion', 'Reuniclus', 'Ducklett', 'Swanna', 'Vanillite', 'Vanillish', 'Vanilluxe', 'Deerling', 'Sawsbuck', 'Emolga', 'Karrablast', 'Escavalier', 'Foongus', 'Amoonguss', 'Frillish', 'Jellicent', 'Alomomola', 'Joltik', 'Galvantula', 'Ferroseed', 'Ferrothorn', 'Klink', 'Klang', 'Klinklang', 'Tynamo', 'Eelektrik', 'Eelektross', 'Elgyem', 'Beheeyem', 'Litwick', 'Lampent', 'Chandelure', 'Axew', 'Fraxure', 'Haxorus', 'Cubchoo', 'Beartic', 'Cryogonal', 'Shelmet', 'Accelgor', 'Stunfisk', 'Mienfoo', 'Mienshao', 'Druddigon', 'Golett', 'Golurk', 'Pawniard', 'Bisharp', 'Bouffalant', 'Rufflet', 'Braviary', 'Vullaby', 'Mandibuzz', 'Heatmor', 'Durant', 'Deino', 'Zweilous', 'Hydreigon', 'Larvesta', 'Volcarona', 'Cobalion', 'Terrakion', 'Virizion', 'Tornadus', 'Thundurus', 'Reshiram', 'Zekrom', 'Landorus', 'Kyurem', 'Keldeo', 'Meloetta', 'Genesect', 'Chespin', 'Quilladin', 'Chesnaught', 'Fennekin', 'Braixen', 'Delphox', 'Froakie', 'Frogadier', 'Greninja', 'Bunnelby', 'Diggersby', 'Fletchling', 'Fletchinder', 'Talonflame', 'Scatterbug', 'Spewpa', 'Vivillon', 'Litleo', 'Pyroar', 'Flabebe', 'Floette', 'Florges', 'Skiddo', 'Gogoat', 'Pancham', 'Pangoro', 'Furfrou', 'Espurr', 'Meowstic', 'Honedge', 'Doublade', 'Aegislash', 'Spritzee', 'Aroma']

water_type_pokemon = ['Squirtle', 'Wartortle', 'Blastoise', 'Psyduck', 'Golduck', 'Poliwag', 'Poliwhirl', 'Poliwrath', 'Tentacool', 'Tentacruel', 'Slowpoke', 'Slowbro', 'Seel', 'Dewgong', 'Shellder', 'Cloyster', 'Krabby', 'Kingler', 'Horsea', 'Seadra', 'Goldeen', 'Seaking', 'Staryu', 'Starmie', 'Magikarp', 'Gyarados', 'Lapras', 'Vaporeon', 'Omanyte', 'Omastar', 'Kabuto', 'Kabutops', 'Totodile', 'Croconaw', 'Feraligatr', 'Chinchou', 'Lanturn', 'Marill', 'Azumarill', 'Politoed', 'Wooper', 'Quagsire', 'Slowking', 'Qwilfish', 'Corsola', 'Remoraid', 'Octillery', 'Suicune', 'Wobbuffet', 'Heracross', 'Sneasel', 'Teddiursa', 'Ursaring', 'Slugma', 'Magcargo', 'Swinub', 'Piloswine', 'Corsola', 'Delibird', 'Mantine', 'Kingdra', 'Phanpy', 'Donphan', 'Porygon2', 'Suicune', 'Tyranitar', 'Lugia', 'Ho-Oh', 'Mudkip', 'Marshtomp', 'Swampert', 'Lotad', 'Lombre', 'Ludicolo', 'Wingull', 'Pelipper', 'Surskit', 'Masquerain', 'Wailmer', 'Wailord', 'Swablu', 'Altaria', 'Whiscash', 'Chimecho', 'Wynaut', 'Spheal', 'Sealeo', 'Walrein', 'Clamperl', 'Huntail', 'Gorebyss', 'Relicanth', 'Luvdisc', 'Bagon', 'Shelgon', 'Salamence', 'Beldum', 'Metang', 'Metagross', 'Regice', 'Latias', 'Latios', 'Kyogre', 'Piplup', 'Prinplup', 'Empoleon', 'Bibarel', 'Buizel', 'Floatzel', 'Shellos', 'Gastrodon', 'Finneon', 'Lumineon', 'Mantyke', 'Phione', 'Manaphy', 'Oshawott', 'Dewott', 'Samurott', 'Panpour', 'Simipour', 'Tympole', 'Palpitoad', 'Seismitoad', 'Carracosta', 'Ducklett', 'Swanna', 'Frillish', 'Jellicent', 'Alomomola', 'Keldeo', 'Froakie', 'Frogadier', 'Greninja', 'Bunnelby', 'Diggersby', 'Binacle', 'Barbaracle', 'Skrelp', 'Dragalge', 'Clauncher', 'Clawitzer', 'Helioptile', 'Heliolisk', 'Goomy', 'Sliggoo', 'Goodra']

fire_type_pokemon = ['Charmander', 'Charmeleon', 'Charizard', 'Vulpix', 'Ninetales', 'Growlithe', 'Arcanine', 'Ponyta', 'Rapidash', 'Magmar', 'Flareon', 'Moltres', 'Cyndaquil', 'Quilava', 'Typhlosion', 'Slugma', 'Magcargo', 'Houndour', 'Houndoom', 'Magby', 'Entei', 'Torchic', 'Combusken', 'Blaziken', 'Numel', 'Camerupt', 'Torkoal', 'Castform', 'Chimchar', 'Monferno', 'Infernape', 'Magmortar', 'Heatran', 'Flame Plate', 'Pansear', 'Simisear', 'Darumaka', 'Darmanitan', 'Darmanitan (Galarian Zen Mode)', 'Litwick', 'Lampent', 'Chandelure', 'Heatmor', 'Fennekin', 'Braixen', 'Delphox', 'Litleo', 'Pyroar', 'Fletchinder', 'Talonflame', 'Larvesta', 'Volcarona', 'Fletchling', 'Litten', 'Torracat', 'Incineroar', 'Salandit', 'Salazzle', 'Turtonator', 'Blacephalon', 'Cinderace', 'Carkol', 'Coalossal', 'Sizzlipede', 'Centiskorch', 'Rolycoly', 'Cufant', 'Copperajah', 'Sizzlipede', 'Centiskorch']

grass_type_pokemon = ['Bulbasaur', 'Ivysaur', 'Venusaur', 'Oddish', 'Gloom', 'Vileplume', 'Paras', 'Parasect', 'Bellsprout', 'Weepinbell', 'Victreebel', 'Exeggcute', 'Exeggutor', 'Tangela', 'Chikorita', 'Bayleef', 'Meganium', 'Bellossom', 'Hoppip', 'Skiploom', 'Jumpluff', 'Sunkern', 'Sunflora', 'Celebi', 'Treecko', 'Grovyle', 'Sceptile', 'Lotad', 'Lombre', 'Ludicolo', 'Seedot', 'Nuzleaf', 'Shiftry', 'Shroomish', 'Breloom', 'Roselia', 'Gulpin', 'Swalot', 'Carvanha', 'Sharpedo', 'Wailmer', 'Wailord', 'Tropius', 'Cacnea', 'Cacturne', 'Lileep', 'Cradily', 'Turtwig', 'Grotle', 'Torterra', 'Chimchar', 'Monferno', 'Infernape', 'Piplup', 'Prinplup', 'Empoleon', 'Kricketot', 'Kricketune', 'Budew', 'Roserade', 'Cranidos', 'Rampardos', 'Cherubi', 'Cherrim', 'Grotle', 'Torterra', 'Gible', 'Gabite', 'Garchomp', 'Carnivine', 'Tangrowth', 'Leafeon', 'Shaymin', 'Snivy', 'Servine', 'Serperior', 'Pansage', 'Simisage', 'Cottonee', 'Whimsicott', 'Petilil', 'Lilligant', 'Maractus', 'Deerling', 'Sawsbuck', 'Foongus', 'Amoonguss', 'Ferroseed', 'Ferrothorn', 'Virizion', 'Chespin', 'Quilladin', 'Chesnaught', 'Skiddo', 'Gogoat', 'Phantump', 'Trevenant', 'Pumpkaboo', 'Gourgeist', 'Rowlet', 'Dartrix', 'Decidueye', 'Litten', 'Torracat', 'Incineroar', 'Popplio', 'Brionne', 'Primarina', 'Comfey', 'Oranguru', 'Passimian', 'Dhelmise', 'Steenee', 'Tsareena', 'Fomantis', 'Lurantis', 'Morelull', 'Shiinotic', 'Grookey', 'Thwackey', 'Rillaboom', 'Flapple', 'Appletun', 'Silicobra', 'Sandaconda', 'Cufant', 'Copperajah', 'Snom', 'Frosmoth', 'Grass Plate', 'Grassy Seed', 'Grassy Seed']

game_list = ['terraria', 'minecraft', 'celeste', 'zelda', 'hollow knight', 'super smash bros', 'valorant', 'super auto pets', 'roblox', 'dark souls', 'hades', 'dead cells', 'forager', 'cuphead', 'mario', 'fallout', 'skyrim', 'warframe', 'dont starve together', 'stardew valley', 'elden ring', 'enter the gungeon', 'karlson', 'rain world', "rust", 'raft', 'subnautica', 'plants vs zombies', 'pacman', 'fortnite', 'grand theft auto', 'tetris', 'overwatch', 'red dead redemption', 'wii sports', 'among us', 'bioshock', 'god of war', 'call of duty', 'undertale', 'metal gear solid', 'halo', 'diablo', 'apex legends', 'pokemon', 'rocket league', 'roblox', 'journey', 'outer wilds', 'portal', 'final fantasy', 'animal crossing', 'spiderman', 'borderlands', 'duck hunt', 'the walking dead', 'league of legends', 'mega man', 'titanfall', 'resident evil', 'mortal kombat', 'spelunky', 'donkey kong', 'the sims', 'tomb raider', 'earthbound', 'starcraft', 'the last of us', 'doom', 'street fighter', 'bloodborne', 'the witcher', 'binding of isaac', 'destiny', 'fall guys', 'geometry dash', 'little nightmares', 'muck', 'octodad', 'oneshot', 'super meat boy', 'slime rancher']

food_list = ['apple', 'banana', 'orange', 'strawberry', 'blueberry', 'grape', 'watermelon', 'pineapple', 'kiwi', 'mango', 'lemon', 'lime', 'peach', 'pear', 'cherry', 'plum', 'raspberry', 'blackberry', 'avocado', 'coconut', 'pomegranate', 'fig', 'melon', 'apricot', 'guava', 'passion fruit', 'grapefruit', 'papaya', 'dragon fruit', 'cantaloupe', 'cranberry', 'date', 'honeydew', 'star fruit', 'bread', 'rice', 'pasta', 'potato', 'corn', 'wheat', 'oats', 'rye', 'beans', 'peas', 'carrot', 'broccoli', 'spinach', 'lettuce', 'tomato', 'cucumber', 'bell pepper', 'onion', 'garlic', 'ginger', 'celery', 'zucchini', 'eggplant', 'asparagus', 'cauliflower', 'brussels sprouts', 'cabbage', 'kale', 'mushroom', 'sweet potato', 'beet', 'radish', 'turnip', 'leek', 'parsnip', 'artichoke', 'pumpkin', 'squash', 'spaghetti', 'sunflower seeds', 'pumpkin seeds', 'sesame seeds', 'poppy seeds', 'peanut', 'almond', 'cashew', 'walnut', 'pecan', 'hazelnut', 'pistachio', 'macadamia', 'chestnut', 'peanut butter', 'butter', 'cheese', 'milk', 'yogurt', 'sour cream', 'cream cheese' 'cheese', 'chocolate', 'ice cream', 'sherbet', 'pudding', 'cake', 'pie', 'cookie', 'brownie', 'cupcake', 'muffin', 'donut', 'pancake', 'waffle', 'croissant', 'bagel', 'breadstick', 'pretzel', 'cracker', 'chips', 'popcorn', 'nacho', 'sandwich', 'burger', 'hot dog', 'pizza', 'pasta', 'salad', 'soup', 'stew', 'curry', 'sushi', 'noodles', 'taco', 'burrito', 'quesadilla', 'enchilada', 'chimichanga', 'tortilla', 'guacamole', 'salsa', 'honey', 'pickles', 'olives', 'anchovy', 'salmon', 'tuna', 'shrimp', 'lobster', 'crab', 'oyster', 'mussels', 'clams', 'squid', 'octopus', 'bacon', 'sausage', 'ham', 'steak', 'pork', 'beef', 'salami', 'pepperoni']

animal_list = ['dog', 'cat', 'horse', 'elephant', 'tiger', 'lion', 'giraffe', 'zebra', 'monkey', 'gorilla', 'bear', 'panda', 'koala', 'kangaroo', 'hippo', 'rhino', 'camel', 'sheep', 'goat', 'cow', 'pig', 'rabbit', 'mouse', 'rat', 'hamster', 'guinea pig', 'chicken', 'duck', 'goose', 'turkey', 'eagle', 'hawk', 'owl', 'peacock', 'penguin', 'dolphin', 'whale', 'shark', 'seal', 'seahorse', 'jellyfish', 'octopus', 'crab', 'lobster', 'turtle', 'snake', 'lizard', 'crocodile', 'alligator', 'frog', 'toad', 'butterfly', 'bee', 'ant', 'spider', 'scorpion', 'snail', 'caterpillar', 'moth', 'dragonfly', 'cockroach', 'mosquito', 'goldfish', 'shrimp', 'starfish', 'flamingo', 'ostrich', 'crow', 'sparrow', 'hummingbird', 'woodpecker', 'pigeon', 'robin', 'beetle', 'grasshopper', 'cricket', 'ladybug', 'cicada', 'termite', 'antelope', 'buffalo', 'cheetah', 'chimpanzee', 'coyote', 'deer', 'fox', 'hyena', 'leopard', 'lynx', 'mole', 'orangutan', 'otter', 'platypus', 'porcupine', 'raccoon', 'squirrel', 'weasel', 'wolf', 'chinchilla', 'alpaca', 'parrot', 'gazelle', 'panther', 'wombat', 'moose', 'jaguar', 'hedgehog', 'tarantula', 'lemur', 'quokka', 'cobra', 'anteater', 'armadillo', 'kiwi', 'narwhal', 'walrus', 'bluefooted booby', 'dugong', 'sloth', 'peccary', 'ocelot', 'sugar glider', 'liger', 'mantis', 'prairie dog', 'axolotl', 'falcon', 'dinosaur']

randomWords = ['ant', 'basketball', 'almond', 'batteries', 'cellphone', 'seal', 'cushion', 'octopus', 'park', 'clams', 'flamingo', 'passion fruit', 'tie', 'bus', 'comic', 'cricket', 'jacket', 'yogurt', 'rug', 'grass', 'vacuum cleaner', 'quesadilla', 'cheetah', 'ostrich', 'television', 'ladybug', 'elephant', 'pomegranate', 'sherbet', 'taco', 'hospital', 'watch', 'weasel', 'broccoli', 'door', 'crayons', 'bed', 'avocado', 'cap', 'bananas', 'grapes', 'water', 'key', 'pancake', 'tortilla', 'cantaloupe', 'street', 'syrup', 'necklace', 'flowers', 'ink', 'asparagus', 'pie', 'cauliflower', 'clothes', 'cicada', 'goldfish', 'artichoke', 'squash', 'honeydew', 'clay', 'hairbrush', 'eraser', 'butter', 'salmon', 'tree', 'coffee', 'pecan', 'orangutan', 'glow', 'milk', 'cracker', 'papaya', 'croissant', 'hamster', 'beans', 'sparrow', 'window', 'pretzel', 'enchilada', 'rabbit', 'frog', 'sofa', 'bear', 'anchovy', 'zucchini', 'gloves', 'spinach', 'telephone', 'knife', 'paper', 'robin', 'rain', 'carrot', 'computer', 'beach', 'waffle', 'deer', 'rice', 'carrots', 'rubber', 'shampoo', 'candlestick', 'popcorn', 'bat', 'lotion', 'radio', 'woodpecker', 'pistachio', 'conditioner', 'button', 'bonesaw', 'blackberry', 'pot', 'bottle', 'mango', 'painting', 'duck', 'canvas', 'sushi', 'olives', 'card', 'curtain', 'sunflower seeds', 'chocolate', 'chimichanga', 'watermelon', 'tea', 'cashew', 'drill', 'salsa', 'donut', 'lettuce', 'pan', 'beater', 'horse', 'sausage', 'ham', 'strawberry', 'beetle', 'fox', 'lamb', 'goose', 'chimpanzee', 'oats', 'zebra', 'garage', 'buckle', 'keys', 'toad', 'noodles', 'pudding', 'radish', 'cow', 'plum', 'rat', 'fish', 'coat', 'kangaroo', 'boom', 'check', 'markers', 'deodorant', 'jar', 'burger', 'lynx', 'steak', 'food', 'acorn', 'muffin', 'celery', 'soap', 'chips', 'hawk', 'notebook', 'apple', 'drawer', 'blanket', 'car', 'pigeon', 'peanut butter', 'hammer', 'candy', 'chili', 'cat', 'sweet potato', 'cane', 'hippo', 'monkey', 'cockroach', 'pumpkin seeds', 'porcupine', 'dog', 'cat', 'horse', 'elephant', 'tiger', 'lion', 'giraffe', 'zebra', 'monkey', 'gorilla', 'bear', 'panda', 'koala', 'kangaroo', 'hippo', 'rhino', 'camel', 'sheep', 'goat', 'cow', 'pig', 'rabbit', 'mouse', 'rat', 'hamster', 'guinea pig', 'chicken', 'duck', 'goose', 'turkey', 'eagle', 'hawk', 'owl', 'peacock', 'penguin', 'dolphin', 'whale', 'shark', 'seal', 'seahorse', 'jellyfish', 'octopus', 'crab', 'lobster', 'turtle', 'snake', 'lizard', 'crocodile', 'alligator', 'frog', 'toad', 'butterfly', 'bee', 'ant', 'spider', 'scorpion', 'snail', 'caterpillar', 'moth', 'dragonfly', 'cockroach', 'mosquito', 'goldfish', 'shrimp', 'starfish', 'flamingo', 'ostrich', 'crow', 'sparrow', 'hummingbird', 'woodpecker', 'pigeon', 'robin', 'beetle', 'grasshopper', 'cricket', 'ladybug', 'cicada', 'termite', 'antelope', 'buffalo', 'cheetah', 'chimpanzee', 'coyote', 'deer', 'fox', 'hyena', 'leopard', 'lynx', 'mole', 'orangutan', 'otter', 'platypus', 'porcupine', 'raccoon', 'squirrel', 'weasel', 'wolf', 'chinchilla', 'alpaca', 'parrot', 'panther', 'wombat', 'moose', 'jaguar', 'hedgehog', 'tarantula', 'gazelle', 'lemur', 'quokka', 'cobra', 'anteater', 'armadillo', 'kiwi', 'narwhal', 'walrus', 'bluefooted booby', 'dugong', 'sloth', 'peccary', 'ocelot', 'sugar glider', 'liger', 'mantis', 'prairie dog', 'axolotl', 'falcon', 'dinosaur', 'ginger', 'laptop', 'earrings', 'goat', 'curry', 'sculpture', 'phone', 'football', 'lion', 'wallet', 'cream', 'pills', 'beet', 'razor', 'onion', 'cake', 'egg', 'soda', 'timer', 'wheat', 'cream cheesecheese', 'dragon fruit', 'socks', 'mirror', 'sheep', 'poppy seeds', 'guava', 'kitchen', 'guinea pig', 'grasshopper', 'drink', 'hat', 'bacon', 'guacamole', 'craft', 'tablet', 'dining room', 'umbrella', 'tissues', 'bell', 'lamp', 'nacho', 'apricot', 'lemon', 'hummingbird', 'refrigerator', 'kiwi', 'pork', 'sun', 'cupcake', 'sunscreen', 'whale', 'dagger', 'baking', 'chicken', 'extension', 'cement', 'comb', 'toothbrush', 'garden', 'bandana', 'pen', 'walnut', 'shoes', 'restaurant', 'office', 'termite', 'dress', 'fork', 'train', 'shark', 'honey', 'toothpaste', 'mushroom', 'jellyfish', 'plate', 'chestnut', 'chain', 'stars', 'sour cream', 'pineapple', 'polish', 'cotton', 'moth', 'handbasket', 'ribbon', 'paint', 'calculator', 'snake', 'tin', 'keyboard', 'potato', 'penguin', 'cabbage', 'washing machine', 'lizard', 'wolf', 'corn', 'seahorse', 'brussels sprouts', 'spider', 'hyena', 'glass', 'peanut', 'bagel', 'pumpkin', 'bread', 'juice', 'spaghetti', 'melon', 'platypus', 'squid', 'bowl', 'cloud', 'wash', 'headphones', 'shrimp', 'clip', 'owl', 'snow', 'turnip', 'candle', 'coyote', 'alligator', 'pepper', 'sandwich', 'living room', 'chocolates', 'macadamia', 'tuna', 'catalogue', 'grocery', 'oyster', 'turtle', 'salad', 'blowdryer', 'blouse', 'grapefruit', 'domino', 'building', 'parsnip', 'duster', 'charger', 'chair', 'marker', 'koala', 'mussels', 'bookmark', 'chalk', 'dragonfly', 'mole', 'ring', 'kale', 'bicycle', 'peas', 'remote', 'floor', 'cherry', 'pillow', 'sesame seeds', 'stew', 'shower', 'lobster', 'spade', 'glasses', 'peach', 'bedroom', 'sugar', 'turkey', 'mountain', 'giraffe', 'bridge', 'grape', 'otter', 'fig', 'school', 'salami', 'tiger', 'skirt', 'cars', 'dictionary', 'ice cream', 'pasta', 'salt', 'mosquito', 'toilet', 'buffalo', 'rye', 'pickles', 'blueberry', 'snail', 'raccoon', 'date', 'soup', 'brownie', 'moon', 'tablecloth', 'teapot', 'fan', 'eggplant', 'book', 'leek', 'perfume', 'game', 'star fruit', 'pizza', 'CD', 'ornament', 'garlic', 'spoon', 'pencil', 'plane', 'hook', 'caterpillar', 'crowbar', 'flashlight', 'burrito', 'raspberry', 'tomato', 'cranberry', 'chenille', 'cucumber', 'lime', 'ice', 'ship', 'peacock', 'canteen', 'brush', 'dolphin', 'battery', 'antelope', 'shirt', 'gorilla', 'pig', 'mouse', 'bee', 'lock', 'fridge', 'bell pepper', 'belt', 'camera', 'oven', 'coconut', 'squirrel', 'starfish', 'leopard', 'baseball', 'scarf', 'yarn', 'feather', 'sink', 'pin', 'empty', 'glue', 'beef', 'breadstick', 'crow', 'mug', 'cup', 'banana', 'hazelnut', 'bag', 'pants', 'jokes', 'cork', 'bow', 'butterfly', 'oil', 'flag', 'terraria', 'minecraft', 'celeste', 'zelda', 'hollow knight', 'super smash bros', 'valorant', 'super auto pets', 'roblox', 'dark souls', 'hades', 'dead cells', 'forager', 'cuphead', 'mario', 'fallout', 'skyrim', 'warframe', 'dont starve together', 'stardew valley', 'elden ring', 'enter the gungeon', 'karlson', 'rain world', "rust", 'raft', 'subnautica', 'plants vs zombies', 'pacman', 'fortnite', 'grand theft auto', 'tetris', 'overwatch', 'red dead redemption', 'wii sports', 'among us', 'bioshock', 'god of war', 'call of duty', 'undertale', 'metal gear solid', 'halo', 'diablo', 'apex legends', 'pokemon', 'rocket league', 'roblox', 'journey', 'outer wilds', 'portal', 'final fantasy', 'animal crossing', 'spiderman', 'borderlands', 'duck hunt', 'the walking dead', 'league of legends', 'mega man', 'titanfall', 'resident evil', 'mortal kombat', 'spelunky', 'donkey kong', 'the sims', 'tomb raider', 'earthbound', 'starcraft', 'the last of us', 'doom', 'street fighter', 'bloodborne', 'the witcher', 'binding of isaac', 'destiny', 'fall guys', 'geometry dash', 'little nightmares', 'muck', 'octodad', 'oneshot', 'super meat boy', 'slime rancher']

HANGMANPICS = ['''
⠀+---+
    |      |
           |
           |
           |
           |
=========''', '''
⠀+---+
    |      |
    0     |
           |
           |
           |
=========''', '''
⠀+---+
    |      |
    0     |
    |      |
           |
           |
=========''', '''
⠀+---+
    |      |
    0     |
   /|     |
           |
           |
=========''', '''
⠀+---+
    |      |
    0     |
   /|\   |
           |
           |
=========''', '''
⠀+---+
    |      |
    0     |
   /|\   |
   /      |
           |
=========''', '''
⠀+---+
    |      |
    0     |
   /|\   |
   / \   |
           |
=========''']

lookup = {
    "points": "points",
    "point": "points",
    "coins": "coins",
    "coin": "coins",
    "daily": "total_daily",
    "streak": "daily_streak",
    "rps": "rps_wins",
    "hm": "hm_wins"
}

def lbhelp(user, amount, count):
    return f"{count + 1}. **{user.display_name}**: __{amount}__\n"

secret_badges = {
    1: "bean_crew",
    2: "gamer",
    3: "nerd",
    4: "beans",
    5: "santa",
    6: "nice_lad",
    7: "funny_lad",
    8: "rep",
    9: "rps",
    10: "hm",
    11: "cake",
    12: "profile"
}

def inv_background(user:discord.Member):
    background = Backgrounds(None, user)
    have = background.have
    count = 0
    msg = ""
    
    for n in have:
        background = Backgrounds(n)
        if count % 4 == 0 and count != 0:
            msg += f"`bg{background.id}`┃\n"
            count += 1
        else:
            msg += f"`bg{background.id}`┃"
            count += 1

    return msg

def inv_gear(user:discord.Member):
    gear = Gear(None, user)
    have = gear.have
    count = 0
    msg = ""
    
    for n in have:
        gear = Gear(n)
        if count % 4 == 0 and count != 0:
            msg += f"`ad{gear.id}`┃\n"
            count += 1
        else:
            msg += f"`ad{gear.id}`┃"
            count += 1

    return msg

def inv_color(user:discord.Member):
    color = Colors(None, user)
    have = color.have
    count = 0
    msg = ""
    
    for n in have:
        color = Colors(n)
        if count % 4 == 0 and count != 0:
            msg += f"`col{color.id}`┃\n"
            count += 1
        else:
            msg += f"`col{color.id}`┃"
            count += 1

    return msg

def inv_font(user:discord.Member):
    font = Fonts(None, user)
    have = font.have
    count = 0
    msg = ""
    
    for n in have:
        font = Fonts(n)
        if count % 4 == 0 and count != 0:
            msg += f"`font{font.id}`┃\n"
            count += 1
        else:
            msg += f"`font{font.id}`┃"
            count += 1

    return msg

def niceNum(message):
    try:
        return '{:,}'.format(int(message))
    except:
        return message

async def lottery_win(ctx, bot):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    
    until = timedelta(days=7)
    cursor.execute("SELECT lottery_cooldown FROM global")
    timer = cursor.fetchone()[0]
    if time_check(None, "lottery_cooldown", "global") < 1:
        now = datetime.now().replace(microsecond=0)
    else:
        now = datetime.strptime(timer, '%Y-%m-%d %H:%M:%S')
    then = now + until
    cursor.execute(f"UPDATE global SET lottery_cooldown = '{then}'")
    db.commit()
    users = cursor.execute("SELECT id FROM main WHERE tickets > 0").fetchall()
    
    players = {i[0]: get_user_tickets(await bot.fetch_user(i[0])) for i in users if await bot.fetch_user(i[0]) != None}
    pool = random.choices(list(players.keys()), weights=list(players.values()), k=sum(list(players.values())))
    winner = bot.get_user(random.choice(pool))
    with sqlite3.connect("main.sqlite") as cursor:
        cursor.execute(f"UPDATE main SET points = {get_user_points(winner) + get_lottery_pot()} WHERE id = {winner.id}")
        cursor.execute("UPDATE global SET lottery = 0")
        cursor.execute("UPDATE main SET tickets = 0")
    cursor.close()
    say = bot.get_channel(1109613004091310120)
    await ctx.reply(f"**{winner.display_name}** won the lottery!")
    await say.send(f"**{winner.display_name}** won the lottery!")

def textLen(msg):
    if len(msg) <= 5:
        return len(msg) * 28
    elif len(msg) <= 10:
        return len(msg) * 24
    else:
        return len(msg) * 22

class Colors:
    def __init__(self, id:str=None, user:discord.Member=None):
        self.roles = [1120221887264469002, 1120221954784362618, 1120221814669455492, 1120221959238725682, 1120221962162159658, 1120221966142558258, 1120221976364064829, 1120221979807600680, 1120221984211615805, 1120221987340554330, 1120221990775701544, 1120221993749454888, 1120221996219904020, 1120221999554383942, 1120222002796576780, 1120222006084898877, 1120222008958013471, 1120222011814314104, 1120222014523850884, 1129129760040165438, 1129129788905357422]
        if user != None:
            have = get_user_color_have(user)
            have2 = have.split(",")
            self.dbHave = have
            self.have = [n for n in have2]
        if id is None:
            self.name = None
            self.id = None
            self.hex = None
            self.role = None
            self.type = None
        id = str(id)
        if id == '1':
            self.name = "Pastel Green"
            self.id = id
            self.hex = "#a3ffac"
            self.role = 1120221887264469002
            self.type = "color"
        elif id == '2':
            self.name = "Pastel Blue"
            self.id = id
            self.hex = "#b8e4ff"
            self.role = 1120221954784362618
            self.type = "color"
        elif id == '3':
            self.name = "Pastel Cyan"
            self.id = id
            self.hex = "#a4d8d8"
            self.role = 1120221814669455492
            self.type = "color"
        elif id == '4':
            self.name = "Pastel Purple"
            self.id = id
            self.hex = "#e79eff"
            self.role = 1120221959238725682
            self.type = "color"
        elif id == '5':
            self.name = "Pastel Red"
            self.id = id
            self.hex = "#ff8097"
            self.role = 1120221962162159658
            self.type = "color"
        elif id == '6':
            self.name = "Pastel Yellow"
            self.id = id
            self.hex = "#eaffc2"
            self.role = 1120221966142558258
            self.type = "color"
        elif id == '7':
            self.name = "Pastel Orange"
            self.id = id
            self.hex = "#ffca99"
            self.role = 1120221976364064829
            self.type = "color"
        elif id == '8':
            self.name = "Pastel Pink"
            self.id = id
            self.hex = "#ff85d5"
            self.role = 1120221979807600680
            self.type = "color"
        elif id == '9':
            self.name = "Pastel Brown"
            self.id = id
            self.hex = "#b1907f"
            self.role = 1120221984211615805
            self.type = "color"
        elif id == '10':
            self.name = "Green"
            self.id = id
            self.hex = "#00ff00"
            self.role = 1120221987340554330
            self.type = "color"
        elif id == '11':
            self.name = "Blue"
            self.id = id
            self.hex = "#0000ff"
            self.role = 1120221990775701544
            self.type = "color"
        elif id == '12':
            self.name = "Cyan"
            self.id = id
            self.hex = "#00ffff"
            self.role = 1120221993749454888
            self.type = "color"
        elif id == '13':
            self.name = "Purple"
            self.id = id
            self.hex = "#d900ff"
            self.role = 1120221996219904020
            self.type = "color"
        elif id == '14':
            self.name = "Red"
            self.id = id
            self.hex = "#ff0000"
            self.role = 1120221999554383942
            self.type = "color"
        elif id == '15':
            self.name = "Yellow"
            self.id = id
            self.hex = "#ffff00"
            self.role = 1120222002796576780
            self.type = "color"
        elif id == '16':
            self.name = "Orange"
            self.id = id
            self.hex = "#ff6a00"
            self.role = 1120222006084898877
            self.type = "color"
        elif id == '17':
            self.name = "Orange"
            self.id = id
            self.hex = "#ff00ff"
            self.role = 1120222008958013471
            self.type = "color"
        elif id == '18':
            self.name = "Brown"
            self.id = id
            self.hex = "#964b00"
            self.role = 1120222011814314104
            self.type = "color"
        elif id == '19':
            self.name = "Ice Blue"
            self.id = id
            self.hex = "#dcf3ff"
            self.role = 1120222014523850884
            self.type = "color"
        elif id == '20':
            self.name = "White"
            self.id = id
            self.hex = "#ffffff"
            self.role = 1129129760040165438
            self.type = "color"
        elif id == '21':
            self.name = "Black"
            self.id = id
            self.hex = "#000000"
            self.role = 1129129788905357422
            self.type = "color"
        elif id == '22':
            self.name = "Navy Blue"
            self.id = id
            self.hex = "#07192B"
            self.role = None
            self.type = "N/A"
        elif id == '23':
            self.name = "Seal Blubber Blue"
            self.id = id
            self.hex = "#8288ab"
            self.role = None
            self.type = "N/A"
        elif id == '24':
            self.name = "Lavender Blue"
            self.id = id
            self.hex = "#afa6f7"
            self.role = None
            self.type = "N/A"
        elif id == '25':
            self.name = "Salmon Pink"
            self.id = id
            self.hex = "#ffe4e4"
            self.role = None
            self.type = "N/A"
        elif id == '26':
            self.name = "Dried Clay Brown"
            self.id = id
            self.hex = "#615A55"
            self.role = None
            self.type = "N/A"
        elif id == '27':
            self.name = "Mud Brown"
            self.id = id
            self.hex = "#40322d"
            self.role = None
            self.type = "N/A"
        elif id == '28':
            self.name = "Barrel Brown"
            self.id = id
            self.hex = "#c4b199"
            self.role = None
            self.type = "N/A"
        elif id == '29':
            self.name = "Forest Green"
            self.id = id
            self.hex = "#2b4029"
            self.role = None
            self.type = "N/A"
        elif id == '30':
            self.name = "Moss Green "
            self.id = id
            self.hex = "#7d947b "
            self.role = None
            self.type = "N/A"
        elif id == '31':
            self.name = "Cream Soda Orange"
            self.id = id
            self.hex = "#ffa66b"
            self.role = None
            self.type = "N/A"
        else:
            self.name = "Error"
            self.id = "Error"
            self.hex = "Error"
            self.role = "Error"

class Backgrounds:
    def __init__(self, id:str=None, user:discord.Member=None):
        self.commons = 7
        self.rares = 3
        self.legendaries = 2
        if user != None:
            have = get_user_background_have(user)
            have2 = have.split(",")
            self.dbHave = have
            self.have = [n for n in have2]
        if id is None:
            self.name = None
            self.id = None
            self.type = None
            self.link = None
        id = str(id)
        if id == '1':
            self.name = "Pastel Green"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/yMpej5e.png"
        elif id == '2':
            self.name = "Pastel Blue"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/W8O0mhJ.png"
        elif id == '3':
            self.name = "Pastel Cyan"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/lni2226.png"
        elif id == '4':
            self.name = "Pastel Purple"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/aEdM15C.png"
        elif id == '5':
            self.name = "Pastel Red"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/1o2ZDpj.png"
        elif id == '6':
            self.name = "Pastel Yellow"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/ow7w7dR.png"
        elif id == '7':
            self.name = "Pastel Orange"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/mDqyGiv.png"
        elif id == '8':
            self.name = "Pastel Pink"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/aEdM15C.png"
        elif id == '9':
            self.name = "Pastel Brown"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/ahyA5HS.png"
        elif id == '10':
            self.name = "Green"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/EI87efE.png"
        elif id == '11':
            self.name = "Blue"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/YJZBRyR.png"
        elif id == '12':
            self.name = "Cyan"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/lbyA89a.png"
        elif id == '13':
            self.name = "Purple"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/29UIpBP.png"
        elif id == '14':
            self.name = "Red"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/c7AgGqc.png"
        elif id == '15':
            self.name = "Yellow"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/8nUCeno.png"
        elif id == '16':
            self.name = "Orange"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/k6Xy5BK.png"
        elif id == '17':
            self.name = "Pink"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/pRcI4fa.png"
        elif id == '18':
            self.name = "Brown"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/qnUqfeG.png"
        elif id == '19':
            self.name = "Ice Blue"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/qecVHOT.png"
        elif id == '20':
            self.name = "Black"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/AHAtCyH.png"
        elif id == '21':
            self.name = "White"
            self.id = id
            self.type = "solid"
            self.link = "https://i.imgur.com/KA26ggC.png"
        elif id == '22':
            self.name = "Clouds 1"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/eScDkJL.png"
        elif id == '23':
            self.name = "Clouds 2"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/Y7BOzsh.png"
        elif id == '24':
            self.name = "Cyberpunk"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/mLr85xs.png"
        elif id == '25':
            self.name = "Felix"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/LlS663x.png"
        elif id == '26':
            self.name = "Nebula"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/sHgOS0s.png"
        elif id == '27':
            self.name = "Mountain 1"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/vzNa7iQ.png"
        elif id == '28':
            self.name = "Mountain 2"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/6J54C7Z.png"
        elif id == '29':
            self.name = "Emoji"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/5Frivg9.png"
        elif id == '30':
            self.name = "Mountain 3"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/CxSTuNU.png"
        elif id == '31':
            self.name = "Silly Cat"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/ordSV4p.png"
        elif id == '32':
            self.name = "Silly Dog"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/WOeHbvt.png"
        elif id == '33':
            self.name = "Star Sky"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/k3HosfN.png"
        elif id == '34':
            self.name = "Sunset"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/dkVp0J8.png"
        elif id == '35':
            self.name = "Vaporwave"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/XaEvXUa.png"
        elif id == '36':
            self.name = "Bean Man"
            self.id = id
            self.type = "picture"
            self.link = "https://i.imgur.com/FciDcLG.png"
        elif id == "C1":
            self.name = "City Building 1"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/Dtrp8GL.png"
        elif id == "C2":
            self.name = "City Building 2"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/j9EavOC.png"
        elif id == "C3":
            self.name = "Snowy Land"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/RvzLcyc.png"
        elif id == "C4":
            self.name = "Rocky River"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/ZpAyCXX.png"
        elif id == "C5":
            self.name = "River Mountain"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/2YMNZMY.png"
        elif id == "C6":
            self.name = "Mountain Edge"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/jPihBM0.png"
        elif id == "C7":
            self.name = "Mountain 3"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/RMHKcxP.png"
        elif id == "R1":
            self.name = "Night City 1"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/4IGuzra.png"
        elif id == "R2":
            self.name = "Night City 2"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/Sc5f1ip.png"
        elif id == "R3":
            self.name = "Night City 3"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/PhU1FdQ.png"
        elif id == "L1":
            self.name = "Retro Land 1"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/g6fe2hg.png"
        elif id == "L2":
            self.name = "Retro Land 2"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/slD2eIa.png"
        else:
            self.name = "Error"
            self.id = "Error"
            self.type = "Error"
            self.link = "Error"

class Gear:
    def __init__(self, id:str=None, user:discord.Member=None):
        self.commons = 2
        self.rares = 3
        self.legendaries = 2
        if user != None:
            have = get_user_gear_have(user)
            have2 = have.split(",")
            self.dbHave = have
            self.have = [n for n in have2]
        if id is None:
            self.name = None
            self.id = None
            self.type = None
            self.link = None
        id = str(id)
        if id == '0':
            self.name = "None"
            self.id = id
            self.type = "None"
            self.link = "None"
        elif id == '1':
            self.name = "Santa Hat"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/V7XbrV1.png"
        elif id == '2':
            self.name = "Cat Ears"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/NHYvLBR.png"
        elif id == '3':
            self.name = "Fedora"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/vpEH2WX.png"
        elif id == '4':
            self.name = "Tophat"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/ybgPHns.png"
        elif id == '5':
            self.name = "Beanie"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/CfUVD15.png"
        elif id == '6':
            self.name = "Cheese"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/BXj5TKk.png"
        elif id == '7':
            self.name = "Felix Ears"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/gQojwks.png"
        elif id == '8':
            self.name = "Bean"
            self.id = id
            self.type = "gear"
            self.link = "https://i.imgur.com/ZxU4Hpr.png"
        elif id == "C1":
            self.name = "Party Hat"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/jF7riJE.png"
        elif id == "C2":
            self.name = "Freeze"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/NgEaA5k.png"
        elif id == "R1":
            self.name = "Neon Red"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/WZKG6Ux.png"
        elif id == "R2":
            self.name = "Neon Blue"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/s7FMBvF.png"
        elif id == "R3":
            self.name = "Neon Green"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/uNcA83k.png"
        elif id == "L1":
            self.name = "Pet Emoji"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/EBoCmG3.png"
        elif id == "L2":
            self.name = "Pet Dog"
            self.id = id
            self.type = "N/A"
            self.link = "https://i.imgur.com/jHH4l85.png"
        else:
            self.name = "Error"
            self.id = "Error"
            self.type = "Error"
            self.link = "Error"

class Fonts:
    def __init__(self, id:str=None, user:discord.Member=None):
        if user != None:
            have = get_user_font_have(user)
            have2 = have.split(",")
            self.dbHave = have
            self.have = [n for n in have2]
        if id is None:
            self.name = None
            self.id = None
            self.type = None
        id = str(id)
        if id == '1':
            self.name = "Font 1"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/ZmMgP83"
        elif id == '2':
            self.name = "Font 2"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/KJdxdO8"
        elif id == '3':
            self.name = "Font 3"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/uGKnROK"
        elif id == '4':
            self.name = "Font 4"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/Pzz7krm"
        elif id == '5':
            self.name = "Font 5"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/uZPhMw7"
        elif id == '6':
            self.name = "Font 6"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/y9xhnAk"
        elif id == '7':
            self.name = "Font 7"
            self.id = id
            self.type = "font"
            self.link = "https://imgur.com/jqkMSPM"
        else:
            self.name = "Error"
            self.id = "Error"
            self.type = "Error"
            self.link = "Error"

class RegularShop:
    def __init__(self, id:str, user:discord.Member):
        if id is None:
            self.name = None
            self.id = None
            self.type = None
            self.have = None
        id = str(id)
        if id == "butter":
            self.name = "Butter"
            self.id = id
            self.type = "butter"
            self.have = get_user_butter(user)
        elif id == "darkness":
            self.name = "Darkness"
            self.id = id
            self.type = "darkness"
            self.have = get_user_darkness(user)
        elif id == "random":
            self.name = "Random"
            self.id = id
            self.type = "random"
            self.have = get_user_random(user)
        elif id == "hunger":
            self.name = "Hunger"
            self.id = id
            self.type = "hunger"
            self.have = get_user_hunger(user)
        elif id == "imposter":
            self.name = "Imposter"
            self.id = id
            self.type = "imposter"
            self.have = get_user_imposter(user)
        elif id == "nitro":
            self.name = "Nitro"
            self.id = id
            self.type = "nitro"
            self.have = get_user_butter(user)
        elif id == "beans":
            self.name = "Beans"
            self.id = id
            self.type = "beans"
            self.have = get_user_beans(user)
        else:
            self.name = "Error"
            self.id = "Error"
            self.type = "Error"
            self.have = "Error"