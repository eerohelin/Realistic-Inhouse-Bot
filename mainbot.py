import asyncio
import discord
import queueHandler
import rofldecoder
import calculateMMR
import leaderboardHandler
import random
import time
import json
import requests
from datetime import datetime

intents = discord.Intents.default()
intents.members = True

riot_api_key = ""

client = discord.Bot(command_prefix = '.', intents=intents)

queue = queueHandler.Queue([], [], [], [], [], 0) # Queue object

async def queueMessageHandler(user=None, action=None, role=None): # Actions, 1 = Queued, 2 = Left Queue 3 = Cleared Queue
    roles = {
        "top" : ["", 0],
        "jungle" : ["", 0],
        "mid" : ["", 0],
        "bottom" : ["", 0],
        "support" : ["", 0]
    }

    summoners = []
    totalSummoners = 0

    for i in roles.keys(): # Get players queueing for roles + amount of players
        attr = getattr(queue, i)
        all_values = [value for elem in attr for value in elem.keys()]
        for m in all_values:
            roles[i][0] += f"{m}  "
            roles[i][1] = len(all_values)
            summoners.append(m)
    totalSummoners = len(summoners)

    now = datetime.now() # Getting current time
    current_time = now.strftime("(%d.%m %H:%M:%S)")

    try: # Create and send Queue message
        rolesText = f"Top:     {roles['top'][1]}  {roles['top'][0]}\nJungle:  {roles['jungle'][1]}  {roles['jungle'][0]}\nMid:     {roles['mid'][1]}  {roles['mid'][0]}\nBottom:  {roles['bottom'][1]}  {roles['bottom'][0]}\nSupport: {roles['support'][1]}  {roles['support'][0]}"
        if action == 1:
            lastAction = f"> [{user}] queued {role}"
        elif action == 2:
            lastAction = f"> [{user}] left queue"
        elif action == 3:
            lastAction = f"> {user} cleared queue"
        else:
            lastAction = f"> Started queue"
        await mainMessage.edit(content=f"```ini\n[{totalSummoners} Summoners in Queue]\n{rolesText}\n____________________________________\n{lastAction} {current_time}```")
    except:
        pass

async def queueDictHandler(user, id, role, interaction):
    with open('database.json', 'r') as data:
        database = json.load(data)
        
        if str(id) in list(database['userData'].keys()): # Check if player has registered using ID
        
            attr = getattr(queue, role)
            all_values = [value for elem in attr for value in elem.values()] # Get values from queue object

            if id in all_values: # Check if user already in queue
                pass
            else:
                queue.enterQueue(id)
                attr.append({user : id})
                setattr(queue, role, attr)
                
            if queue.checkQueue() == 1:
                await queuePopHandler()
            else:
                pass

            await queueMessageHandler(user, 1, role)
            queue.acceptCheck = 0
            print(queue.__dict__.values())
        else:
            await interaction.response.send_message('Queue FAILED! You are not registered. To register, use the command "/register (EUW Summoner Name)"', ephemeral=True)

async def removePastMsgs():
    async for message in mainChannel.history(limit=15): # Delete messages
        if message.author == client.user:
            await message.delete()

@client.event
async def on_reaction_add(reaction, user): # React on accept
    message = reaction.message
    if message.id == acceptMessage.id:
        if user != client.user:
            if reaction.emoji == "???":
                for i in playerObjects:
                    if i.id == user.id:
                        i.accepted = True
                        await updatePopMessage()
                        await queueAcceptChecker()

            elif reaction.emoji == "???": # React on decline
                for i in playerObjects:
                    if i.id == user.id:
                        i.accepted = False
                        
                try:
                    for i in list(queue.__dict__.keys()): # Remove declined player from queue
                        for m in range(len(queue.__dict__[i])):
                            declinedUser = queue.__dict__[i][m]
                            if list(declinedUser.keys())[0] == user.name:
                                del queue.__dict__[i][m]
                except:
                    pass

                await mainChannel.send(content=f"{user.name} declined, cancelling match...") 
                time.sleep(5)
                await removePastMsgs()
                await startQueueFunction(mainChannel)
                
