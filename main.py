import discord
from discord import Intents, app_commands
from discord.ext import commands
import os, time, random, sqlite3, asyncio
import utils, game_utils
import datetime
from datetime import datetime, timedelta
from easy_pil import Editor, Canvas, load_image_async, Font
from contextlib import closing

token = os.environ.get("token")
intents = discord.Intents().all()
bot_prefix = commands.when_mentioned_or("b!", "B!", "b?", "B?")
bot = commands.Bot(command_prefix=bot_prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')

initial_extensions = ["cogs.admin", "cogs.economy", "cogs.fun", "cogs.games", "cogs.help", "cogs.sabotages"]

async def load():
    for filename in initial_extensions:
        await bot.load_extension(filename)

async def main():
    async with bot:
        await load()
        await bot.start(token)

@bot.event
async def on_ready():
    with sqlite3.connect('main.sqlite') as cursor:
        cursor.execute("UPDATE main SET game_playing = 'not playing'")
    cursor.close()
    activity = discord.Game(name="b!help", type = 1)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bean Man Online!\nSyncing commands...")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    msg = message.content
    if message.channel.id == 1109612661643161620:
        if message.content == "<:BeanMan:1110981189466079274>":
            await utils.secret_add(1114975229253525625, "Bean Crew", message.author, message, "bean_crew")
    if message.channel.id == 1109614615442243725:
        if msg.lower() in ["hug", "hugs"]:
            await utils.secret_add(1118016271867445258, "Nice Lad", message.author, message, "nice_lad")
    if message.channel.id == 1109614899648270357:
        if msg.lower() in ["beans", "bean", ":beans:"]:
            await utils.secret_add(1114995433496903792, "Beans", message.author, message, "beans")
    if msg.lower() == "up up down down left right left right b a start":
        await utils.secret_add(1114985995536965822, "Gamer", message.author, message, "gamer")
    if message.channel.id == 1109612143512408085:
        await utils.secret_add(1124356650728423456, "Funny Lad", message.author, message, "funny_lad")
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    emoji = payload.emoji.name
    reaction = discord.utils.get(message.reactions, emoji=emoji)
    if payload.message_id == 1109600687551172658:
        await utils.secret_add(1114984409377034290, "Nerd", user, message, "nerd")

@bot.event
async def on_member_join(member:discord.Member):
    if member.guild.id == 1109586411058901152:
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        logs = bot.get_channel(1109590623012524063)
        cursor.execute(f"SELECT team FROM main WHERE id = {member.id}")
        result = cursor.fetchone()
        first = False
        
        if result is None:
            utils.db_make(member)
            
        result = utils.get_user_team(member)
        
        if result == 0:
            first = True
            
        if not first:
            team = utils.get_user_team(member)
            role_team = discord.utils.get(member.guild.roles, name=f"Team {team}")
            await member.add_roles(role_team)
            await logs.send(f"<a:BlobEnter:868589633544527952>┃**{member}** rejoined the server.")
        else:
            randomTeam = random.randint(1,5)
            role_team = discord.utils.get(member.guild.roles, name=f"Team {randomTeam}")
            await member.add_roles(role_team)
            cursor.execute(f"UPDATE main SET team = {randomTeam} WHERE id = {member.id}")
            await logs.send(f"<a:BlobEnter:868589633544527952>┃**{member}** joined the server.")
            
        role_trust = discord.utils.get(member.guild.roles, name="Level 1 Trust")
        await member.add_roles(role_trust)
        db.commit()

@bot.event
async def on_member_remove(member):
    if member.guild.id == 1109586411058901152:
        logs = bot.get_channel(1109590623012524063)
        await logs.send(f"<a:A_BlobLeave:868589633448067082>┃**{member.display_name}** left the server.")

@bot.event
async def on_command_error(ctx, error):
    spam = utils.spam_check(ctx)
    if spam >= 5:
        if spam == 5:
            await ctx.reply("You're being error limited.")
        return
    if isinstance(error, commands.CommandOnCooldown):
            msg = await ctx.reply(utils.cooldown_help(ctx, int(error.retry_after)))
            await asyncio.sleep(int(error.retry_after))
            await msg.delete()
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.reply("That command wasn't found!")
    elif isinstance(error, commands.BadArgument) or isinstance(error, commands.UserInputError):
        await ctx.reply("<:Error:957349442514718800>┃You inputed the command incorrectly!")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("<:Error:957349442514718800>┃You're missing argument(s)!")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.NoPrivateMessaget):
        await ctx.reply("<:Error:957349442514718800>┃I can't message you!")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.reply("<:Error:957349442514718800>┃The command failed to run.")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MaxConcurrencyReached):
        await ctx.reply("<:Error:957349442514718800>┃Concurrency error.")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MemberNotFound) or isinstance(error, commands.UserNotFound):
        await ctx.reply("<:Error:957349442514718800>┃That member cannot be found.")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply("<:Error:957349442514718800>┃I don't have the correct permissions.")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("<:Error:957349442514718800>┃You don't have the correct permissions to use this command.")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.NSFWChannelRequired):
        await ctx.reply("<:Error:957349442514718800>┃This command can only be triggered inside nsfw channels.")
        ctx.command.reset_cooldown(ctx)
    else:
        await ctx.reply("An unknown error happened. Please report this.")

