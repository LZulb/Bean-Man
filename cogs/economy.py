import discord
import utils, game_utils
import sqlite3, datetime, asyncio, random, re
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord import app_commands
from datetime import datetime, timedelta

class EconomyCog(commands.Cog, name="Economy"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="beg")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def beg_command(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
        randN = random.randint(0, 100)
        if randN < 46:
            utils.badgeUpdate(ctx.author, "points", 7)
            utils.main_database_update([ctx.author.id],["points"],[7],["add"])
            await ctx.reply(f":star:┃You got <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, 7)}**!")
        elif randN > 45 and randN < 51:
            utils.badgeUpdate(ctx.author, "points", 13)
            utils.main_database_update([ctx.author.id],["points"],[13],["add"])
            await ctx.reply(f":star2:┃You got <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, 13)}**!")
        elif randN == 52:
            utils.badgeUpdate(ctx.author, "points", 35)
            utils.main_database_update([ctx.author.id],["points"],[35],["add"])
            await ctx.reply(f":star_struck:┃You got <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, 35)}**!")
        else:
            coinAmt = random.randint(47, 113)
            utils.main_database_update([ctx.author.id],["coins"],[coinAmt],["add"])
            await ctx.reply(f":sparkles:┃You got :coin:**{utils.darkness_text(ctx.author, coinAmt)}**!")

    @commands.command(name="bet")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bet_command(self, ctx, amount:int=1):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
        randN = random.randint(0, 100)
        points = utils.get_user_points(ctx.author)
        
        if points < amount:
            await ctx.reply("<:Error:957349442514718800>┃You don't have enough points to bet!")
            return
        if amount < 1:
            await ctx.reply("<:Error:957349442514718800>┃Enter a valid amount.")
            return
        if amount > 50:
            await ctx.reply(f"<:Error:957349442514718800>┃Keep bets {utils.darkness_text(ctx.author, '50')} or lower!")
            return
            
        if randN < 51:
            fancy_math = int(amount * round(random.uniform(0.85, 1.15), 2))
            utils.badgeUpdate(ctx.author, "points", fancy_math)
            utils.main_database_update([ctx.author.id],["points"],[fancy_math],["add"])
            await ctx.reply(f"<:V_GreenVerify:868218741765316638>┃You got <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, fancy_math)}**!")
        else:
            points = utils.get_user_points(ctx.author)
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET points = {points - amount} WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":x:┃You lost <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, amount)}**!")

    @commands.command(aliases=['points', 'wallet', 'cash', 'money', "balance", "bal"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def points_command(self, ctx, user:discord.Member=None):
        if ctx.author.id != 683886490211713176:
            if not await utils.generalCheck(self.bot, ctx):
                return
        if user is None:
            user = ctx.author
            
        points = utils.get_user_points(user)
        coins = utils.get_user_coins(user)
        
        points = '{:,}'.format(points)
        coins = '{:,}'.format(coins)
        embed = utils.embed_help(user, f"**__{user.display_name}'s Wallet__**", f"<:Booster:868199875509092422>**{utils.darkness_text(user, points)}**\n:coin:**{utils.darkness_text(user, coins)}**", discord.Colour.green(), True, True)
        await ctx.reply(embed=embed)

    @commands.command(aliases=['shop', 'store'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def shop_command(self, ctx):
        if ctx.author.id not in [683886490211713176, 638476312658313222]:
            if not await utils.generalCheck(self.bot, ctx):
                return
        rod = utils.get_user_rod(ctx.author)
        if rod == 0:
            add = f"\n`rod`┃<:WoodRod:1130998787175895120> **Wooden Rod**┃:coin:**{utils.item_price('rod', user=ctx.author)}**"
        elif rod == 1:
            add = f"\n`rod`┃<:SilverRod:1130998788849414245> **Silver Rod**┃:coin:**{utils.item_price('rod', user=ctx.author)}**"
        elif rod == 2:
            add = f"\n`rod`┃<:GoldRod:1130998789902176256> **Golden Rod**┃:coin:**{utils.item_price('rod', user=ctx.author)}**"
        elif rod == 3:
            add = f"\n`rod`┃<:DiamondRod:1130998790917193739> **Diamond Rod**┃:coin:**{utils.item_price('rod', user=ctx.author)}**"
        else:
            add = ""
        page1 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name = "**:smiling_imp:┃Sabotages**", value = f"`butter`┃:butter: **Butter**┃<:Booster:868199875509092422>{utils.item_price('butter')}\n`darkness`┃:night_with_stars: **Darkness**┃<:Booster:868199875509092422>{utils.item_price('darkness')}\n`random`┃:game_die: **Random**┃<:Booster:868199875509092422>{utils.item_price('random')}\n`hunger`┃:canned_food: **Hunger**┃<:Booster:868199875509092422>{utils.item_price('hunger')}\n`imposter`┃:japanese_ogre: **Imposter**┃<:Booster:868199875509092422>{utils.item_price('imposter')}")
        embed.add_field(name = "**:cloud:┃Other**", value = f"`nitro`┃<:U_Nitro:1111426154851737670> **Nitro**┃<:Booster:868199875509092422>{utils.item_price('nitro')}\n`beans`┃:beans: **Beans**┃<:Booster:868199875509092422>{utils.item_price('beans')}\n`crate`┃<:Crate:1129920387178831972> **Crate**┃:coin:{utils.item_price('crate')}\n`dcrate`┃<:DiamondCrate:1129920579504455701> **Diamond Crate**┃:coin:{utils.item_price('diamond_crate')}\n`ticket`┃:tickets:**Ticket**┃<:Booster:868199875509092422>**{utils.item_price('ticket')}**{add}")
        embed.set_footer(text="page 1/7")

        page2 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name="Profile Backgrounds (1)", value="\n".join([f"`bg{n+1}`┃:frame_photo: [__**{utils.Backgrounds(n+1).name}**__]({utils.Backgrounds(n+1).link})┃:coin:**{utils.item_price(utils.Backgrounds(n+1).type)}**" for n in range(9)]))
        embed.add_field(name="Profile backgrounds (2)", value="\n".join([f"`bg{n+10}`┃:frame_photo: [__**{utils.Backgrounds(n+10).name}**__]({utils.Backgrounds(n+10).link})┃:coin:**{utils.item_price(utils.Backgrounds(n+10).type)}**" for n in range(9)]))
        embed.set_footer(text="page 2/7")
        
        page3 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name="Profile Backgrounds (3)", value="\n".join([f"`bg{n+19}`┃:frame_photo: [__**{utils.Backgrounds(n+19).name}**__]({utils.Backgrounds(n+19).link})┃:coin:**{utils.item_price(utils.Backgrounds(n+19).type)}**" for n in range(9)]))
        embed.add_field(name="Profile Backgrounds (4)", value="\n".join([f"`bg{n+28}`┃:frame_photo: [__**{utils.Backgrounds(n+28).name}**__]({utils.Backgrounds(n+28).link})┃:coin:**{utils.item_price(utils.Backgrounds(n+28).type)}**" for n in range(9)]))
        embed.set_footer(text="page 3/7")
        
        page4 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name="Avatar Decoration", value="\n".join([f"`ad{n+1}`┃:frame_photo: [__**{utils.Gear(n+1).name}**__]({utils.Gear(n+1).link})┃:coin:**{utils.item_price(utils.Gear(n+1).type)}**" for n in range(8)]))
        embed.set_footer(text="page 4/7")
        
        page5 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name="Colors (1)", value="\n".join([f"`col{n+1}`┃:art: **{utils.Colors(n+1).name}**┃:coin:**{utils.item_price(utils.Colors(n+1).type)}**" for n in range(9)]))
        embed.add_field(name="Colors (2)", value="\n".join([f"`col{n+10}`┃:art: **{utils.Colors(n+10).name}**┃:coin:**{utils.item_price(utils.Colors(n+10).type)}**" for n in range(9)]))
        embed.set_footer(text="page 5/7")
        
        page6 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name="Colors (3)", value="\n".join([f"`col{n+19}`┃:art: **{utils.Colors(n+19).name}**┃:coin:**{utils.item_price(utils.Colors(n+19).type)}**" for n in range(3)]))
        embed.set_footer(text="page 6/7")
        
        page7 = embed = utils.embed_help(ctx.author, "**<:BeanMan:1110981189466079274>┃Bean's Goods**", "Use `b!buy >id<` to buy an item from the store!", discord.Colour.purple(), True, True)
        embed.add_field(name="Fonts", value="\n".join([f"`font{n+1}`┃:keyboard: [__**{utils.Fonts(n+1).name}**__]({utils.Fonts(n+1).link})┃:coin:**{utils.item_price(utils.Fonts(n+1).type)}**" for n in range(7)]))
        embed.set_footer(text="page 7/7")
        
        pages = [page1, page2, page3, page4, page5, page6, page7]
        buttons = ["⏮", "◀", "▶", "⏭"]
        current = 0
        msg = await ctx.reply(embed=pages[current])
        
        for button in buttons:
          await msg.add_reaction(button)
          
        while True:
            try:
              reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message.id == msg.id and reaction.emoji in buttons, timeout=25)
            
            except asyncio.TimeoutError:
                embed = pages[current]
                embed.set_footer(text="Timeout")
                await msg.clear_reactions()
                break
                return
            else:
                previous_pages = current

                if reaction.emoji == "⏮":
                    current = 0
        
                elif reaction.emoji == "◀":
                    if current > 0:
                        current -= 1
            
                elif reaction.emoji == "▶":
                    if current < len(pages) - 1:
                        current += 1

                elif reaction.emoji == "⏭":
                    current = len(pages) - 1
                
                for button in buttons:
                    await msg.remove_reaction(button, ctx.author)
        
                if current != previous_pages:
                    await msg.edit(embed=pages[current])

    @commands.command(name="buy")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buy_command(self, ctx, item:str, amount:int=1):
        item = item.lower()
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
        if amount < 1:
            await ctx.reply("<:Error:957349442514718800>┃Enter a valid number!")
            return
        if amount > 10000:
            await ctx.reply("<:Error:957349442514718800>┃You can't buy that much, silly!")
            return
        logs = self.bot.get_channel(1109590623012524063)
        points = utils.get_user_points(ctx.author)
        coins = utils.get_user_coins(ctx.author)
        if item[:2] == "bg":
            pro = item[2:]
            background = utils.Backgrounds(pro, ctx.author)
            price = utils.item_price(background.type)
            have, dbHave = background.have, background.dbHave

            if not price:
                await ctx.send("<:Error:957349442514718800>┃You can't buy this!")
                return
            if pro in have:
                await ctx.reply("<:Error:957349442514718800>┃You already own this!")
                return
            if background.id == "Error":
                await ctx.reply("<:Error:957349442514718800>┃Not a valid ID!")
                return
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return

            with sqlite3.connect('main.sqlite') as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE profiles SET background_have = '{dbHave},{pro}' WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought **{background.name}** background!")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **{background.name}**")
            
        elif item[:2] == "ad":
            pro = item[2:]
            gear = utils.Gear(pro, ctx.author)
            price = utils.item_price(gear.type)
            have, dbHave = gear.have, gear.dbHave

            if not price:
                await ctx.send("<:Error:957349442514718800>┃You can't buy this!")
                return
            if pro in have:
                await ctx.reply("<:Error:957349442514718800>┃You already own this!")
                return
            if gear.id == "Error":
                await ctx.reply("<:Error:957349442514718800>┃Not a valid ID!")
                return
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return

            with sqlite3.connect('main.sqlite') as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE profiles SET gear_have = '{dbHave},{pro}' WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought **{gear.name}**!")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **{gear.name}**")
        
        elif item[:3] == "col":
            pro = item[3:]
            color = utils.Colors(pro, ctx.author)
            price = utils.item_price(color.type)
            have, dbHave = color.have, color.dbHave

            if not price:
                await ctx.send("<:Error:957349442514718800>┃You can't buy this!")
                return
            if pro in have:
                await ctx.reply("<:Error:957349442514718800>┃You already own this!")
                return
            if color.id == "Error":
                await ctx.reply("<:Error:957349442514718800>┃Not a valid ID!")
                return
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return

            with sqlite3.connect('main.sqlite') as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE profiles SET color_have = '{dbHave},{pro}' WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought **{color.name}**!")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **{color.name}**")
        
        elif item[:4] == "font":
            pro = item[4:]
            font = utils.Fonts(pro, ctx.author)
            price = utils.item_price(font.type)
            have, dbHave = font.have, font.dbHave

            if not price:
                await ctx.send("<:Error:957349442514718800>┃You can't buy this!")
                return
            if pro in have:
                await ctx.reply("<:Error:957349442514718800>┃You already own this!")
                return
            if font.id == "Error":
                await ctx.reply("<:Error:957349442514718800>┃Not a valid ID!")
                return
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return

            with sqlite3.connect('main.sqlite') as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE profiles SET font_have = '{dbHave},{pro}' WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought **{font.name}**!")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **{font.name}**")

        elif item in ["ticket", "tickets"]:
            price = utils.item_price(item, amount)
            if points < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, price - points)}**!")
                return
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET tickets = {utils.get_user_tickets(ctx.author) + amount} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE global SET lottery = {utils.get_lottery_pot() + price}")
                cursor.execute(f"UPDATE main SET points = {points - price} WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought: **{amount} {item.title()}**!")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **{amount} {item}**")
            
        elif item == "dcrate":
            price = utils.item_price('diamond_crate', amount)
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE main SET diamond_crate = {utils.get_user_diamond_crate(ctx.author) + amount} WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought <:DiamondCrate:1129920579504455701>**{amount}**")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **1 {item}**")
            
        elif item == "crate":
            price = utils.item_price('crate', amount)
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE main SET crate = {utils.get_user_crate(ctx.author) + amount} WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f":credit_card:┃You bought <:Crate:1129920387178831972>**{amount}**")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **1 {item}**")
            
        elif item == "rod":
            rod = utils.get_user_rod(ctx.author)
            price = utils.item_price("rod", user=ctx.author)
            if not price:
                await ctx.reply("<:Error:957349442514718800>┃Your rod is already at max rarity.")
                return
            if coins < price:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing :coin:**{utils.darkness_text(ctx.author, price - coins)}**!")
                return
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET coins = {coins - price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE main SET rod = {rod + 1} WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(":credit_card:┃You upgraded your rod!")
            await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **1 {item}**")
            
        elif item in utils.buy_list:
            item_price = utils.item_price(item, amount)
            if item_price > points:
                await ctx.reply(f"<:Error:957349442514718800>┃You're missing <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, item_price - points)}**!")
                return
            if item == "nitro":
                db = sqlite3.connect("main.sqlite")
                cursor = db.cursor()
                cursor.execute("SELECT nitro FROM teams")
                nitroCount = cursor.fetchone()
                if nitroCount[0] < 1:
                    await ctx.reply("<:Error:957349442514718800>┃Nitro is out of stock!")
                    cursor.close(); db.close()
                    return
                utils.badgeUpdate(ctx.author, "buy", amount)
                cursor.execute(f"UPDATE main SET points = {utils.get_user_points(ctx.author) - item_price} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE teams SET nitro = {nitroCount[0] - 1}")
                db.commit()
                LZulb = await self.bot.fetch_user(683886490211713176)
                dmuser = await self.bot.fetch_user(ctx.author.id)
                nitroID = utils.makeID()
                await ctx.reply("<:V_PurpleVerify:868218741660450837>┃Your request is pending! Make sure your friend requests or DMs are open. If you don't hear back 24 hours, make a ticket under <#1109608389216043019>. Check DMs for your Nitro ID.")
                await dmuser.send(f"Great job winning Nitro! Here's your Nitro ID: `{nitroID}`. Once prompted by **{LZulb}**, please provide the Nitro ID. DO NOT share this code with anyone.")
                await LZulb.send(f"**{ctx.author}** claimed Nitro.")
                await logs.send(f"<:U_Nitro:1111426154851737670>┃**{ctx.author}'s** Nitro ID is: `{nitroID}`.")
                cursor.close()
                db.close()
            else:
                utils.badgeUpdate(ctx.author, "buy", amount)
                utils.main_database_update([ctx.author.id,ctx.author.id],["points",item],[item_price, amount],["sub","add"])
                await ctx.reply(f":credit_card:┃You bought: **{amount} {item.title()}**")
                await logs.send(f":credit_card:┃**{ctx.author.display_name}** bought **{amount} {item}**")
        else:
            await ctx.reply("<:Error:957349442514718800>┃Not a valid item!")
    
    @commands.command(aliases=['inv', 'inventory'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def inventory_command(self, ctx, user:discord.Member=None):
        if ctx.author.id != 683886490211713176:
            if not await utils.generalCheck(self.bot, ctx):
                return

        if user is None:
            user = ctx.author
        
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT butter FROM main WHERE id = {user.id}")
        butter_count = cursor.fetchone()
        cursor.execute(f"SELECT darkness FROM main WHERE id = {user.id}")
        darkness_count = cursor.fetchone()
        cursor.execute(f"SELECT random FROM main WHERE id = {user.id}")
        random_count = cursor.fetchone()
        cursor.execute(f"SELECT hunger FROM main WHERE id = {user.id}")
        hunger_count = cursor.fetchone()
        cursor.execute(f"SELECT imposter FROM main WHERE id = {user.id}")
        imposter_count = cursor.fetchone()
        cursor.execute(f"SELECT beans FROM main WHERE id = {user.id}")
        beans_count = cursor.fetchone()
        cursor.close(); db.close()
        crate = utils.get_user_crate(user)
        dcrate = utils.get_user_diamond_crate(user)
        tickets = utils.get_user_tickets(ctx.author)
        rod = f"\n{utils.rodEmoji[utils.get_user_rod(user)]}"
        
        page1 = embed = utils.embed_help(user, title=f"<:Backpack:957349442581827604>┃**{user.display_name}**'s Inventory", color=discord.Colour.blue(), author=True, timestamp=True)
        embed.add_field(name=":smiling_imp:┃**Sabotages**", value=f":butter:Butter┃**{butter_count[0]}**\n:night_with_stars: Darkness┃**{darkness_count[0]}**\n:game_die:Random┃**{random_count[0]}**\n:canned_food:Hunger┃**{hunger_count[0]}**\n:japanese_ogre:Imposter┃**{imposter_count[0]}**")
        embed.add_field(name=":cloud:┃Misc", value=f":beans:Beans┃**{beans_count[0]}**\n<:Crate:1129920387178831972>Crate┃**{crate}**\n<:DiamondCrate:1129920579504455701>Diamond Crate┃**{dcrate}**\n:tickets:Tickets┃**{tickets}**{rod}")
        embed.set_footer(text="page 1/5")
        
        page2 = embed = utils.embed_help(user, title=f"<:Backpack:957349442581827604>┃**{user.display_name}**'s Inventory", color=discord.Colour.blue(), author=True, timestamp=True)
        embed.add_field(name="Backgrounds", value=utils.inv_background(user))
        embed.set_footer(text="page 2/5")
        
        page3 = embed = utils.embed_help(user, title=f"<:Backpack:957349442581827604>┃**{user.display_name}**'s Inventory", color=discord.Colour.blue(), author=True, timestamp=True)
        embed.add_field(name="Avatar Decoration", value=utils.inv_gear(user))
        embed.set_footer(text="page 3/5")
        
        page4 = embed = utils.embed_help(user, title=f"<:Backpack:957349442581827604>┃**{user.display_name}**'s Inventory", color=discord.Colour.blue(), author=True, timestamp=True)
        embed.add_field(name="Colors", value=utils.inv_color(user))
        embed.set_footer(text="page 4/5")

        page5 = embed = utils.embed_help(user, title=f"<:Backpack:957349442581827604>┃**{user.display_name}**'s Inventory", color=discord.Colour.blue(), author=True, timestamp=True)
        embed.add_field(name="Fonts", value=utils.inv_font(user))
        embed.set_footer(text="page 5/5")
        
        inv_pages = [page1, page2, page3, page4, page5]
        buttons = ["⏮", "◀", "▶", "⏭"]
        current = 0
        msg = await ctx.reply(embed=inv_pages[current])
        
        for button in buttons:
          await msg.add_reaction(button)
          
        while True:
            try:
              reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.message.id == msg.id and reaction.emoji in buttons, timeout=25)
            
            except asyncio.TimeoutError:
                embed = inv_pages[current]
                embed.set_footer(text="Timeout")
                await msg.clear_reactions()
                break
                return
            else:
                previous_pages = current

                if reaction.emoji == "⏮":
                    current = 0
        
                elif reaction.emoji == "◀":
                    if current > 0:
                        current -= 1
            
                elif reaction.emoji == "▶":
                    if current < len(inv_pages) - 1:
                        current += 1

                elif reaction.emoji == "⏭":
                    current = len(inv_pages) - 1
                
                for button in buttons:
                    await msg.remove_reaction(button, ctx.author)
        
                if current != previous_pages:
                    await msg.edit(embed=inv_pages[current])
    
    @commands.command(name="give")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give_command(self, ctx, member:discord.Member, amount:int, cur:str="points"):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return

        if cur in ["coins", "coin", "c"]:
            emoji = ":coin:"
            cur = utils.get_user_coins(ctx.author)
            dis = "coins"
        else:
            emoji = "<:Booster:868199875509092422>"
            cur = utils.get_user_points(ctx.author)
            dis = "points"
        
        logs = self.bot.get_channel(1109590623012524063)
    
        if cur < amount:
            await ctx.reply(f"<:Error:957349442514718800>┃You don't have enough {dis} to give!")
        elif amount < 1:
            await ctx.reply("<:Error:957349442514718800>┃Please enter a valid amount!")
        elif member.id == ctx.author.id:
            await ctx.reply(f"<:Error:957349442514718800>┃You already own those {dis}!")
        else:
            if amount >= 100 and cur == 'points':
                await utils.secret_add(1114995423057301595, "Santa", ctx.author, ctx.message, "santa")
            utils.main_database_update([ctx.author.id, member.id], [dis, dis], [amount, amount], ["sub", "add"])
            await ctx.reply(f"You gave **{member.display_name} {emoji}{amount}**!")
            await logs.send(f"{emoji}┃**{ctx.author}** gave **{member} {emoji}{amount}**")
    
    @commands.command(aliases=["slot", "slots"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def slot_command(self, ctx, amount:int, category="points"):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
            
        if category in ["coins", "coin"]:
            cur = utils.get_user_coins(ctx.author)
            category, entry = "c", "coins"
        elif category in ["points", "point"]:
            cur = utils.get_user_points(ctx.author)
            category, entry = "p", "points"
        else:
            await ctx.reply("<:Error:957349442514718800>┃That's not a valid category!")
            return
            
        if cur < amount:
            await ctx.reply("<:Error:957349442514718800>┃You don't have the funds for this.")
            return
        if amount > 100 and category == "p":
            await ctx.reply("<:Error:957349442514718800>┃Keep point bets 100 or lower!")
            return
        if amount > 10000 and category == "c":
            await ctx.reply("<:Error:957349442514718800>┃Keep coin bets 10,000 or lower!")
            return
        if amount < 1:
            await ctx.reply("<:Error:957349442514718800>┃Enter a valid amount!")
            return
        
        emojis = {
            "p": "<:Booster:868199875509092422>",
            "c": ":coin:",
            "rolling": "<a:Slots:1129261852489162762>",
            "bean": "<:SlotsBean:1129473782654976010>",
            "cherry": "<:SlotsCherry:1129473784605311076>",
            "points": "<:SlotsPoint:1129473789772697640>",
            "coins": "<:SlotsCoin:1129473786098491523>",
            "eggplant": "<:SlotsEggplant:1129473787738468483>",
            "skull": "<:SlotsSkull:1129473790930337903>"
        }

        slots = {
            1: emojis["rolling"],
            2: emojis["rolling"],
            3: emojis["rolling"]
        }

        msg = await ctx.reply(f"`║           ║`\n`╣` {slots[1]} {slots[2]} {slots[3]}`╠`\n`║           ║`")

        for count in range(3):
            rEmoji = random.choices(list(emojis.keys())[3:], weights=[5,10,10,25,35,15], k=100)
            slots[count + 1] = emojis[random.choice(rEmoji)]
            await asyncio.sleep(.8)
            await msg.edit(content=f"`║           ║`\n`╣` {slots[1]} {slots[2]} {slots[3]}`╠`\n`║           ║`")
            
        multi = 1
        
        slot_bean = len(re.findall(emojis['bean'], "".join([n for n in slots.values()])))
        slot_cherry = len(re.findall(emojis['cherry'], "".join([n for n in slots.values()])))
        slot_points = len(re.findall(emojis['points'], "".join([n for n in slots.values()])))
        slot_coins = len(re.findall(emojis['coins'], "".join([n for n in slots.values()])))
        slot_eggplants = len(re.findall(emojis['eggplant'], "".join([n for n in slots.values()])))
        slot_skulls = len(re.findall(emojis['skull'], "".join([n for n in slots.values()])))

        if slot_skulls == 3:
            multi += .25
            
        if slot_eggplants == 3:
            multi += 1.5
            
        if slot_coins == 3:
            multi += 2.5
            
        if slot_points > 1:
            if slot_points == 3:
                multi += 5
            else:
                multi += 2
                
        if slot_cherry > 0:
            if slot_cherry == 1:
                multi += 1
            elif slot_cherry == 2:
                multi += 3
            else:
                multi += 10
                
        if slot_bean == 3:
            multi += 100

        if multi == 1:
            await msg.edit(content=f"`║           ║`\n`╣` {slots[1]} {slots[2]} {slots[3]}`╠`\n`║           ║`\nYou lost {emojis[category]}**{amount}**")
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET {entry} = {cur - amount} WHERE id = {ctx.author.id}")
            cursor.close()
        else:
            await msg.edit(content=f"`║           ║`\n`╣` {slots[1]} {slots[2]} {slots[3]}`╠`\n`║           ║`\nTotal Profit: {emojis[category]}**{int((amount * multi) - amount)}**")
            
            with sqlite3.connect("main.sqlite") as cursor:
                cursor.execute(f"UPDATE main SET {entry} = {cur + int((amount * multi) - amount)} WHERE id = {ctx.author.id}")
            cursor.close()

    @commands.command(name="open")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def open_command(self, ctx, item:str):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
        if item == "crate":
            c = utils.get_user_crate(ctx.author)
            if c < 1:
                await ctx.reply("<:Error:957349442514718800>┃You don't have a crate to open.")
                return
            pool = random.choices(["C", "R", "L", "coins1", "coins2", "coins3", "nothing"], weights=[30, 15, 5, 40, 25, 15, 20], k=150)
            multi = 1
            emoji = "<:V_GreenVerify:868218741765316638>"
            crate, cSet = "crate", c - 1
        elif item == "dcrate":
            c = utils.get_user_diamond_crate(ctx.author)
            if c < 1:
                await ctx.reply("<:Error:957349442514718800>┃You don't have a diamond crates to open.")
                return
            pool = random.choices(["R", "L", "coins1", "coins2", "coins3"], weights=[30, 10, 10, 30, 20], k=100)
            multi = 3.5
            emoji = "<:V_DarkCyanVerify:868218741727580282>"
            crate, cSet = "diamond_crate", c - 1
        else:
            await ctx.reply("<:Error:957349442514718800>┃Not a valid item.")
        choice = random.choice(pool)
        if choice == "C":
            if random.randint(1,2) == 1:
                ID = random.randint(1,utils.Backgrounds().commons)
                background = utils.Backgrounds(f"C{ID}", user=ctx.author)
                entry = "background_have"
                name, amount = ":frame_photo:", background.name
                set = f'{background.dbHave},C{ID}'
            else:
                ID = random.randint(1,utils.Gear().commons)
                gear = utils.Gear(f"C{ID}", user=ctx.author)
                entry = "gear_have"
                name, amount = ":frame_photo:", gear.name
                set = f'{gear.dbHave},C{ID}'
        elif choice == "R":
            if random.randint(1,2) == 1:
                ID = random.randint(1,utils.Backgrounds().rares)
                background = utils.Backgrounds(f"R{ID}", user=ctx.author)
                entry = "background_have"
                name, amount = ":frame_photo:", background.name
                set = f'{background.dbHave},R{ID}'
            else:
                ID = random.randint(1,utils.Gear().rares)
                gear = utils.Gear(f"R{ID}", user=ctx.author)
                entry = "gear_have"
                name, amount = ":frame_photo:", gear.name
                set = f'{gear.dbHave},R{ID}'
        elif choice == "L":
            if random.randint(1,2) == 1:
                ID = random.randint(1,utils.Backgrounds().legendaries)
                background = utils.Backgrounds(f"L{ID}", user=ctx.author)
                entry = "background_have"
                name, amount = ":frame_photo:", background.name
                set = f'{background.dbHave},L{ID}'
            else:
                ID = random.randint(1,utils.Gear().legendaries)
                gear = utils.Gear(f"L{ID}", user=ctx.author)
                entry = "gear_have"
                name, amount = ":frame_photo:", gear.name
                set = f'{gear.dbHave},L{ID}'
        elif choice == "beans":
            entry = "beans"
            name, amount = ":beans:", random.randint(1,3)
            set = utils.get_user_beans(ctx.author) + amount
        elif choice == "coins1":
            entry = "coins"
            name, amount = ":coin:", random.randint(int(6500*multi),int(7500*multi))
            set = utils.get_user_coins(ctx.author) + amount
        elif choice == "coins2":
            entry = "coins"
            name, amount = ":coin:", random.randint(int(8500*multi),int(9500*multi))
            set = utils.get_user_coins(ctx.author) + amount
        elif choice == "coins3":
            entry = "coins"
            name, amount = ":coin:", random.randint(int(10500*multi),int(11500*multi))
            set = utils.get_user_coins(ctx.author) + amount
        elif choice == "nothing":
            entry = False
            name, amount = False, False
            set = False
        with sqlite3.connect("main.sqlite") as cursor:
            cursor.execute(f"UPDATE main SET {crate} = {cSet} WHERE id = {ctx.author.id}")
        cursor.close()
        if type(entry) == str:
            if entry in ["background_have", "gear_have"]:
                with sqlite3.connect("main.sqlite") as cursor:
                    cursor.execute(f"UPDATE profiles SET {entry} = '{set}' WHERE id = {ctx.author.id}")
            else:
                with sqlite3.connect("main.sqlite") as cursor:
                    cursor.execute(f"UPDATE main SET {entry} = {set} WHERE id = {ctx.author.id}")
            cursor.close()
            await ctx.reply(f"{emoji}┃You got {name}**{utils.niceNum(amount)}**.")
        else:
            await ctx.reply(":x:┃You didn't get anything.")

    @commands.command(name="lottery")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lottery_command(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        pot = f"**Pot**: <:Booster:868199875509092422>__{utils.niceNum(utils.get_lottery_pot())}__"
        left = utils.time_check(None, "lottery_cooldown", "global")
        if left < 1:
            await utils.lottery_win(ctx, self.bot)
            left = utils.time_check(None, "lottery_cooldown", "global")
        timeLeft = f"**Ends In**: __{utils.cooldown_help(ctx, left, True)}__"
        
        embed = utils.embed_help(ctx.author, "Lottery Information", f"{pot}\n{timeLeft}", discord.Colour.yellow(), True, True)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
    print("Economy loaded")