@client.event
async def on_reaction_remove(reaction, user): # Remove readycheck on reaction removal
    message = reaction.message
    if message.id == acceptMessage.id:
        if user != client.user:
            if reaction.emoji == "???":
                for i in playerObjects:
                    if i.id == user.id:
                        i.accepted = False
                        await updatePopMessage()

class queuePopPlayer(): # Create player objects when Queue pops

    def __init__(self, id, name, role):
        self.id = id
        self.name = name
        self.role = role
        self.accepted = False


async def updatePopMessage(): # Update Queue pop message
    newText = ""
    for i in playerObjects:
        if i.accepted == True:
            newText += f"{i.name} ???\n"
        else:
            newText += f"{i.name}\n"
    await acceptMessage.edit(content=f"```ini\n[Accept the match]\n{newText}```")

async def queueAcceptHandler():

    teams = [
        {
            'top' : "",
            'jungle' : "",
            'mid' : "",
            'bottom' : "",
            'support' : "",
            'opgg' : []
        },
        {
            'top' : "",
            'jungle' : "",
            'mid' : "",
            'bottom' : "",
            'support' : "",
            'opgg' : []
        }
    ]

    for i in playerObjects: # Creating teams
        for m in list(queue.__dict__.keys()):
            if i.role == m:
                for k in range(2):
                    try:
                        number = random.randint(0, len(queue.__dict__[m]) - 1)
                    except:
                        number = 0
                    try:
                        teams[k][m] = queue.__dict__[m][number]
                        del queue.__dict__[m][number]
                    except:
                        pass

    for i in range(len(teams)):
        for k in teams[i]:
            try:
                teams[i]["opgg"].append(list(teams[i][k].values())[0]) # Appends user ID
                teams[i][k] = list(teams[i][k].keys())[0]
            except:
                pass

    blue = teams[0] # Making the message
    red = teams[1]
    blueTeam = f"[Blue Team]\nTop:     {blue['top']}\nJungle:  {blue['jungle']}\nMid:     {blue['mid']}\nBottom:  {blue['bottom']}\nSupport: {blue['support']}"
    redTeam = f"[Red Team]\nTop:     {red['top']}\nJungle:  {red['jungle']}\nMid:     {red['mid']}\nBottom:  {red['bottom']}\nSupport: {red['support']}"
    createdTeams = f"{blueTeam}\n\n{redTeam}"
    
    with open('database.json', 'r') as data: # Create OPGG's by getting the summonernames from database.json using ID
        database = json.load(data)
        bOPGG = ""
        for i in blue["opgg"]:
            bOPGG += f"{database['userData'][str(i)]['summoner']},"
        rOPGG = ""
        for i in red["opgg"]:
            rOPGG += f"{database['userData'][str(i)]['summoner']},"

    blueOPGG = f"https://euw.op.gg/multisearch/euw?summoners={bOPGG}"
    redOPGG = f"https://euw.op.gg/multisearch/euw?summoners={rOPGG}"

    await removePastMsgs() # Remove past messages and send message
    await mainChannel.send(f"```ini\n[MATCH ACCEPTED]\n\n{createdTeams}```\nBlue OPGG: {blueOPGG}\nRed OPGG: {redOPGG}")

    await asyncio.sleep(60) # Wait (60s) then start the Queue again
    await removePastMsgs()
    await startQueueFunction(mainChannel)

async def queueAcceptChecker():
    checkAll = []
    for i in playerObjects:
        checkAll.append(i.accepted)
    if False in checkAll: # Check if all players have accepted
        print("Not accepted")
    else:
        if queue.acceptCheck == 0:
            print("accepted")
            await queueAcceptHandler()
            queue.acceptCheck = 1
        else:
            pass
    


