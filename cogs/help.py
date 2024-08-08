import discord
import utils, game_utils
import sqlite3, datetime, asyncio, random
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from datetime import datetime, timedelta

class HelpCog(commands.Cog, name="Help"):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def help(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        msg = """- To get more help with any of the commands, type: `b!help >command<`!
### <:Booster:868199875509092422>┃__Economy__
points, beg, bet, shop, give, inv, buy, daily, slots, open, lottery
### :smiling_imp:┃__Sabotage__
butter, darkness, random, hunger, imposter
### :video_game:┃__Games__
memory, battle, rps, hangman, roll, block, fish
### :smile:┃__Fun__
rep, cake
### :fire:┃__Customize__
profile, equip, color, aboutme, role
### :thinking:┃__Extra__
badges, fetch, lb, team, cooldown
### :gear:┃__Bot Prefixes__
`b!` / `b?`
"""
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Help Commands**", description = msg, author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="all")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def help_all(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        msg = """- To get more help with any of the commands, type: `b!help >command<`!
### <:Booster:868199875509092422>┃__Economy__
points, beg, bet, shop, give, inv, buy, daily, slots, open, lottery
### :smiling_imp:┃__Sabotage__
butter, darkness, random, hunger, imposter
### :video_game:┃__Games__
memory, battle, rps, hangman, roll, block, fish
### :smile:┃__Fun__
rep, cake
### :fire:┃__Customize__
profile, equip, color, aboutme, role
### :thinking:┃__Extra__
badges, fetch, lb, team, test, cooldown
### <:DiscoordShield:879192337102823424>┃__Mod__
clear
### <:AdminCheck:868216411896569857>┃__Admin__
force, ban, let, magic, delete, create, THEGREATRESET
### :gear:┃__Bot Prefixes__
`b!` / `b?`
"""
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Help Commands**", description = msg, author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(aliases=["points", "cash", "wallet", "money", "balance", "bal"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_points(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Points Command**", description = "- How to use: `b!points`\nUsing this command will show you your points!", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="beg")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_beg(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Beg Command**", description = "- How to use: `b!beg`\nUsing this command will give you a chance to earn some points!", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="gamble")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_gamble(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Gamble Command**", description = "- How to use: `b!gamble`\nUsing this command will give you a chance to earn anywhere from .85% - 1.15% your initial bet.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(aliases=["shop", "store"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_shop(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Shop Command**", description = "- How to use: `b!shop`\nUsing this command will open up a shop with items you can buy.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="give")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_give(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Give Command**", description = "- How to use: `b!give (user) (amount)`\nUsing this command will give whatever user you mention the amount of money you specified.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="buy")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_buy(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Buy Command**", description = "- How to use: `b!buy (item id) (amount)`\nUsing this command will buy the item you choose.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="daily")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_daily(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Daily Command**", description = "- How to use: `b!daily`\nUsing this command will give you a points bonus depending on your daily streak. This command can only be used once per day.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(aliases=["inv", "inventory"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_inv(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Inventory Command**", description = "- How to use: `b!inv`\nUsing this command will show your inventory.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="roll")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_roll(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Roll Command**", description = "- How to use: `b!roll`\nUsing this command will give a chance to earn a character of the code relating to your team.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="memory")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_memory(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Memory Game**", description = "- How to use: `b!memory`\nThis will bring you into a memory game where you compete for points.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="battle")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_battle(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Battle Game**", description = "- How to use: `b!battle (team number) (amount)`\nWhen you use this command, you start a battle with whatever team you choose. The first team to get 15 points wins. The pot is split among the winning team members. To join a battle, you must be on the team they challenged and must type `join (amount)`.\n\nIf there are 5 people on both teams and the pot is at least 500 points, the winning team will earn a part of the code for their team.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="rps")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_rps(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃RPS Game**", description = "- How to use: `b!rps (user) (amount)`\nRPS stands for Rock, paper, scissors. When you challenge someone to RPS, the person you challenged must agree to the bets to continue. If they agree, the person that started the battle will go first. Bean Man will send a DM to each person asking for their choice.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="team")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_team(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Team Command**", description = "- How to use: `b!team (team number)`\nUsing this command assigns you to a team. This can't be undone. You're stuck with whatever team you choose. You can make a ticket to <#1109608389216043019> to change your team if you have a valid reason why.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="butter")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_butter(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Butter Sabotage**", description = "- How to use: `b!sab (team number) butter`\nUsing this command sabotages the team of your choice with the butter effect. The effect lasts for 1 hour and can't stack. Butter gives the affected team of your choice a 25% chance to fail whatever command they use.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="darkness")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_darkness(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Darkness Sabotage**", description = "- How to use: `b!sab (team number) darkness`\nUsing this command sabotages the team of your choice with the darkness effect. The effect lasts for 1 hour and can't stack. Darkness hides certain details within the response message from the affected team users.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="random")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_random(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Random Sabotage**", description = "- How to use: `b!sab (team number) random`\nUsing this command increases the odds of failing the **roll** command by 0.0005% forever for the affected team. This sabotage can stack.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="hunger")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_hunger(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Hunger Sabotage**", description = "- How to use: `b!sab (team number) hunger`\nUsing this command sabotages the team of your choice with the hunger effect. The effect lasts for 1 hour and can't stack. Hunger makes Bean Man only function if the user on the affected team has beans in their inventory.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="imposter")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_imposter(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Imposter Sabotage**", description = "- How to use: `b!sab (team number) imposter`\nUsing this command sabotages the team of your choice with the imposter effect. The effect lasts for 1 hour and can't stack. Imposter makes users affected by the sabotage pass a human verification test 50% of the time.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="beans")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_beans(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Beans Item**", description = "Beans. A yummy and effective way to combat Bean Man when he's hungry!", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(aliases=["badges", "badge"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_badge(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Badge Command**", description = "- How To Use: `b!badges`\nBadges track your progress with certain events in Bean Man. You can unlock **Secret badges** by doing certain tasks around the server.", author=True, timestamp=True)
        await ctx.reply(embed=embed)
    
    @help.command(name="fetch")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_fetch(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Fetch Command**", description = "- How To Use: `b!fetch (top)`\nThe fetch command only grabs the eligible users that can play the final RPS to win the Nitro.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["hangman", "hm"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_hangman(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Hangman Game**", description = "- How To Use: `b!hm (category)`\nThe hangman game gives you *coins* if you win. You can pick between: animals, foods, games, pokemon (water, fire, grass), or all.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["coins", "coin"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_coins(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Coins**", description = "Coins are used to buy many different cosmetic items. Explore the buy command to find everything you can buy with coins!", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["lb", "leaderboard"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_leaderboard(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Leaderboard Command**", description = "- How To Use: `b!lb (category) (top)`\nThis command sends the top of whatever category you input. You can choose from: `points`, `coins`, `daily`, `streak`, `rps`, `hm`\nIf you want more categories, make a request under <#1109608389216043019>.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="profile")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_profile(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Profile Command**", description = "- How To Use: `b!profile`\nThis command lets you view your Bean Man profile.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="equip")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_equip(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466    079274>┃Equip Command**", description = "- How To Use: `b!equip (id)`\nThis command lets you equip items to your profile.\n\nExamples:\n- `b!equip bg3` Equips a profile background.\n- `b!equip ad3` Equips avatar gear.\n- `b!equip font3` Equips font for your profile.\n- `b!equip badge3 1` Equips a badge in the slot you specify. badge0 removes the badge.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["color", "col"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_color(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Color Command**", description = "- How To Use: `b!col (category) (id)`\nThis command lets you add more color to your profile.\n\nExamples:\n- `b!col name col3` This changes the color of your name on your profile.\n- `b!col border col3` This changes the color of your border on your profile.\n- `b!col am col3` This colors your about me text on your profile.\n- `b!col bg col3` This colors your about me background on your profile.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["aboutme", "am"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_aboutme(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃About Me Command**", description = "- How To Use: `b!am (text)`\nThis command lets you set your about me to be whatever you want it to be as long as it's under 150 characters. You can use the command without inputting any text to remove your about me if you so wish.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["role", "roles"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_role(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Role Command**", description = "- How To Use: `b!role (id)`\nIf you provide a color ID, you will be given a color role. If you provide \"top\", you will be displayed at the top of the leaderboard.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["fish", "fishing"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_fish(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Fish Game**", description = "- How To Use: `b!fish`\nTo start fishing, you need to first buy a fishing rod which can be found inside the buy command. You can fish up trash, coins/points, and crates.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(aliases=["block", "blocks"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_block(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Block Game**", description = "- How To Use: `b!block`\nWhen you use this command, you have to count all every color the bot gives you inside a squre of blocks.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="open")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_open(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Open Game**", description = "- How To Use: `b!open (item) (amount)`\nOpens an item.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="lottery")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_lottery(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Open Game**", description = "- How To Use: `b!lottery`\nVoews the amount of moeny the lottery is at. You can use `B!buy ticket (amount)` to buy tickets. Winners are chosen every week and they get the entire pot.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="force")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_force(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Force Admin**", description = "- How To Use: `b!force (user) (team)`\nThis command changes the team of the user to whichever team you choose.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="ban")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_ban(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Ban Admin**", description = "- How To Use: `b!ban (user) (True/False)`\nThis command bans the user from using Bean Man. Yes, True and False have to be capital.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="magic")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_magic(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Magic Admin**", description = "- How To Use: `b!magic (user) (amount)`\nThis command Adds the amount of money to the users wallet.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="delete")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_delete(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Delete Admin**", description = "- How To Use: `b!delete (user)`\nThis command deletes the user you choose from the database.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="create")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_create(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Delete Admin**", description = "- How To Use: `b!create (user)`\nThis command creates the user you choose a database entry.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="THEGREATRESET")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_THEGREATRESET(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃THEGREATRESET Admin**", description = "- How To Use: `b!THEGREATRESET`\nThis command sets the bot up for a competition.", author=True, timestamp=True)
        await ctx.reply(embed=embed)

    @help.command(name="let")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_let(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        embed = utils.embed_help(ctx.author, title = "**<:BeanMan:1110981189466079274>┃Let Admin**", description = "- How To Use: `b!let (user) (table) (value) (set) (type)`\nThe let command alters a value for a user.\n## user\nThe user you want to alter\n## table\nThe table you want to alter\n## value\nThe value inside the database you want to change. Yes, this is cap sensitive and MUST come from the database\n## set\nWhat you want to set the value of the entry to be\n## type\nIf you're changing the value to words, you MUST add \"string\"\n\n- Example 1: `b!let user#1234 (table) points 10`\n- Example 2: `b!let user#1234 (table) daily_cooldown None string`", author=True, timestamp=True)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
    print("Help loaded")