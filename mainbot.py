import asyncio
import discord
import queueHandler
import rofldecoder
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

async def queueMessageHandler(user=None, action=None, role=None): # Actions, 1 = Queued, 2 = Left Queue
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
        else:
            lastAction = f"> Started queue"
        await mainMessage.edit(content=f"```ini\n[{totalSummoners} Summoners in Queue]\n{rolesText}\n____________________________________\n{lastAction} {current_time}```")
    except:
        pass

async def queueDictHandler(user, id, role, interaction):
    with open('users.json', 'r') as data:
        playerData = json.load(data)
        
        if str(id) in list(playerData.keys()): # Check if player has registered using ID
        
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
            if reaction.emoji == "✅":
                for i in playerObjects:
                    if i.id == user.id:
                        i.accepted = True
                        await updatePopMessage()
                        await queueAcceptChecker()

            elif reaction.emoji == "❌": # React on decline
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
            if reaction.emoji == "✅":
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
            newText += f"{i.name} ✅\n"
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
                teams[i]["opgg"].append(list(teams[i][k].values())[0])
                teams[i][k] = list(teams[i][k].keys())[0]
            except:
                pass

    blue = teams[0] # Making the message
    red = teams[1]
    blueTeam = f"[Blue Team]\nTop:     {blue['top']}\nJungle:  {blue['jungle']}\nMid:     {blue['mid']}\nBottom:  {blue['bottom']}\nSupport: {blue['support']}"
    redTeam = f"[Red Team]\nTop:     {red['top']}\nJungle:  {red['jungle']}\nMid:     {red['mid']}\nBottom:  {red['bottom']}\nSupport: {red['support']}"
    createdTeams = f"{blueTeam}\n\n{redTeam}"
    
    with open('users.json', 'r') as data: # Create OPGG's by getting the summonernames from users.json using ID
        playerData = json.load(data)
        bOPGG = ""
        for i in blue["opgg"]:
            bOPGG += f"{playerData[str(i)]},"
        rOPGG = ""
        for i in red["opgg"]:
            rOPGG += f"{playerData[str(i)]},"

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
    if False in checkAll:
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

    for i in acceptlist: # Create Objects
        k = queuePopPlayer(i[1], i[0], i[2])
        playerObjects.append(k)

    global acceptMessage
    acceptMessage = await mainChannel.send(f"```ini\n ```")
    await updatePopMessage()
    await acceptMessage.add_reaction("✅")
    await acceptMessage.add_reaction("❌")



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

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.secondary, emoji="✖")
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
async def startqueue(ctx):
    if ctx.channel.name == "botti":
        tempMsg = await ctx.respond("_ _")
        await tempMsg.delete_original_message()
        await startQueueFunction(ctx.channel)
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
async def register(ctx, summoner: discord.Option(str)):

    summonerName = summoner

    async def verifySummoner_callback(interaction):
        r = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={riot_api_key}")
        dic = json.loads(r.content)
        if str(dic["profileIconId"]) == "4":
            with open('users.json', 'r') as data:
                playerData = json.load(data)

            playerData[str(ctx.user.id)] = summonerName
            outData = json.dumps(playerData, indent=4)

            with open('users.json', 'w') as data:
                data.write(outData)

            await ctx.respond(ephemeral=True, content=f"```ini\nSuccesfully registered summoner [{summonerName}]```")
        else:
            pass

    verifyButton = discord.ui.Button(label="Verify", style=discord.ButtonStyle.secondary)
    verifyButton.callback = verifySummoner_callback

    verifyView = discord.ui.View()
    verifyView.add_item(verifyButton)

    await ctx.respond(ephemeral=True, content=f'```ini\nPlease change your summoner icon to the one below and click "Verify" to verify Summoner [{summoner}]```', file=discord.File('lol_icon.png'), view=verifyView)



@client.event
async def on_message(message): # Get game file
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

                dicts = rofldecoder.decodeRofl(filename)
                winMsg = f"[VICTORY]\n{dicts['win'][0]}\n{dicts['win'][1]}\n{dicts['win'][2]}\n{dicts['win'][3]}\n{dicts['win'][4]}\n\n"
                loseMsg = f"[DEFEAT]\n{dicts['lose'][0]}\n{dicts['lose'][1]}\n{dicts['lose'][2]}\n{dicts['lose'][3]}\n{dicts['lose'][4]}"

                gameProcessedMsg = winMsg + loseMsg

                await message.reply(content=f"Game [{filenameOnly}] successfully processed.\n\n```ini\n{gameProcessedMsg}```")

            else:
                await message.reply(content=f"Game [{filenameOnly}] has already been processed.")
        else:
            await message.reply(content=f"Please enter a valid gamefile")
    else:
        pass

client.run('')