async def queuePopHandler():
    global mainChannel
    mainChannel = client.get_channel(mainMessage.channel.id)

    players = {
        'top' : "",
        'jungle' : "",
        'mid' : "",
        'bottom' : "",
        'support' : ""
    }

    tempAcceptList = []

    for i in queue.__dict__.keys(): # Make list of players to mention
        for m in range(0, 2):
            user = queue.__dict__[i]
            try:
                userName = list(user[m].values())[0]
                tempAcceptList.append([userName, i])
                players[i] += f"<@{userName}> "
            except:
                pass

    await mainMessage.delete() # Delete the queue message

    await mainChannel.send(f"||{players['top'] + players['jungle'] + players['mid'] + players['bottom'] + players['support']}||") # Mention players

    acceptlist = []
    for i in tempAcceptList:
        userProfile = client.get_user(i[0])
        acceptlist.append([userProfile.name, i[0], i[1]])

    global playerObjects
    playerObjects = []

    for i in acceptlist: # Create queuepop player objects
        k = queuePopPlayer(i[1], i[0], i[2])
        playerObjects.append(k)

    global acceptMessage
    acceptMessage = await mainChannel.send(f"```ini\n ```")
    await updatePopMessage()
    await acceptMessage.add_reaction("???")
    await acceptMessage.add_reaction("???")



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

class View(discord.ui.View):

    @discord.ui.button(label="Top", style=discord.ButtonStyle.secondary, emoji="<:loltop:997609506890596423>")
    async def top_button_callback(self, button, interaction):
        await queueDictHandler(interaction.user.name, interaction.user.id, "top", interaction)

    @discord.ui.button(label="Jungle", style=discord.ButtonStyle.secondary, emoji="<:loljungle:997609532056420393>")
    async def jungle_button_callback(self, button, interaction):
        await queueDictHandler(interaction.user.name, interaction.user.id, "jungle", interaction)

    @discord.ui.button(label="Mid", style=discord.ButtonStyle.secondary, emoji="<:lolmid:997609577547837561>")
    async def mid_button_callback(self, button, interaction):
        await queueDictHandler(interaction.user.name, interaction.user.id, "mid", interaction)

    @discord.ui.button(label="Bottom", style=discord.ButtonStyle.secondary, emoji="<:loladc:997609620862419044>")
    async def bottom_button_callback(self, button, interaction):
        await queueDictHandler(interaction.user.name, interaction.user.id, "bottom", interaction)

    @discord.ui.button(label="Support", style=discord.ButtonStyle.secondary, emoji="<:lolsupport:997609646040830114>")
    async def support_button_callback(self, button, interaction):
        await queueDictHandler(interaction.user.name, interaction.user.id, "support", interaction)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.secondary, emoji="???")
    async def leave_button_callback(self, button, interaction):
        queue.enterQueue(interaction.user.id)
        user = client.get_user(interaction.user.id)
        await queueMessageHandler(user=user.name, action=2)

async def startQueueFunction(channel):
    if channel.name == "botti":
        global mainMessage
        mainMessage = await channel.send("", view=View())
        await queueMessageHandler()
    else:
        pass

@client.slash_command(description="Starts the Queue")
async def startbot(ctx):
    if ctx.channel.name == "botti":
        await ctx.channel.purge(limit=2)
        tempMsg = await ctx.respond("_ _")
        await tempMsg.delete_original_message()
        await startQueueFunction(ctx.channel)
        await mainLeaderboardHandler()
    else:
        pass
    

@client.slash_command()
async def clear(ctx):
    if ctx.channel.name == "botti":
        await ctx.defer()
        await ctx.channel.purge(limit=10)
    else:
        pass

@client.slash_command()
async def clearqueue(ctx):
    if str(ctx.channel.id) == "997609315932307500":
        queue.top = [] # Clear all role queues
        queue.jungle = []
        queue.mid = []
        queue.bottom = []
        queue.support = []
        queue.acceptCheck = 0
        await queueMessageHandler(action=3, user=ctx.user.name) # Update message
        await ctx.respond("Succesfully cleared queue", ephemeral=True)
    else:
        pass

