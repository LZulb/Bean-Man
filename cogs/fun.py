import discord
import utils, game_utils
import sqlite3, datetime, asyncio, random, re
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from datetime import datetime, timedelta
from easy_pil import Editor, Canvas, load_image_async, Font

class FunCog(commands.Cog, name="Fun"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cooldown")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cooldown_command(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        daily = utils.cooldown_help(ctx, utils.time_check(ctx.author, 'daily_cooldown', 'main'), True)
        memory = utils.cooldown_help(ctx, utils.time_check(ctx.author, 'memory_cooldown', 'main'), True)
        rep = utils.cooldown_help(ctx, utils.time_check(ctx.author, 'rep_cooldown', 'main'), True)
        cake = utils.cooldown_help(ctx, utils.time_check(ctx.author, 'cake_cooldown', 'main'), True)
        display = f"Daily Command: **{daily}**\nMemory Command: **{memory}**\nRep Command: **{rep}**\nCake Command: **{cake}**"
        embed = utils.embed_help(ctx.author, "Cooldowns", display, discord.Colour.greyple(), True, True)
        await ctx.reply(embed=embed)

    @commands.command(name="profile")
    async def profile_command(self, ctx, user:discord.Member=None):
        if not await utils.generalCheck(self.bot, ctx):
            return
    
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
    
        if user is None:
            user = ctx.author
    
        cursor.execute(f"SELECT background, aboutme, border_color, aboutme_color, aboutme_background_color, name_color, font, badge_1, badge_2, pfp_gear FROM profiles WHERE id = {user.id}")
        grab = cursor.fetchall()[0]
        cursor.close(); db.close()
        
        bg = grab[0]
        aboutMe = grab[1]
        border = utils.Colors(grab[2]).hex
        aboutMeColor = utils.Colors(grab[3]).hex
        aboutMeBgColor = grab[4]
        nameColor = utils.Colors(grab[5]).hex
        font = grab[6]
        badge1 = grab[7]
        badge2 = grab[8]
        gear = grab[9]
        rep = utils.get_user_rep(user)

        background = Editor(f"Backgrounds/Background{bg}.png")
        blank = Editor("Backgrounds/blank.png")
        userFont = Font(f"Fonts/Font{font}/Regular.ttf", 40)
        aboutFont = Font(f"Fonts/Font{font}/Regular.ttf", 30)
        
        # Profile Picture Works
        profile = await load_image_async(str(user.avatar.url))
        pfp = Editor(profile).resize((110, 110)).circle_image()
        if gear != "0":
            add = Editor(f"AddOns/Extra{gear}.png").resize((110, 110))

        background.paste(pfp, (65, 35))
        if gear != "0":
            background.paste(add, (65, 35))

        name_bg = Editor(f"Backgrounds/Background{aboutMeBgColor}.png").resize((utils.textLen(user.display_name), 65))
        name_bg.rounded_corners(radius=23)
        name_bg.blend(image=blank, alpha=.50)
        background.paste(name_bg, (182, 56))
        background.text((205, 74), user.display_name, font=userFont, color=nameColor, stroke_fill="black")
        
        rep_beg = Editor(f"Backgrounds/Background{aboutMeBgColor}.png").resize((len(f"Rep: {rep}") * 28, 65))
        rep_beg.rounded_corners(radius=23)
        rep_beg.blend(image=blank, alpha=.50)
        background.paste(rep_beg, (660, 56))
        background.text((680, 74), f"Rep: {rep}", font=userFont, color=nameColor, stroke_fill="black")

        # badges
        if badge1 != 0:
            a = Editor(f"Badges/Badge{badge1}.png")
            badge = Editor(a).resize((60, 60))
            background.paste(badge, (75, 175))
            
        if badge1 != 0:
            b = Editor(f"Badges/Badge{badge2}.png")
            badge = Editor(b).resize((60, 60))
            background.paste(badge, (165, 175))
        
        # Border
        
        background.rectangle((0, 0), width=900, height=5, color=border, radius=0, stroke_width=5)
        background.rectangle((0, 395), width=900, height=5, color=border, radius=0, stroke_width=5)
        background.rectangle((0, 0), width=5, height=400, color=border, radius=0, stroke_width=5)
        background.rectangle((895, 0), width=5, height=400, color=border, radius=0, stroke_width=5)
        
        # About Me
        abtlen = len(aboutMe)

        if abtlen > 0:
        
            if abtlen > 100:
                am_bg = Editor(f"Backgrounds/Background{aboutMeBgColor}.png").resize((800, 125))
                am_bg.rounded_corners(radius=23)
                am_bg.blend(image=blank, alpha=.50)
                background.paste(am_bg, (50, 250))
            elif abtlen > 50:
                am_bg = Editor(f"Backgrounds/Background{aboutMeBgColor}.png").resize((800, 100))
                am_bg.rounded_corners(radius=23)
                am_bg.blend(image=blank, alpha=.50)
                background.paste(am_bg, (50, 250))
            else:
                am_bg = Editor(f"Backgrounds/Background{aboutMeBgColor}.png").resize((800, 75))
                am_bg.rounded_corners(radius=23)
                am_bg.blend(image=blank, alpha=.50)
                background.paste(am_bg, (50, 250))
            
            for n in range(3):
                if abtlen > 50:
                    background.text((450, 275 + n * 27), f"{aboutMe[n*50:n*50+50]}-", font=aboutFont, color=aboutMeColor, align="center")
                    abtlen -= 50
                else:
                    background.text((450, 275 + n * 27), aboutMe[n*50:100+abtlen], font=aboutFont, color=aboutMeColor, align="center")
                    break
    
        file = discord.File(fp=background.image_bytes, filename="Profile.png")
        await ctx.reply(file=file)

    @commands.command(name="equip")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def equip_command(self, ctx, item:str, slot:int=None):
        if not await utils.generalCheck(self.bot, ctx):
            return
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        try:
            if item[:2] == "bg":
                pro = item[2:4].upper()
                background = utils.Backgrounds(pro, ctx.author)
                have = background.have

                if have == "Error":
                    await ctx.reply("<:Error:957349442514718800>┃You entered an invalid ID!")
                    return
                if pro not in have:
                    await ctx.reply("<:Error:957349442514718800>┃You don't own this!")
                    return
    
                cursor.execute(f"UPDATE profiles SET background = '{pro}' WHERE id = {ctx.author.id}")
                db.commit()
                await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃You equipped a **{background.name}** background!")
            elif item[:2] == "ad":
                pro = item[2:].upper()
                gear = utils.Gear(pro, ctx.author)
                have = gear.have

                if have == "Error":
                    await ctx.reply("<:Error:957349442514718800>┃You entered an invalid ID!")
                    return
                if pro not in have:
                    await ctx.reply("<:Error:957349442514718800>┃You don't own this!")
                    return
    
                cursor.execute(f"UPDATE profiles SET pfp_gear = '{pro}' WHERE id = {ctx.author.id}")
                db.commit()
                await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃You equipped **{gear.name}** gear!")
            elif item[:4] == "font":
                pro = item[4:].upper()
                font = utils.Fonts(pro, ctx.author)
                have = font.have

                if have == "Error":
                    await ctx.reply("<:Error:957349442514718800>┃You entered an invalid ID!")
                    return
                if pro not in have:
                    await ctx.reply("<:Error:957349442514718800>┃You don't own this!")
                    return
    
                cursor.execute(f"UPDATE profiles SET font = '{pro}' WHERE id = {ctx.author.id}")
                db.commit()
                await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃You equipped **{font.name}**!")
            elif item[:5] == "badge":
                if slot is None:
                    await ctx.reply("You must provide a slot! (`b!equip badge1 1` or `b!equip badge1 2`)")
                    return
                pro = int(item[5:])
                if pro == 0:
                    cursor.execute(f"UPDATE profiles SET badge_{slot} = {pro} WHERE id = {ctx.author.id}")
                    db.commit()
                    await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃You removed your badge in slot **{slot}**!")
                    return
                have = cursor.execute(f"SELECT secret_{utils.secret_badges[slot]} FROM main WHERE id = {ctx.author.id}")
                if have == 0:
                    await ctx.reply("<:Error:957349442514718800>┃You don't own this badge!")
                    return
    
                cursor.execute(f"UPDATE profiles SET badge_{slot} = {pro} WHERE id = {ctx.author.id}")
                db.commit()
                await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃You equipped a **Badge** in slot **{slot}**!")
            else:
                await ctx.reply("<:Error:957349442514718800>┃I don't recognize that item.")
        finally:
            cursor.close(); db.close()

    @commands.command(aliases=["aboutme", 'am'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def aboutme_command(self, ctx, *, msg=""):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if len(msg) > 150:
            await ctx.reply("<:Error:957349442514718800>┃Your about me has to less than 150 characters.")
            return
        if len(re.findall("f[4a]g+([o0]t)", msg)) > 0 or len(re.findall("n[i1!]gg+[e3]r", msg)) > 0 or len(re.findall("n[i1!]gg+[a4]", msg)) > 0:
            await ctx.reply("<:Error:957349442514718800>┃Don't say slurs :(")
            return
        msg = re.sub('"', '“', msg)
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f'UPDATE profiles SET aboutme = "{msg}" WHERE id = {ctx.author.id}')
        db.commit()
        cursor.close(); db.close()
        await ctx.reply("<:V_GreenVerify:868218741765316638>┃Your about me has been updated!")

    @commands.command(aliases=["color", "col"])
    async def color_command(self, ctx, obj, col):
        if not await utils.generalCheck(self.bot, ctx):
            return
        pro = col[3:].upper()
        color = utils.Colors(pro, ctx.author)
        have = color.have

        if color.name in ["Error", None]:
            await ctx.reply("<:Error:957349442514718800>┃You entered an invalid ID!")
            return
        if pro not in have:
            await ctx.reply(f"<:Error:957349442514718800>┃You don't own {color.name}!")
            return
        try:
            with sqlite3.connect('main.sqlite') as cursor:
                if obj == "name":
                    cursor.execute(f"UPDATE profiles SET name_color = '{pro}' WHERE id = {ctx.author.id}")
                    await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃Your name color was updated to **{color.name}**!")
                elif obj == "border":
                    cursor.execute(f"UPDATE profiles SET border_color = '{pro}' WHERE id = {ctx.author.id}")
                    await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃Your profile border was updated to **{color.name}**!")
                elif obj in ["am", "aboutme"]:
                    cursor.execute(f"UPDATE profiles SET aboutme_color = '{pro}' WHERE id = {ctx.author.id}")
                    await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃Your about me text was updated to **{color.name}**!")
                elif obj in ["bg", "background"]:
                    cursor.execute(f"UPDATE profiles SET aboutme_background_color = '{pro}' WHERE id = {ctx.author.id}")
                    await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃Your about me background color was updated to **{color.name}**!")
                else:
                    await ctx.reply("<:Error:957349442514718800>┃The didn't provide the correct category.")
        finally:
            cursor.close()

    @commands.command(aliases=["badges", "badge"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def badge_command(self, ctx, user:discord.Member=None):
        if not await utils.generalCheck(self.bot, ctx):
            return
                
        if user is None:
            user = ctx.author
            
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        secret_msg = ""
        
        secrets = ["bean_crew", "gamer", "nerd", "beans", "santa", "nice_lad", "funny_lad", "rep", "rps", "hm", "cake", "profile"]
        for secret, count in zip(secrets, range(len(secrets))):
            cursor.execute(f"SELECT secret_{secret} FROM main WHERE id = {ctx.author.id}")
            has_secret = cursor.fetchone()[0]
            add_to = "???"
            if has_secret == 1:
                add_to = secret.replace("_", " ")
                add_to = add_to.title()
            if secret == secrets[-1]:
                secret_msg += f"- `badge{count + 1}`┃**{add_to}**"
            else:
                secret_msg += f"- `badge{count + 1}`┃**{add_to}**\n"
        cursor.close(); db.close()
        
        page1 = embed = utils.embed_help(user, title=f"{user.display_name}'s Badges", color=discord.Colour.yellow(), author=True, timestamp=True)
        embed.add_field(name="Badges", value=f"{utils.badgeCreation(ctx)}")
        embed.set_footer(text="page 1/2")
        
        page2 = embed = utils.embed_help(user, title=f"{user.display_name}'s Badges", color=discord.Colour.yellow(), author=True, timestamp=True)
        embed.add_field(name="Secret Badges", value=secret_msg)
        embed.set_footer(text="page 2/2")
        
        badge_pages = [page1, page2]
        buttons = ["◀", "▶"]
        current = 0
        msg = await ctx.reply(embed=badge_pages[current])
        
        for button in buttons:
          await msg.add_reaction(button)
          
        while True:
            try:
              reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message.id == msg.id and reaction.emoji in buttons, timeout=25)
            
            except asyncio.TimeoutError:
                embed = badge_pages[current]
                embed.set_footer(text="Timeout")
                await msg.clear_reactions()
                return
            else:
                previous_pages = current
        
                if reaction.emoji == "◀":
                    if current > 0:
                        current -= 1
            
                elif reaction.emoji == "▶":
                    if current < len(badge_pages) - 1:
                        current += 1
                
                for button in buttons:
                    await msg.remove_reaction(button, ctx.author)
        
                if current != previous_pages:
                    await msg.edit(embed=badge_pages[current])

    @commands.command(name="role")
    async def role_command(self, ctx, col):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if col[:3] == "col":
            pro = col[3:5]
            color = utils.Colors(pro, ctx.author)
            have = color.have
            
            if pro not in have:
                await ctx.reply("<:Error:957349442514718800>┃You don't own this color!")
                return
    
            roleList = [r.id for r in ctx.author.roles if r != ctx.message.guild.default_role]
            allRoles = color.roles
            for i in allRoles:
                if i in roleList:
                    role_take = discord.utils.get(ctx.author.guild.roles, id=i)
                    await ctx.author.remove_roles(role_take)
                    break
            role_give = discord.utils.get(ctx.author.guild.roles, id=color.role)
            await ctx.author.add_roles(role_give)
            await ctx.reply("<:V_GreenVerify:868218741765316638>┃You equipped a colored role!")
        elif col[:3] == "top":
            coins = utils.get_user_coins(ctx.author)
            roleList = [r.id for r in ctx.author.roles if r != ctx.message.guild.default_role]
            
            if coins < 10_000:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{10_000 - coins}**!")
                return
            if 1124391688073388222 in roleList:
                await ctx.reply("<:Error:957349442514718800>┃You're already displaying to the top!")
                return
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - 10_000} WHERE id = {ctx.author.id}")
            cursor.close()
            top = discord.utils.get(ctx.author.guild.roles, id=1124391688073388222)
            await ctx.author.add_roles(top)
            await ctx.reply("<:V_GreenVerify:868218741765316638>┃You're now displaying at the top of the leaderboard!")
        else:
            await ctx.reply("<:Error:957349442514718800>┃Not a valid role type!")

    @commands.command(name="cake")
    async def cake_command(self, ctx, user:discord.Member=None):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if user is None:
            embed = utils.embed_help(ctx.author, f"**{ctx.author.display_name}**'s Cake", f"<:BeanCakeRegular:1128760753151823902>┃**{utils.get_user_cake(ctx.author)}**", author=True, timestamp=True)
            await ctx.reply(embed=embed)
        if user.id == ctx.author.id:
            await ctx.reply("<:Error:957349442514718800>┃You can't cake yourself!")
            return
        else:
            if utils.get_user_cake(ctx.author) < 1:
                await ctx.reply("<:Error:957349442514718800>┃You need cake to start giving cake!")
                return
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            time_left = utils.time_check(ctx.author, "cake_cooldown", "main")
            if time_left < 1:
                utils.add_time(ctx.author, "cake_cooldown", 1, "days", db, cursor)
                cursor.execute(f"UPDATE main SET cake = {utils.get_user_rep(user) + 1} WHERE id = {user.id}")
                db.commit()
                await ctx.reply(f"<:BeanCakeRegular:1128760753151823902>┃**{user.display_name}** gained +1 cake!")
                if utils.get_user_cake(user) == 25:
                    await utils.secret_add(1132357098940940389, "Birthy", user, ctx.message, "cake")
                cursor.close(); db.close()
            else:
                await ctx.reply((utils.cooldown_help(ctx, time_left)))
            cursor.close(); db.close()

    @commands.command(name="rep")
    async def rep_command(self, ctx, user:discord.Member=None):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if user is None:
            embed = utils.embed_help(ctx.author, f"**{ctx.author.display_name}**'s Rep", f"<:V_GreenVerify:868218741765316638>┃**{utils.get_user_rep(ctx.author)}**", author=True, timestamp=True)
            await ctx.reply(embed=embed)
        if user.id == ctx.author.id:
            await ctx.reply("<:Error:957349442514718800>┃You can't rep yourself!")
            return
        else:
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            time_left = utils.time_check(ctx.author, "rep_cooldown", "main")
            if time_left < 1:
                utils.add_time(ctx.author, "rep_cooldown", 1, "days", db, cursor)
                cursor.execute(f"UPDATE main SET rep = {utils.get_user_rep(user) + 1} WHERE id = {user.id}")
                db.commit()
                await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃**{user.display_name}** gained +1 rep!")
                if utils.get_user_rep(user) == 25:
                    await utils.secret_add(1132357088346128535, "Popular", user, ctx.message, "rep")
                cursor.close(); db.close()
            else:
                await ctx.reply((utils.cooldown_help(ctx, time_left)))
            cursor.close(); db.close()

async def setup(bot):
    await bot.add_cog(FunCog(bot))
    print("Fun loaded")