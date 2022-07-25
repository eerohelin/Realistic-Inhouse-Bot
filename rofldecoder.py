import json

def decodeRoflGameResult(filename):
    dicts = []
    with open('tempgame.rofl', 'r', encoding='latin1') as data:
    
        newdata = data.read().split('{')
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

    for i in range(0, 10):
        try:
            if dicts[i]["WIN"] == "Win":
                name = dicts[i]['NAME'].encode("latin1").decode("utf8")
                results["win"].append(f"{name} ({dicts[i]['SKIN']}) {dicts[i]['CHAMPIONS_KILLED']}/{dicts[i]['NUM_DEATHS']}/{dicts[i]['ASSISTS']}")
            else:
                name = dicts[i]['NAME'].encode("latin1").decode("utf8")
                results["lose"].append(f"{name} ({dicts[i]['SKIN']}) {dicts[i]['CHAMPIONS_KILLED']}/{dicts[i]['NUM_DEATHS']}/{dicts[i]['ASSISTS']}")
        except:
            pass

    return results