async def getEmoji(number):
    if number == 1:
        emoji = "????"
    elif number == 2:
        emoji= "????"
    elif number == 3:
        emoji = "????"
    else: 
        emoji = "????"
    return emoji

@client.slash_command(description='View a users position on the leaderboard. Usage: /showpos (optional: @user)')
async def showpos(ctx, summoner: discord.Option(str, required=False)):
    sortedPlayers = leaderboardHandler.sortLeaderboard()

    with open('database.json', 'r') as dataBase:
        db = json.load(dataBase)

    
    if summoner == None: # If optional left empty
        summonerName = db['userData'][str(ctx.user.id)]['summoner']
        userID = str(ctx.user.id)
    else:
        try: # If optional is not a registered user
            if summoner[:2] == "<@":
                userID = summoner.split("!")[1].replace(">", "")
                summonerName = db['userData'][str(userID)]['summoner']

            else:
                return 0
        except:
            summonerName = None

    embedVar = discord.Embed(title="!Realistic Leaderboard", description=f"**Showing leaderboard position of <@{userID}>**", color=0x00ff00)

    for i in range(len(sortedPlayers)):
        if sortedPlayers[i]['summoner'] == summonerName:
            embedVar.clear_fields()
            emoji = await getEmoji(i)
            embedVar.add_field(name=f"{i + 1}. {emoji} {sortedPlayers[i]['summoner']}  ({sortedPlayers[i]['points']} ???)  {sortedPlayers[i]['wins']}W/{sortedPlayers[i]['losses']}L", value="_ _", inline=False)
        else:
            pass
    
    if embedVar.fields != []:
        await ctx.respond(ephemeral=True, embed=embedVar)
    else:
        await ctx.respond(ephemeral=True, content=f"User <@{userID}> does not have a registered account.")

    

async def updateMainLeaderboard():
    sortedPlayers = leaderboardHandler.sortLeaderboard()
    embedVar = discord.Embed(title="!Realistic Leaderboard", description=f"**Top 10**", color=0x00ff00)
    embedVar.set_footer(text="/leaderboard to view the whole leaderboard\n/showpos to view a specific users position on the leaderboard")
    embedVar.clear_fields()

    for m in range(0, 10):
        number = m + 1
        emoji = await getEmoji(number)
        embedVar.add_field(name=f"{m + 1}. {emoji} {sortedPlayers[m]['summoner']}  ({sortedPlayers[m]['points']} ???)  {sortedPlayers[m]['wins']}W/{sortedPlayers[m]['losses']}L", value="_ _", inline=False)
    await mainLeaderboardMsg.edit(embed=embedVar)

async def mainLeaderboardHandler():
    channel = client.get_channel(1000844563394596945) # #Leaderboard
    await channel.purge(limit=2)
    embedVar = discord.Embed(title="!Realistic Leaderboard", description=f"**Top 10**", color=0x00ff00)
    embedVar.set_footer(text="/leaderboard to view the whole leaderboard\n/showpos to view a specific users position on the leaderboard")
    sortedPlayers = leaderboardHandler.sortLeaderboard()

    for m in range(0, 10):
        number = m + 1
        emoji = await getEmoji(number)
        embedVar.add_field(name=f"{m + 1}. {emoji} {sortedPlayers[m]['summoner']}  ({sortedPlayers[m]['points']} ???)  {sortedPlayers[m]['wins']}W/{sortedPlayers[m]['losses']}L", value="_ _", inline=False)
    global mainLeaderboardMsg
    mainLeaderboardMsg = await channel.send(embed=embedVar)

