import json


def sortLeaderboard():
    with open('database.json', 'r') as db:
        dicts = json.load(db)
    dictList = []

    for i in dicts['userData']:
        if dicts['userData'][i]['wins'] == 0 and dicts['userData'][i]['losses'] == 0:
            pass
        else:
            dictList.append(dicts["userData"][i])

    newlist = sorted(dictList, key=lambda d: d['points'], reverse=True)
    return newlist
    # for i in newlist:
    #     print(f"{i['summoner']} : {i['points']}")

if __name__ == "__main__":
    sortLeaderboard()