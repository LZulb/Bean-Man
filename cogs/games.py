import discord
import utils, game_utils
import sqlite3, datetime, asyncio, random
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from datetime import datetime, timedelta

class GamesCog(commands.Cog, name="Games"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="battle")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def battle_game(self, ctx, team2:int, amount:int=0):
        try:
            uhoh = False
            if not await utils.generalCheck(self.bot, ctx) or not await game_utils.pre_game(ctx):
                uhoh = True
                return
            if ctx.channel.id not in utils.battle_chats:
                await ctx.reply("This command only works inside battle chats!")
                uhoh = True
                return
            if team2 not in [1,2,3,4,5]:
                await ctx.reply("<:Error:957349442514718800>┃Not a valid team!")
                uhoh = True
                return
            if amount < 0:
                await ctx.reply("<:Error:957349442514718800>┃Enter a valid amount!")
                uhoh = True
                return
            db = sqlite3.connect("main.sqlite")
            cursor = db.cursor()
            team1 = utils.get_user_team(ctx.author)
            authorPoints = utils.get_user_points(ctx.author)
            if authorPoints < amount:
                await ctx.reply("<:Error:957349442514718800>┃You don't have enough points to bet!")
                uhoh = True
                return
            cursor.execute(f"UPDATE main SET points = {authorPoints - amount} WHERE id = {ctx.author.id}")
            users1 = [ctx.author]
            users2 = []
            banned = [ctx.author]
            pot = amount
            code = False
            
            if team1 == team2:
                await ctx.reply("<:Error:957349442514718800>┃Don't pick your own team!")
                uhoh = True
                return
            db.commit()
        
            loading = await ctx.reply("<a:U_Loading:1116853864914767892>┃Waiting For Users...\n\nHow to join\n- `join (amount of points)`\nTips\n- Answers won't be longer than one word!\n- Type \"start\" to start the battle!")
            while True:
                msg = await game_utils.responses(ctx.channel, self.bot, 60, team1, team2)
                if msg.attachments:
                    continue
                if msg == "timeout":
                    break
                    
                user = msg.author
                message = msg.content
                newMsg = message.split()
                team = utils.get_user_team(user)
        
                if newMsg[0].lower() in ["start", "stop"] and msg.author == ctx.author:
                    break
                if user in banned:
                    continue
                if newMsg[0].lower() != "join" or len(newMsg) > 2:
                    continue
                if len(newMsg) < 2:
                    await msg.add_reaction("❓")
                    continue
                    
                try:
                    points = utils.get_user_points(user)
                    if points < int(newMsg[1]) or int(newMsg[1]) < 0:
                        await msg.add_reaction("<:Booster:868199875509092422>")
                        continue
                    pot += int(newMsg[1])
                    cursor.execute(f"UPDATE main SET points = {points - int(newMsg[1])} WHERE id = {user.id}")
                except:
                    await msg.add_reaction("❓")
                    continue
                
                if team == team1:
                    await msg.add_reaction("✅")
                    users1.append(user)
                if team == team2:
                    await msg.add_reaction("✅")
                    users2.append(user)
                cursor.execute(f"UPDATE main SET game_playing = 'playing' WHERE id = {user.id}")
                db.commit()
                banned.append(user)
        
            if len(users2) < 1:
                await loading.edit(content=":x:┃Failed."); await asyncio.sleep(.5)
                await ctx.reply(f"<:Error:957349442514718800>┃**Team {team2}** has no members!")
                cursor.execute(f"UPDATE main SET points = {authorPoints} WHERE id = {ctx.author.id}")
                db.commit()
                return
            else:
                await loading.edit(content="<:V_GreenVerify:868218741765316638>┃Successful!"); await asyncio.sleep(.5)
                await ctx.reply("<:V_GreenVerify:868218741765316638>┃Game is starting...")
                await asyncio.sleep(3)
        
            if len(users1) >= 5 and len(users2) >= 5 and pot >= 500:
                code = True
        
            Round = 1
            score = {
                f"team{team1}": 0,
                f"team{team2}": 0
            }
            lastAnswer = "correct"
            while score[f"team{team1}"] < 15 and score[f"team{team2}"] < 15 and Round < 30:
                if lastAnswer == "correct":
                    randNum = random.choice([1, 2, 3])
                    if randNum == 1:
                        randQ = game_utils.mathQuestion(Round)
                    elif randNum == 2:
                        randQ = game_utils.randomSend()
                    else:
                        randQ = game_utils.randomQuestions()
                    await ctx.reply(f"Team {team1}: {score[f'team{team1}']}\nTeam {team2}: {score[f'team{team2}']}\nRound: {Round}\n\n{randQ[0]}")
                msg = await game_utils.responses(ctx.channel, self.bot, 20, users1, users2, False)
                if msg.attachments:
                    continue
                # Multiprocesssing
                newMsg = msg.content
                team = utils.get_user_team(msg.author)
                if msg == "timeout":
                    Round += 1
                    await ctx.reply("<:TimeoutError:957349442598633552>┃Next question!"); await asyncio.sleep(.5)
                    break
                if newMsg.lower() in randQ[1]:
                    score[f"team{team}"] += 1
                    Round += 1
                    await msg.add_reaction("✅"); await asyncio.sleep(.5)
                    lastAnswer = "correct"
                else:
                    await msg.add_reaction("❌"); await asyncio.sleep(.5)
                    lastAnswer = "wrong"
            if score[f"team{team1}"] > score[f"team{team2}"]:
                winner = team1
                winnerUsers = users1
            else:
                winner = team2
                winnerUsers = users2
            potPer = pot // len(winnerUsers)
            for user in winnerUsers:
                points = utils.get_user_points(user)
                cursor.execute(f"UPDATE main SET points = {points + potPer} WHERE id = {user.id}")
                db.commit()
                utils.badgeUpdate(user, "points", potPer)
            if code:
                alert = self.bot.get_channel(1109591422631415948)
                cursor.execute(f"SELECT team{winner}code FROM teams")
                codeAmt = cursor.fetchone()[0]
                cursor.execute(f"UPDATE teams SET team{winner}code = {codeAmt + 1}")
                db.commit()
                alert.send(f"**team {winner}** earned one character to the code!")
            for person1 in users1:
                cursor.execute(f"UPDATE main SET game_playing = 'not playing' WHERE id = {person1.id}")
            for person2 in users2:
                cursor.execute(f"UPDATE main SET game_playing = 'not playing' WHERE id = {person2.id}")
            db.commit()
            await ctx.reply(f"<a:MovingCrown:868218744583901274>┃Team **{winner}** is the winner! The pot has been split among the winners.")
        finally:
            if not uhoh:
                db.commit()
                cursor.close()
                db.close()
                users1.extend(users2)
                for user in users1:
                    utils.playing_set(user, "not playing")
            else:
                cursor.close()
                db.close()
                utils.playing_set(ctx.author, "not playing")
            
    @commands.command(name="rps")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rps_game(self, ctx, member:discord.Member, amount:int=0, cur:str="points"):
        try:
            if not await utils.generalCheck(self.bot, ctx) or not await game_utils.pre_game(ctx):
                return
            if member.id == 1109576486572265514:
                await ctx.reply("Heh, you're challenging me?")
                resultAuthor = await game_utils.makeTurn(ctx, ctx.author, self.bot)
                resultBot = random.choice(["paper", "rock", "scissors"])
                if resultAuthor == "DM":
                    await ctx.reply(f"<:Error:957349442514718800>┃I was not able to DM **{ctx.author.display_name}**.")
                    return
                if not resultAuthor:
                    await ctx.reply(f"<:Error:957349442514718800>┃**{ctx.author.display_name}** didn't provide any details.")
                    return
                if (resultAuthor == "rock" and resultBot == "scissors") or (resultAuthor == "paper" and resultBot == "rock") or (resultAuthor == "scissors" and resultBot == "paper"):
                    winner = ctx.author
                elif resultAuthor == resultBot:
                    await ctx.reply(":x:┃There was a tie!")
                    return
                else:
                    winner = member
            
                await ctx.reply(f"<a:MovingCrown:868218744583901274>┃{winner.mention} won!")
                return
            if utils.get_playing == "playing":
                await ctx.reply(f"**{member.display_name}** is already playing a game!")
                return
            utils.playing_set(member, "playing")
            if cur in ["coins", "coin", "c"]:
                emoji = ":coin:"
                authorPoints = utils.get_user_coins(ctx.author)
                memberPoints = utils.get_user_coins(member)
                dis = "coins"
            else:
                emoji = "<:Booster:868199875509092422>"
                cur = utils.get_user_points(ctx.author)
                dis = "points"
                authorPoints = utils.get_user_points(ctx.author)
                memberPoints = utils.get_user_points(member)
                
            authorTeam = utils.get_user_team(ctx.author)
            memberTeam = utils.get_user_team(member)
            code = False
            
            if authorTeam == utils.get_winner():
                if memberTeam != authorTeam:
                    await ctx.reply("<:Error:957349442514718800>┃You must choose someone from your team!")
                    return
                if utils.get_rps_able(ctx.author) == "able" and utils.get_rps_able(member) == "able":
                    code = True
                    amount = 1
        
            if ctx.author == member:
                await ctx.reply("<:Error:957349442514718800>┃Don't pick yourself.")
                return
            if amount < 1:
                await ctx.reply("<:Error:957349442514718800>┃You didn't provide a valid amount.")
                return
            if authorPoints < amount:
                await ctx.reply(f"<:Error:957349442514718800>┃You don't have enough {dis} to bet!")
                return
            if memberPoints < amount:
                await ctx.reply(f"<:Error:957349442514718800>┃**{member.display_name}** doesn't have enough {dis} to bet!")
                return
        
            preCount = 0
            if not code:
                await ctx.reply(f"**{member.display_name}**, do you wish to play Rock, Paper, Scissors with **{ctx.author.display_name}** for {emoji}**{amount}**?\n`yes`/`no`")
            else:
                await ctx.reply(f"## <:U_Star:1003776660002320404>Final RPS<:U_Star:1003776660002320404>\n**{member.display_name}**, do you wish to play your **FINAL** Rock, Paper, Scissors with **{ctx.author.display_name}**?\n`yes`/`no`")
            while preCount < 2:
                startMsg = await utils.response(ctx.channel, member, self.bot, 30)
                if startMsg == "timeout":
                    await ctx.reply("<:TimeoutError:957349442598633552>┃Timeout error!")
                    return
                elif startMsg.content.lower() not in ["yes", 'y', "no", "n"]:
                    preCount += 1
                elif startMsg.content.lower() in ["no", "n"]:
                    play = False
                    break
                else:
                    play = True
                    break
        
            if not play:
                await ctx.reply(f"**{member.display_name}** doesn't wish to play!")
                return
            
            mainMsg = await ctx.reply(f"Waiting for **{ctx.author.display_name}**...")
            resultAuthor = await game_utils.makeTurn(ctx, ctx.author, self.bot)
            if resultAuthor == "DM":
                await ctx.reply(f"<:Error:957349442514718800>┃I was not able to DM **{ctx.author.display_name}**. Everyone has been refunded and the game has ended.")
                return
            if not resultAuthor:
                await ctx.reply(f"<:Error:957349442514718800>┃**{ctx.author.display_name}** didn't provide any details. Everyone has been refunded and the game has ended.")
                return
                
            await mainMsg.edit(content=f"Waiting for **{member.display_name}**...")
            resultMember = await game_utils.makeTurn(ctx, member, self.bot)
            if resultMember == "DM":
                await ctx.reply(f"<:Error:957349442514718800>┃I was not able to DM **{member.display_name}**. Everyone has been refunded and the game has ended.")
                return
            if not resultMember:
                await ctx.reply(f"<:Error:957349442514718800>┃**{member.display_name}** didn't provide any details. Everyone has been refunded and the game has ended.")
                return
        
            if (resultAuthor == "rock" and resultMember == "scissors") or (resultAuthor == "paper" and resultMember == "rock") or (resultAuthor == "scissors" and resultMember == "paper"):
                winner = ctx.author
                loser = member
            elif resultAuthor == resultMember:
                if not code:
                    await ctx.reply(":x:┃There was a tie! Both parties were refunded.")
                    return
                else:
                    await ctx.reply(":x:┃There was a tie! Both parties may try again.")
                    return
            else:
                winner = member
                loser = ctx.author
        
            if not code:
                with sqlite3.connect('main.sqlite') as cursor:
                    cursor.execute(f"UPDATE main SET rps_wins = {utils.get_user_rps_wins(winner) + 1} WHERE id = {winner.id}")
                utils.badgeUpdate(winner, "points", amount)
                utils.main_database_update([winner.id, loser.id],[dis, dis],[amount, amount],["add", "sub"])
                await ctx.reply(f"<a:MovingCrown:868218744583901274>┃{winner.mention} won and earns {emoji}**{amount}**!")
                if utils.get_user_rps_wins(ctx.author) == 25:
                    await utils.secret_add(1132357105467281489, "Sharp", ctx.author, ctx.message, "rps")
            else:
                with sqlite3.connect('main.sqlite') as cursor:
                    cursor.execute(f"UPDATE main SET rps_wins = {utils.get_user_rps_wins(winner) + 1} WHERE id = {winner.id}")
                cursor.close()
                utils.main_database_update([loser.author.id],["rps_status"],["not able"],["set"])
                await ctx.reply(f"## <:U_Star:1003776660002320404>RPS Result<:U_Star:1003776660002320404>\n{ctx.author.mention} & {member.mention} the winner is... ||{winner.mention}||!")
        finally:
            utils.playing_set(ctx.author, "not playing")
            utils.playing_set(member, "not playing")
        
    @commands.command(name="memory")
    async def memory_game(self, ctx, end:int=0):
        try:
            if not await utils.generalCheck(self.bot, ctx) or not await game_utils.pre_game(ctx):
                return
            earn = True
            left = utils.time_check(ctx.author, "memory_cooldown", "main")
            if left < 1:
                utils.add_time(ctx.author, "memory_cooldown", 30, "minutes")
            else:
                await ctx.reply("You're playing practice mode because you're on a memory cooldown! You won't earn any points.")
                await asyncio.sleep(.5)
                earn = False

            if end < 2:
                end = 0
                    
            round = 1
            earned = 0
            state = "playing"
            multi = 1
            blocks = 3
            difficulty = 3
    
            while state == "playing":
                if end != 0:
                    if round % 3 == 0 and round != 0:
                        blocks += 1
                        multi += .20
                        difficulty += 2
                    if round % end == 0:
                        state = "not playing"
                        break
                else:
                    if round % 3 == 0 and round != 0:
                        msg = f"Round **{round}**┃<:Booster:868199875509092422>**{utils.darkness_text(ctx.author, earned)}**\nDo you want to continue and risk your points or claim your points and quit?\n`continue`/`claim`"
                        tries = 0
                        
                        while tries < 2:
                            if tries != 0:
                                    msg = "<:Error:957349442514718800>┃Enter a valid mode!"
                                    
                            if tries == 2:
                                await ctx.reply("<:Error:957349442514718800>┃Too many attempts. Game ended.")
                                state = "not playing"
                                break
            
                            await ctx.reply(msg)
                            risk = await utils.response(ctx.channel, ctx.author, self.bot, 15)
    
                            if risk == "timeout":
                                tries += 1
                                continue
                            risk = risk.content
                            if risk.lower() == "continue":
                                blocks += 1
                                multi += .20
                                difficulty += 2
                                break
                            elif risk.lower() == "claim":
                                state = "not playing"
                                break
                            else:
                                tries += 1
                        if tries == 2:
                            await ctx.reply("<:Error:957349442514718800>┃Too many attempts. Game ended.")
                            state = "not playing"
                        
                if state != "playing":
                    break
        
                points_give = int(round * multi) // 2
                if round == 1:
                    points_give += 1
                    
                colors = game_utils.random_color(blocks, difficulty)
                msg = await ctx.reply(f'Round **{round}**┃<:Booster:868199875509092422>**{utils.darkness_text(ctx.author, earned)}**\nRemember this:\n{game_utils.format_colors(colors[0])}')
                await asyncio.sleep(3.75)
                await msg.edit(content=f"Round **{round}**┃<:Booster:868199875509092422>**{utils.darkness_text(ctx.author, earned)}**\nWhat color was in slot **{colors[1] + 1}**?")
                
                guess = await utils.response(ctx.channel, ctx.author, self.bot, 3.75)
                if guess == "timeout":
                    await ctx.reply("<:TimeoutError:957349442598633552>┃Timeout error!")
                    state = "failed"
                    break
                guess = guess.content.lower()
                    
                if guess.lower() == colors[2] or guess.lower() == colors[2][0]:
                    round += 1
                    earned += points_give
                    continue
                else:
                    await ctx.reply(":x:┃Sorry, that is wrong!")
                    state = "failed"
                
            if state != "failed":
                if earn:
                    utils.badgeUpdate(ctx.author, "points", earned)
                    utils.main_database_update([ctx.author.id], ["points"], [earned], ["add"])
                    await ctx.reply(f"**{ctx.author.display_name}**, you ended up earning <:Booster:868199875509092422>**{utils.darkness_text(ctx.author, earned)}**!")
                else:
                    await ctx.reply("Practice over!")
            return
        finally:
            utils.playing_set(ctx.author, "not playing")
    
    @commands.command(aliases=["hangman", "hm"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hangman_game(self, ctx, type:str=None, more:str=None):
        try:
            if not await utils.generalCheck(self.bot, ctx) or not await game_utils.pre_game(ctx):
                return
            if type in ["foods", "food"]:
                randomWord = random.choice(utils.food_list)
            elif type in ["animals", "animal"]:
                randomWord = random.choice(utils.animal_list)
            elif type in ["games", "game"]:
                randomWord = random.choice(utils.game_list)
            elif type in ["pokemon", 'pokémon']:
                if more is None:
                    randomWord = random.choice(utils.pokemon_list)
                else:
                    if more.lower() == 'water':
                        randomWord = random.choice(utils.water_type_pokemon)
                    elif more.lower() == "fire":
                        randomWord = random.choice(utils.fire_type_pokemon)
                    elif more.lower() == "grass":
                        randomWord = random.choice(utils.grass_type_pokemon)
                    else:
                        await ctx.reply('<:Error:957349442514718800>┃Pokemon type is not "water", "fire", or "grass"!')
                        return
            elif type == "all":
                randomWord = random.choice(utils.randomWords)
            else:
                await ctx.reply('<:Error:957349442514718800>┃Type is not "foods", "animals", "games", "pokemon", or "all".')
                return
            guessed = [" "]
            tries = 0
            msg = ""

            while tries <= 6:
                display = "".join([f"{letter} " if letter in guessed else "? " for letter in randomWord])
                guessedDisplay = ''.join([f"{g}, " if (g != guessed[-1] and g != " ") else g for g in guessed])
                if len(guessed) == 1:
                    OG_MSG = await ctx.reply(f"{msg}## {display} ┃ Lives: {7 - tries}\n{guessedDisplay}\n{utils.HANGMANPICS[tries]}\nSend a letter...")
                else:
                    await OG_MSG.edit(content=f"{msg}## {display} ┃ Lives: {7 - tries}\n{guessedDisplay}\n{utils.HANGMANPICS[tries]}\nSend a letter...")
                guess = await utils.response(ctx.channel, ctx.author, self.bot, 30)
    
                if guess == "timeout":
                    msg = ":x:┃You received a time limit penalty!\n"
                    tries += 1
                    continue
                newGuess = guess.content
                if len(newGuess.lower()) > 1:
                    if newGuess.lower() == randomWord:
                        msg = "<:V_GreenVerify:868218741765316638>┃Correct!\n"
                        await OG_MSG.edit(content=f"{msg}## {''.join([letter for letter in randomWord])} ┃ Lives: {7 - tries}\n{guessedDisplay}\n{utils.HANGMANPICS[tries]}")
                        break
                    msg = ":x:┃That's not it!\n"
                    tries += 1
                    continue
                if newGuess.lower() in guessed:
                    msg = ":x:┃You already guessed that!\n"
                    tries += 1
                    continue
                    
                if newGuess.lower() not in randomWord:
                    if newGuess.lower() not in guessed:
                        guessed.append(newGuess.lower())
                    tries += 1
                    msg = ":x:┃Incorrect!\n"
                else:
                    if newGuess.lower() not in guessed:
                        guessed.append(newGuess.lower())
                    msg = "<:V_GreenVerify:868218741765316638>┃Correct!\n"
                    if "".join([letter if letter in guessed else "?" for letter in randomWord]) == randomWord:
                        await OG_MSG.edit(content=f"{msg}## {''.join([letter for letter in randomWord])} ┃ Lives: {7 - tries}\n{guessedDisplay}\n{utils.HANGMANPICS[tries]}")
                        break
            if tries == 7:
                await ctx.reply(f":x:┃You Lost! The word was **{randomWord.title()}**.")
            else:
                db = sqlite3.connect("main.sqlite")
                cursor = db.cursor()
                randomCoinAmt = random.randint(100, 350)
                if tries == 0:
                    randomCoinAmt += 100
                elif tries == 1:
                    randomCoinAmt += 50
                elif tries == 2:
                    randomCoinAmt += 25
                else:
                    randomCoinAmt = randomCoinAmt

                cursor.execute(f"UPDATE main SET coins = {utils.get_user_coins(ctx.author) + randomCoinAmt} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE main SET hm_wins = {utils.get_user_hm_wins(ctx.author) + 1} WHERE id = {ctx.author.id}")
                db.commit()
                if utils.get_user_hm_wins(ctx.author) == 25:
                    await utils.secret_add(1132357102459945010, "Hanging", ctx.author, ctx.message, "hm")

                await ctx.reply(f"<a:MovingCrown:868218744583901274>┃You won and received :coin:**{randomCoinAmt}**!")
        finally:
            utils.playing_set(ctx.author, "not playing")

    @commands.command(name="block")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def block_game(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
        colors = [":red_square:", ":green_square:", ":blue_square:", ":purple_square:", ":brown_square:", ":orange_square:", ":yellow_square:", ":white_large_square:"]
        msg = ""
        randCol = {
            random.choice(colors): 0
        }
        for n in range(49):
            col = random.choice(colors)
            if col in list(randCol.keys()):
                randCol[col] += 1
            if (n+1) % 7 == 0 and (n+1) != 1:
                msg += f"{col}\n"
            else:
                msg += col
        color, amount = list(randCol.keys())[0], list(randCol.values())[0]
        mainMsg = await ctx.reply(f"How many {color} blocks are there?\n{msg}")
        response = await utils.response(ctx.channel, ctx.author, self.bot, 5)
        if response == "timeout":
            await mainMsg.edit(content=f"How many {color} blocks are there?\n{msg}\n<:TimeoutError:957349442598633552>┃You ran out of time.")
            return
        else:
            try:
                response = int(response.content)
            except:
                await mainMsg.edit(content=f"How many {color} blocks are there?\n{msg}\n<:Error:957349442514718800>┃You didn't provide a number.")
                return
            if response == amount:
                if random.randint(1,3) == 1:
                    cur = utils.get_user_points(ctx.author)
                    rCur = random.randint(5, 13)
                    entry, name = "points", f"<:Booster:868199875509092422>**{rCur}**"
                else:
                    cur = utils.get_user_coins(ctx.author)
                    rCur = random.randint(58, 93)
                    entry, name = "coins", f":coin:**{rCur}**"
                with sqlite3.connect("main.sqlite") as cursor:
                    cursor.execute(f"UPDATE main SET {entry} = {cur + rCur} WHERE id = {ctx.author.id}")
                cursor.close()
                await mainMsg.edit(content=f"How many {color} blocks are there?\n{msg}\n<:V_GreenVerify:868218741765316638>┃Correct! You won {name}!")
            else:
                await mainMsg.edit(content=f"How many {color} blocks are there?\n{msg}\n<:Error:957349442514718800>┃The correct amount was **{amount}**!")

    @commands.command(name="fish")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def fishing_game(self, ctx):
        if not await utils.generalCheck(self.bot, ctx):
            return
        if utils.get_playing(ctx.author) == "playing":
            await ctx.reply("<:Error:957349442514718800>┃You're playing a game!")
            return
        rod = utils.get_user_rod(ctx.author)
        if rod == 0:
            await ctx.reply("<:Error:957349442514718800>┃You don't have a fishing rod.")
            return
        pond = [
            "`...,...,/\.....,/\.,..,..,`",
            "`../\..,.,.,/\..,...,../\.,`",
            "`....,./\....,,.,,,/\,..,.,`",
            "`../\..,....,.,/\.,,,../\.,`"
        ]
        fishing = ""
        catching = ""
        caught = ""
        for count in range(4):
            line = pond.pop((random.randint(0,len(pond) - 1)))
            if count == 0:
                fishing += f"{line}\n"
                catching += f"{line}       !\n"
                caught += f"{line}\n"
            elif count == 1:
                fishing += f"{line}    0\n"
                catching += f"{line}   \\ 0 /\n"
                caught += f"{line}    0/O\n"
            elif count == 2:
                fishing += f"{line}   /|\\\n"
                catching += f"{line}      |\n"
                caught += f"{line}   /|\n"
            else:
                fishing += f"{line}    /\\"
                catching += f"{line}    /\\"
                caught += f"{line}    /\\"
        mainMsg = await ctx.reply(fishing)
        pre = await utils.response(ctx.channel, ctx.author, self.bot, random.randint(2,5))
        if pre == "timeout":
            await mainMsg.edit(content=catching)
            after = await utils.response(ctx.channel, ctx.author, self.bot, .80)
            if after == "timeout":
                await mainMsg.edit(content=f"{fishing}\n:x:┃The fish got away :(")
            elif after.content.lower() == "catch":
                loot = ["trash", "cur", "crate"]
                if rod == 1:
                    pool = random.choices(loot, weights=[30,65,5], k=100)
                elif rod == 2:
                    pool = random.choices(loot, weights=[25,70,5], k=100)
                elif rod == 3:
                    pool = random.choices(loot, weights=[20,75,5], k=100)
                else:
                    pool = random.choices(loot, weights=[17,75,8], k=100)
                pick = random.choice(pool)
                if pick == "trash":
                    await mainMsg.edit(content=f"{caught}\n:x:┃You caught trash.")
                elif pick == "cur":
                    if random.randint(1,3) == 1:
                        cur = utils.get_user_points(ctx.author)
                        rCur = random.randint(5 + 2 * rod, 13 + 2 * rod)
                        entry, name = "points", f"<:Booster:868199875509092422>**{rCur}**"
                    else:
                        cur = utils.get_user_coins(ctx.author)
                        rCur = random.randint(23 + 13 * rod, 59 + 13 * rod)
                        entry, name = "coins", f":coin:**{rCur}**"
                    with sqlite3.connect("main.sqlite") as cursor:
                        cursor.execute(f"UPDATE main SET {entry} = {cur + rCur} WHERE id = {ctx.author.id}")
                    cursor.close()
                    await mainMsg.edit(content=f"{caught}\n<:V_GreenVerify:868218741765316638>┃You caught and sold your fish for {name}!")
                else:
                    crates = ["crate", "diamond_crate"]
                    if rod == 1:
                        cratePool = random.choices(crates, weights=[90,10], k=100)
                    elif rod == 2:
                        cratePool = random.choices(crates, weights=[88,12], k=100)
                    elif rod == 3:
                        cratePool = random.choices(crates, weights=[86,14], k=100)
                    else:
                        cratePool = random.choices(crates, weights=[84,16], k=100)
                    crate = random.choice(cratePool)
                    if crate == "crate":
                        crate, name, entry = utils.get_user_crate(ctx.author), "<:Crate:1129920387178831972>**Crate**", "crate"
                    else:
                        crate, name, entry = utils.get_user_diamond_crate, "<:DiamondCrate:1129920579504455701>**Diamond Crate**", "diamond_crate"
                    with sqlite3.connect("main.sqlite") as cursor:
                        cursor.execute(f"UPDATE main SET {entry} = {crate + 1} WHERE id = {ctx.author.id}")
                    cursor.close()
                    await mainMsg.edit(content=f"{caught}\n<:V_DarkCyanVerify:868218741727580282>┃You caught a {name}!")
            else:
                await mainMsg.edit(content=f"{fishing}\n:x:┃The fish got away because you didn't catch it :(")
        else:
            await mainMsg.edit(content=f"{fishing}\n:x:┃You didn't catch any anything :(")

async def setup(bot):
    await bot.add_cog(GamesCog(bot))
    print("Games loaded")