#---------------#
# MAIN COMMANDS #
#---------------#

@bot.command(name="team")
@commands.cooldown(1, 10, commands.BucketType.user)
async def team_command(ctx, team:int):
    logs = bot.get_channel(1109590623012524063)
    if not await utils.generalCheck(bot, ctx):
        return
    if team > 5 or team < 1:
        await ctx.reply("Not a team!")
        return
    with sqlite3.connect('main.sqlite') as cursor:
        lastTeam = utils.get_user_team(ctx.author)
        roleList = [r.id for r in ctx.author.roles if r != ctx.guild.default_role]
        if lastTeam == 0:
            role = discord.utils.get(ctx.author.guild.roles, name=f"Team {team}")
            await ctx.author.add_roles(role)
            cursor.execute(f"UPDATE main SET team = {team} WHERE id = {ctx.author.id}")
            await ctx.reply(f"You're now in **Team {team}**!")
            await logs.send(f":mechanic:┃**{ctx.author}** joined **Team {team}**")
        else:
            role = discord.utils.get(ctx.author.guild.roles, name=f"Team {lastTeam}")
            if role.id in roleList:
                await ctx.reply("<:Error:957349442514718800>┃You're already in a team!")
    cursor.close()

@bot.command(name="roll")
@commands.cooldown(1, 30, commands.BucketType.user)
async def roll_command(ctx):
    alert = bot.get_channel(1109591422631415948)
    if not await utils.generalCheck(bot, ctx):
        return
    with sqlite3.connect('main.sqlite') as cursor:
        team = utils.get_user_team(ctx.author)
        cursor.execute(f"SELECT team{team}random FROM teams")
        add = cursor.fetchone()[0]
        randN = random.randint(0, 200000 + add)
        if randN == 1:
            cursor.execute(f"SELECT team{team}code FROM teams")
            code = cursor.fetchone()[0]
            cursor.execute(f"UPDATE teams SET team{team}code = {code + 1}")
            await ctx.reply(utils.darkness_text(ctx.author, f"<:U_Star:1003776660002320404>**YOU GOT IT**<:U_Star:1003776660002320404>\n**{ctx.author.name}** earned their team one character to the code!"))
            await alert.send(f"**{ctx.author.name}** earned their team one character to the code!")
        else:
            await ctx.reply(utils.darkness_text(ctx.author, "Nothing happened."))
    cursor.close()
    
@bot.command(name="daily")
async def daily_command(ctx):
    if not await utils.generalCheck(bot, ctx):
        return
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    time_left = utils.time_check(ctx.author, "daily_cooldown", "main")
    if time_left < 1:
        streak = utils.get_user_streak(ctx.author)
        if time_left < -86400:
            cursor.execute(f"UPDATE main SET daily_streak = 1 WHERE id = {ctx.author.id}")
        else:
            cursor.execute(f"UPDATE main SET daily_streak = {streak + 1} WHERE id = {ctx.author.id}")
        db.commit()
        utils.add_time(ctx.author, "daily_cooldown", 1, "days", db, cursor)
        utils.badgeUpdate(ctx.author, "daily", 1)
        streak = utils.get_user_streak(ctx.author)
        dis_streak = utils.darkness_text(ctx.author, streak)
        points = utils.get_user_points(ctx.author)
        utils.badgeUpdate(ctx.author, "points", streak)
        cursor.execute(f"UPDATE main SET points = {streak + points} WHERE id = {ctx.author.id}")
        db.commit()
        await ctx.reply(f":white_check_mark:┃You claimed your daily and got: <:Booster:868199875509092422>**{dis_streak}**! You're on a streak of **{dis_streak}**")
    else:
        await ctx.reply((utils.cooldown_help(ctx, time_left)))
    cursor.close(); db.close()