async def leadearboardEmbedHandler(embedVar, page):

    # ---- CREATE THE PAGES ----
    sortedPlayers = leaderboardHandler.sortLeaderboard()
    numOfPages = 1
    pageNum = 0
    pagesGoneThrough = 0
    pages = {}

    for i in range(len(sortedPlayers)): # Get number of pages
        pageNum += 1
        if pageNum == 11:
            numOfPages +=1
            pageNum = 1

    if numOfPages >= page: # Check if requested page is out of reach
        pass
    else:
        return 0

    for i in range(0, numOfPages): # Create an empty dict of pages
        i += 1
        pageName = "page" + str(i)
        pages[str(pageName)] = []
    
    for i in range(0, numOfPages): # Create pages with each page holding 10 users
        i += 1
        for m in range(0, 10):
            m += pagesGoneThrough
            pageName = "page" + str(i)
            try:
                pages[pageName].append([f"{sortedPlayers[m]['summoner']}  ({sortedPlayers[m]['points']} ???)  {sortedPlayers[m]['wins']}W/{sortedPlayers[m]['losses']}L", f"{sortedPlayers[m]['wins']}W/{sortedPlayers[m]['losses']}L", m + 1])
            except:
                pass
        pagesGoneThrough += 10
    # ---- ----


    wantedPage = "page" + str(page)
    embedVar.clear_fields()
    for i in pages[wantedPage]: # Change emoji based on player ranking
        path = i
        emoji = await getEmoji(path[2])

        embedVar.add_field(name=f"{path[2]}. {emoji} {path[0]}", value="_ _", inline=False) # Create field
    return 1

@client.slash_command(description="View the whole leaderboard")
async def leaderboard(ctx):
    page = 1
    if ctx.channel.name == "priva":
        embedVar = discord.Embed(title="!Realistic Leaderboard", description=f"**Page {page}**", color=0x00ff00)

        # ---- CHANGE PAGE ----
        async def leaderBoardNextPage_callback(interaction):
            nonlocal page
            page += 1
            await updateLeaderboard(page)
        async def leaderBoardPrevPage_callback(interaction):
            nonlocal page
            if page - 1 != 0:
                page -= 1
                await updateLeaderboard(page)
            else:
                pass
        # --- ----
        

        # ---- CREATE BUTTONS ----
        leaderBoardButtonNext = discord.ui.Button(label=">", style=discord.ButtonStyle.secondary)
        leaderBoardButtonNext.callback = leaderBoardNextPage_callback

        leaderBoardButtonPrev = discord.ui.Button(label="<", style=discord.ButtonStyle.secondary)
        leaderBoardButtonPrev.callback = leaderBoardPrevPage_callback

        leaderBoardView = discord.ui.View()
        leaderBoardView.add_item(leaderBoardButtonPrev)
        leaderBoardView.add_item(leaderBoardButtonNext)
        # ---- ----


        await leadearboardEmbedHandler(embedVar, 1) # Initiate leaderboard
        original_message = await ctx.respond(ephemeral=True, embed=embedVar, view=leaderBoardView)

        async def updateLeaderboard(wantedPage):
            nonlocal page
            responseNum = await leadearboardEmbedHandler(embedVar, wantedPage) # Edit embed + get response ( 1 = success 0 = error)
            if responseNum == 1:
                embedVar.description = f"**Page {page}**"
                await original_message.edit_original_message(embed=embedVar, view=leaderBoardView) # Edit message
            else:
                page -= 1 # If requested page is out of reach

    else:
        pass


