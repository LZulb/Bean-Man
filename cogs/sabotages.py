import discord
import utils, game_utils
import sqlite3, datetime, asyncio, random
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from datetime import datetime, timedelta

locked = False

class SabotageCog(commands.Cog, name="Sabotage"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sab")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sabotage_command(self, ctx, team_number:int=None, sab:str=None):
        if ctx.author.id != 683886490211713176:
            if not await utils.generalCheck(self.bot, ctx):
                return
            if locked:
                await ctx.send("This command is currently locked!")
                return
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        if locked:
            await ctx.send("This command is currently locked!")
            return
        if sab is None:
            embed = utils.embed_help(ctx.author, f":smiling_imp:┃**Team {team_number}**'s Sabotages", color=discord.Colour.blurple(), author=True, timestamp=True)
            for n in range(5):
                if n == 4:
                    cursor.execute(f"SELECT team{team_number}random FROM teams")
                    odds = cursor.fetchone()[0]
                    if odds == 0:
                        maths = 0
                    else:
                        maths = round((odds / 200000) * 100, 3)
                    embed.add_field(name=utils.sabotage_list[n].title(), value=f"{maths}%")
                else:
                    utils.sab_time_check(ctx.author, team_number, utils.sabotage_list[n])
                    time_left = utils.time_check(ctx.author, f"team{team_number}{utils.sabotage_list[n]}", "teams")
                    embed.add_field(name=utils.sabotage_list[n].title(), value=utils.cooldown_help(ctx, time_left, True))
            await ctx.send(embed=embed)
            return
        cursor.execute(f"SELECT {sab} FROM main WHERE id = {ctx.author.id}")
        sab_thing = cursor.fetchone()[0]
        team = utils.get_user_team(ctx.author)
        sab = sab.lower()
        if sab_thing < 1:
            await ctx.send(f"<:Error:957349442514718800>┃You don't have a **{sab.title()}** sabotage!")
            return
        elif team_number < 1 or team_number > 5:
            await ctx.send("<:Error:957349442514718800>┃Choose a valid team!")
            return
        elif team == team_number:
            await ctx.send("<:Error:957349442514718800>┃You can't sabotage your own team!")
            return
        else:
            logs = self.bot.get_channel(1109590623012524063)
            if sab != "random":
                try:
                    tomorrow = timedelta(hours=1)
                    now = datetime.now().replace(microsecond=0)
                    then = now + tomorrow
                    utils.badgeUpdate(ctx.author, "sab", 1)
                    utils.main_database_update([ctx.author.id],[sab],[1],["sub"])
                    cursor.execute(f"UPDATE teams SET team{team_number}{sab} = '{then}'")
                    db.commit()
                    await ctx.send(f":white_check_mark:┃**{ctx.author.display_name}** sabotaged **Team {team_number}** with the **{sab.title()}** effect!")
                    await logs.send(f":smiling_imp:┃**{ctx.author}** sabotaged **Team {team_number}** with the **{sab.title()}** effect.")
                except:
                    await ctx.send("<:Error:957349442514718800>┃Not a valid type of sabotage.")
            else:
                cursor.execute(f"SELECT team{team_number}random FROM teams")
                random_count = cursor.fetchone()[0]
                utils.badgeUpdate(ctx.author, "sab", 1)
                utils.main_database_update([ctx.author.id],[sab],[1],["sub"])
                cursor.execute(f"UPDATE teams SET team{team_number}random = {random_count + 10}")
                db.commit()
                await ctx.send(f":white_check_mark:┃**{ctx.author.display_name}** sabotaged **Team {team_number}** with the **{sab.title()}** curse!")
                await logs.send(f":smiling_imp:┃**{ctx.author.display_name}** sabotaged **Team {team_number}** with the **{sab.title()}** curse.")

    @sabotage_command.error
    async def on_sabotage_command_error(self, ctx, error):
        spam = utils.spam_check(ctx)
        if spam >= 5:
            if spam == 5:
                await ctx.send("You're being error limited.")
            return
        if isinstance(error, commands.CommandOnCooldown):
            msg = await ctx.send(utils.cooldown_help(ctx, int(error.retry_after)))
            await asyncio.sleep(int(error.retry_after))
            await msg.delete()
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.UserInputError):
            await ctx.send("<:Error:957349442514718800>┃You inputed the command incorrectly! Use `b!help sab` to learn how to use the command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("<:Error:957349442514718800>┃You're missing argument(s)! Use `b!help sab` to learn how to use the command!")
        else:
            await ctx.send("An unknown error happened. Please try again!")

async def setup(bot):
    await bot.add_cog(SabotageCog(bot))
    print("Sabotages loaded")