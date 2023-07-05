import json



def decodeRoflGameResult(filename):
    dicts = []
    with open('tempgame.rofl', 'r', encoding='latin1') as data:
    
        newdata = data.read().split('{') # Parse data
        for i in range(len(newdata)):
            if len(dicts) != 10:
                dictionary = {}
                replacedData = newdata[i].replace("\\", "").replace('"', "").replace("}", "") # Parse data
                replacedData = replacedData.split(']')[0]
                for m in replacedData.split(","):
                    playerdata = m.split(":")
                    try:
                        dictionary[playerdata[0]] = playerdata[1]
                        continue
                    except:
                        pass
                if "ASSISTS" in list(dictionary.keys()): # Check if dict is PLAYER
                    dicts.append(dictionary)
                else:
                    pass
                # print(f"{dictionary['NAME']} {dictionary['CHAMPIONS_KILLED']}/{dictionary['NUM_DEATHS']}/{dictionary['ASSISTS']} {dictionary['WIN']}")
                # print(dictionary)
                # print(get_key(dictionary["NAME"]))
                # print(dictionary["NAME"].encode("latin1").decode("utf8"))
                # print(replacedData.split(","))
            else:
                break
    results = {
    "win" : [],
    "lose" : []
    }

    resultsDisplay = {
        "win" : [],
        "lose" : []
    }

    for i in range(0, 10):
        try:
            if dicts[i]["WIN"] == "Win":
                name = dicts[i]['NAME'].encode("latin1").decode("utf8")
                nameChampGap = " " * (17 - len(name))
                champKdaGap = " " * (13 - len(dicts[i]['SKIN']))
                results["win"].append(f"{name}({dicts[i]['SKIN']}){champKdaGap}{dicts[i]['CHAMPIONS_KILLED']}/{dicts[i]['NUM_DEATHS']}/{dicts[i]['ASSISTS']}")
                resultsDisplay["win"].append(f"{name}{nameChampGap}({dicts[i]['SKIN']}){champKdaGap}{dicts[i]['CHAMPIONS_KILLED']}/{dicts[i]['NUM_DEATHS']}/{dicts[i]['ASSISTS']}")
            else:
                name = dicts[i]['NAME'].encode("latin1").decode("utf8")
                nameChampGap = " " * (17 - len(name))
                champKdaGap = " " * (13 - len(dicts[i]['SKIN']))
                results["lose"].append(f"{name}({dicts[i]['SKIN']}){champKdaGap}{dicts[i]['CHAMPIONS_KILLED']}/{dicts[i]['NUM_DEATHS']}/{dicts[i]['ASSISTS']}")
                resultsDisplay["lose"].append(f"{name}{nameChampGap}({dicts[i]['SKIN']}){champKdaGap}{dicts[i]['CHAMPIONS_KILLED']}/{dicts[i]['NUM_DEATHS']}/{dicts[i]['ASSISTS']}")
        except:
            pass
    fullResult = [resultsDisplay, results] # Results Display has a gap between the name and the champion, while "results" does not so the name detection will work
    return fullResult

def decodeRoflMmrResult(filename):
    dicts = []
    with open('tempgame.rofl', 'r', encoding='latin1') as data:
    
        newdata = data.read().split('{') # Parse data
        for i in range(len(newdata)):
            if len(dicts) != 10: # Check if all players are already in dicts
                dictionary = {}
                replacedData = newdata[i].replace("\\", "").replace('"', "").replace("}", "") # Parse data
                replacedData = replacedData.split(']')[0]
                for m in replacedData.split(","):
                    playerdata = m.split(":")
                    try:
                        dictionary[playerdata[0]] = playerdata[1]
                        continue
                    except:
                        pass
                if "ASSISTS" in list(dictionary.keys()): # Check if dict is PLAYER
                    dicts.append(dictionary)
                else:
                    pass
                # METHODS -------------
                # print(f"{dictionary['NAME']} {dictionary['CHAMPIONS_KILLED']}/{dictionary['NUM_DEATHS']}/{dictionary['ASSISTS']} {dictionary['WIN']}")
                # print(dictionary)
                # print(get_key(dictionary["NAME"]))
                # print(dictionary["NAME"].encode("latin1").decode("utf8"))
                # print(replacedData.split(","))
            else:
                break

    winMMR = []
    loseMMR = []

    with open('database.json', 'r') as dataBase:
        db = json.load(dataBase)


    for i in range(len(dicts)):
        name = dicts[i]['NAME'].encode("latin1").decode("utf8") # Encode/Decode to make ÄÖ letters work
        for m in db["userData"]:
            if name.lower() == db["userData"][m]['summoner'].lower():
                if dicts[i]["WIN"] == "Win":
                    winMMR.append(db["userData"][m]['points'])
                else:
                    loseMMR.append(db["userData"][m]['points'])

    try:
        avgWinMMR = sum(winMMR) / len(winMMR)
    except:
        avgWinMMR = 1000
    try:
        avgLoseMMR = sum(loseMMR) / len(loseMMR)
    except:
        avgLoseMMR = 1000

    result = [avgWinMMR, avgLoseMMR]

    return result

if __name__ == "__main__":
    decodeRoflMmrResult("asdf")