@client.slash_command(description="Register an EUW League of Legends account")
async def register(ctx, summoner: discord.Option(str)):

    summonerName = summoner

    async def verifySummoner_callback(interaction):
        r = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={riot_api_key}")
        dic = json.loads(r.content)
        if str(dic["profileIconId"]) == "4": # Check if Icon is correct
            with open('database.json', 'r') as data:
                dataBase = json.load(data)
            path = dataBase['userData'][str(ctx.user.id)] = {} # Create player in database.json
            path['summoner'] = summonerName
            path['points'] = 1000
            path['wins'] = 0
            path['losses'] = 0
            outData = json.dumps(dataBase, indent=4)

            with open('database.json', 'w') as data:
                data.write(outData)

            await ctx.respond(ephemeral=True, content=f"```ini\nSuccesfully registered summoner [{summonerName}]```")
        else:
            pass

    verifyButton = discord.ui.Button(label="Verify", style=discord.ButtonStyle.secondary)
    verifyButton.callback = verifySummoner_callback

    verifyView = discord.ui.View()
    verifyView.add_item(verifyButton)

    with open('database.json', 'r') as datab:
        database = json.load(datab)

        if str(ctx.user.id) in list(database['userData'].keys()): # Check if user has already registered
            await ctx.respond(ephemeral=True, content="You have already registered. If you wish to change your summoner name, please contact an admin.")
        else:
            await ctx.respond(ephemeral=True, content=f'```ini\nPlease change your summoner icon to the one below and click "Verify" to verify Summoner [{summoner}]```', file=discord.File('lol_icon.png'), view=verifyView)




@client.event
async def on_message(message): # Get game file
    try:
        if message.channel.name == "priva" and message.author.bot != True:
            try:
                filename = message.attachments[0].filename
                filenameOnly = filename.split(".")[0]
                filenameEnding = filename.split(".")[1]
                url = message.attachments[0].url
            except:
                filenameEnding = None

            if filenameEnding == "rofl":
                with open("database.json", "r") as dataBase:
                    database = json.load(dataBase)
                if filenameOnly not in database["pastGames"]:

                    response = requests.get(url) # Get file from discord server

                    with open("tempgame.rofl", "wb") as tempgame: # Read/Write file
                        tempgame.write(response.content)
                    database["pastGames"].append(filenameOnly)
                    outData = json.dumps(database, indent=4)
                    with open("database.json", "w") as data:
                        data.write(outData)

                    
                    dicts = rofldecoder.decodeRoflGameResult(filename)
                    mmrDicts = rofldecoder.decodeRoflMmrResult(filename)
                    gain_loss = calculateMMR.calculateMMR(990, mmrDicts[1]) # Change 990 to mmrDicts[0]

                    # ----  Add wins/losses to database ----
                    winners = []
                    losers = []
                    for i in dicts[1]['win']: # Get names of winners/losers
                        winners.append(i.split("(")[0].lower())
                    for i in dicts[1]['lose']:
                        losers.append(i.split("(")[0].lower())
                    with open('database.json', 'r') as database:
                        db = json.load(database)
                    
                    for i in list(db['userData'].keys()): # Change win/lose numbers + MMR
                        if db['userData'][i]['summoner'].lower() in winners:
                            db['userData'][i]['wins'] += 1
                            db['userData'][i]['points'] += gain_loss[0]
                        elif db['userData'][i]['summoner'].lower() in losers:
                            db['userData'][i]['losses'] += 1
                            db['userData'][i]['points'] -= gain_loss[1]
                        else:
                            pass

                    outData = json.dumps(db, indent=4)
                    with open('database.json', 'w') as data:
                        data.write(outData)
                    # ---- ----
                    
                    winMsg = f"[VICTORY +{gain_loss[0]}]\n{dicts[0]['win'][0]}\n{dicts[0]['win'][1]}\n{dicts[0]['win'][2]}\n{dicts[0]['win'][3]}\n{dicts[0]['win'][4]}\n\n"
                    loseMsg = f"[DEFEAT -{gain_loss[1]}]\n{dicts[0]['lose'][0]}\n{dicts[0]['lose'][1]}\n{dicts[0]['lose'][2]}\n{dicts[0]['lose'][3]}\n{dicts[0]['lose'][4]}"

                    gameProcessedMsg = winMsg + loseMsg

                    await updateMainLeaderboard()

                    await message.reply(content=f"Game [{filenameOnly}] successfully processed.\n\n```ini\n{gameProcessedMsg}```")

                else:
                    await message.reply(content=f"Game [{filenameOnly}] has already been processed.")
            else:
                await message.reply(content=f"Please enter a valid gamefile")
        else:
            pass
    except:
        pass

client.run('')