@bot.command(name='fetch')
@commands.cooldown(1, 10, commands.BucketType.user)
async def fetch_command(ctx, top:int):
    if not await utils.generalCheck(bot, ctx):
        return
    if type(top) is not int:
        await ctx.reply("<:Error:957349442514718800>┃Top must be an integer!")
    if top > 25:
        await ctx.reply("<:Error:957349442514718800>┃Top can't be more than 25!")
    if top < 1:
        await ctx.reply("<:Error:957349442514718800>┃Top can't be less than 1!")
    await ctx.reply(utils.get_final_team(bot, top))

@bot.command(aliases=["lb", "leaderboard"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def leaderboard_command(ctx, category, top=10):
    if not await utils.generalCheck(bot, ctx):
        return
    await ctx.channel.typing()
    if top < 1:
        await ctx.reply("<:Error:957349442514718800>┃Top can't be lower than 1!")
        return
    elif top > 25:
        await ctx.reply("<:Error:957349442514718800>┃Top can't be larger than 25!")
        return
    elif category not in list(utils.lookup.keys()):
        await ctx.reply(f"<:Error:957349442514718800>┃**{category}** is not a valid category!")
        return
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    
    cursor.execute(f"SELECT {utils.lookup[category]}, id FROM main")
    look = cursor.fetchall()

    look.sort(key=tuple, reverse=True)
    look = look[:top]
    users = [await bot.fetch_user(u[1]) for u in look if await bot.fetch_user(u[1]) != None]
    amounts = ['{:,}'.format(a[0]) for a in look]
    display = "".join([f"{count + 1}. **{user.display_name}**: __{amount}__\n" for user, amount, count in zip(users, amounts, range(top))])
    embed = utils.embed_help(ctx.author, f"{category.title()} Leaderboard", display, discord.Colour.yellow(), author=True, timestamp=True)
    cursor.close(); db.close()
    
    await ctx.reply(embed=embed)

@bot.command(name="check")
async def check_command(ctx, id):
    if not await utils.generalCheck(bot, ctx):
        return
    
    if id[:2] == "bg":
        pro = id[2:4].upper()
        background = utils.Backgrounds(pro, ctx.author)
        embed = utils.embed_help(ctx.author, f"**{background.name}**", image=background.link if background.link not in ["Error", None] else None)
        await ctx.send(embed=embed)
    elif id[:2] == "ad":
        pro = id[2:].upper()
        gear = utils.Gear(pro, ctx.author)
        embed = utils.embed_help(ctx.author, f"**{gear.name}**", image=gear.link if gear.link not in ["Error", None] else None)
        await ctx.send(embed=embed)
    elif id[:4] == "font":
        pro = id[4:].upper()
        font = utils.Fonts(pro, ctx.author)
        embed = utils.embed_help(ctx.author, f"**{font.name}**", image=font.link if font.link not in ["Error", None] else None)
        await ctx.send(embed=embed)
    elif id[:3] == "col":
        pro = id[4:].upper()
        color = utils.Colors(pro, ctx.author)
        embed = utils.embed_help(ctx.author, f"**{color.name}**", image=color.link if color.link not in ["Error", None] else None)
        await ctx.send(embed=embed)
    else:
        await ctx.send("<:Error:957349442514718800>┃I can't check that item.")

@bot.command()
async def test(ctx, user:discord.Member):
    said = await utils.response(ctx.channel, ctx.author, bot, 30)
    if said == "timeout":
        # handle timeout here
        pass
    else:
        said = said.content.lower()
        if said == "penis":
            # Do things here!
            pass
        elif said == "hello":
            # Do more things here!
            pass
        else:
            # Do more things things here!
            pass

asyncio.run(main())