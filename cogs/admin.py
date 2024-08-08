import discord
import utils, game_utils
import sqlite3, datetime, asyncio, random
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from datetime import datetime, timedelta

class AdminCog(commands.Cog, name="Admin"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="force")
    async def force_admin(self, ctx, user:discord.Member, team:int):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE main SET team = {team} WHERE id = {user.id}")
            db.commit()
            await ctx.reply(f"**{user.display_name}**'s team has been changed to **Team {team}**!")
            await logs.send(f":plunger:┃**{ctx.author.display_name}** forced **{user.display_name}** to be on **Team {team}**.")
        else:
            return
    
    @commands.command(name="ban")
    async def ban_admin(self, ctx, user:discord.Member, state:str):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            if state not in ["True", "False"]:
                await ctx.reply("Not True or False.")
                return
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"UPDATE main SET ban = '{state}' WHERE id = {user.id}")
            db.commit()
            await ctx.reply(f"<:BanHammer_:957349442573467708>┃**{user.display_name}**'s ban state has been updated.")
            await logs.send(f"<:BanHammer_:957349442573467708>┃**{ctx.author.display_name}** updated **{user.display_name}**'s ban state to **{state}**.")
        else:
            return
    
    @commands.command(name="let")
    async def let_admin(self, ctx, user:discord.Member, table:str, value:str, set, type:str=None):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            if type == "string":
                cursor.execute(f"UPDATE {table} SET {value} = '{set}' WHERE id = {user.id}")
            else:
                cursor.execute(f"UPDATE {table} SET {value} = {set} WHERE id = {user.id}")
            db.commit()
            await ctx.reply("Let it be!")
            await logs.send(f":triangular_ruler:┃**{ctx.author.display_name}**: {user} : {table} : {value} : {set} : {type}.")
        else:
            return
    
    @commands.command(name='magic')
    async def magic_admin(self, ctx, member:discord.Member, amount:int):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            points = utils.get_user_points(member)
            cursor.execute(f"UPDATE main SET points = {points + amount} WHERE id = {member.id}")
            db.commit()
            await ctx.reply(":magic_wand:┃Almost like magic!")
            await logs.send(f":magic_wand:┃**{ctx.author.display_name}** used magic to give **{member.display_name} {amount}** points!")
        else:
            return
    
    @commands.command(name="clean")
    async def clean_admin(self, ctx):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            utils.cleanDatabase(self.bot)
            await ctx.reply("Database has been cleaned!")
            await logs.send(f":broom:┃**{ctx.author.display_name}** cleaned the database.")
        else:
            return
    
    @commands.command(name="delete")
    async def delete_admin(self, ctx, user:discord.Member):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM main WHERE id = {user.id}")
            db.commit()
            await ctx.reply(f"**{user.display_name}** has been deleted from the database!")
            await logs.send(f"<:Trash:868199875261636680>┃**{ctx.authorname}** deleted **{user.display_name}** from the database.")
        else:
            return
    
    @commands.command(name="create")
    async def create_admin(self, ctx, user:discord.Member):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            utils.db_make(user)
            await ctx.reply(f"A database entry for **{user.display_name}** has been made!")
            await logs.send(f":page_facing_up:┃**{ctx.author.display_name}** created a database entry for **{user.display_name}**.")
        else:
            return

    @commands.command(aliases=["c", "clear"])
    @commands.has_permissions(manage_messages=True)
    async def clear_admin(self, ctx, amount:int=1):
        if amount > 25:
            await ctx.reply("<:Error:957349442514718800>┃Keep purge under 25 or lower.")
            return
        if amount < 1:
            await ctx.reply("<:Error:957349442514718800>┃Now you're just being silly.")
            return
        logs = self.bot.get_channel(1109590623012524063)
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await logs.send(f"<:Trash:868199875261636680>┃**{ctx.author.display_name}** purged {amount} messages inside **{ctx.channel}**")

    @commands.command(name="THEGREATRESET")
    async def reset_admin(self, ctx):
        if ctx.author.id in [683886490211713176, 502183735484088340]:
            logs = self.bot.get_channel(1109590623012524063)
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            cursor.execute("UPDATE main SET points = 0")
            
            cursor.execute("UPDATE main SET darkness = 0")
            cursor.execute("UPDATE main SET imposter = 0")
            cursor.execute("UPDATE main SET hunger = 0")
            cursor.execute("UPDATE main SET butter = 0")
            cursor.execute("UPDATE main SET random = 0")
            
            cursor.execute("UPDATE main SET beans = 0")
            cursor.execute("UPDATE main SET daily_streak = 0")

            cursor.execute("UPDATE teams SET team1random = 0")
            cursor.execute("UPDATE teams SET team2random = 0")
            cursor.execute("UPDATE teams SET team3random = 0")
            cursor.execute("UPDATE teams SET team4random = 0")
            cursor.execute("UPDATE teams SET team5random = 0")

            cursor.execute("UPDATE teams SET team1code = 0")
            cursor.execute("UPDATE teams SET team2code = 0")
            cursor.execute("UPDATE teams SET team3code = 0")
            cursor.execute("UPDATE teams SET team4code = 0")
            cursor.execute("UPDATE teams SET team5code = 0")

            cursor.execute("UPDATE teams SET nitro = 2")
            
            db.commit()
            await ctx.reply("It has been done.")
            await logs.send(f":page_facing_up:┃**{ctx.author.display_name}** caused THE GREAT RESET.")
        else:
            return

    @commands.command(name="sb")
    @commands.has_permissions(ban_members = True)
    async def server_ban_admin(self, ctx, user:discord.Member, reason:str="None provided."):
        await user.ban(reason = reason)
        await ctx.send("Banned.")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
    print("Admin loaded")