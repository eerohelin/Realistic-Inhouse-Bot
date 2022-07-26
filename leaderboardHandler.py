
dicts = {
    "pastGames": [

    ],
    "userData": {
        "152433069222002688": {
            "summoner": "h0laa",
            "wins": 3,
            "losses": 1,
            "points": 900
        },
        "152433069222002686": {
            "summoner": "raiki",
            "wins": 1,
            "losses": 0,
            "points": 1002
        },
        "15243306922200268655": {
            "summoner": "krisu",
            "wins": 12,
            "losses": 4,
            "points": 1060
        },
        "1524330692220026421655": {
            "summoner": "jaani",
            "wins": 12,
            "losses": 4,
            "points": 1030
        },
        "15243306922206421655": {
            "summoner": "faker",
            "wins": 12,
            "losses": 4,
            "points": 980
        },
        "152433022206421655": {
            "summoner": "zeekkis",
            "wins": 12,
            "losses": 4,
            "points": 910
        },
        "15243302220642221655": {
            "summoner": "miika",
            "wins": 12,
            "losses": 4,
            "points": 965
        },
        "152433022206422212655": {
            "summoner": "akseli",
            "wins": 12,
            "losses": 4,
            "points": 965
        },
        "15243302220642122212655": {
            "summoner": "arlet",
            "wins": 12,
            "losses": 4,
            "points": 1265
        },
        "152433022206421212212655": {
            "summoner": "jankos",
            "wins": 12,
            "losses": 4,
            "points": 12625
        },
        "1524330692220026864214": {
            "summoner": "aapo",
            "wins": 3,
            "losses": 2,
            "points": 1005
        }
    }
}

def sortLeaderboard():
    dictList = []

    for i in dicts['userData']:
        dictList.append(dicts["userData"][i])

    newlist = sorted(dictList, key=lambda d: d['points'], reverse=True)
    return newlist
    for i in newlist:
        print(f"{i['summoner']} : {i['points']}")

if __name__ == "__main__":
    sortLeaderboard()