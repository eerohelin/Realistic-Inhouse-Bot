

def calculateMMR(winTeamAVG, loseTeamAVG):

    baseNumber = 15

    differenceNum = [winTeamAVG, loseTeamAVG]

    differenceNum.sort(reverse=True) # Get difference between the numbers
    difference = differenceNum[0] - differenceNum[1]

    if winTeamAVG > loseTeamAVG:
        if difference >= 0 and difference <= 29:
            winMultiplier = 0
            loseMultiplier = 0
        elif difference >= 30 and difference <= 59:
            winMultiplier = 1
            loseMultiplier = 2
        elif difference >= 60 and difference <= 79:
            winMultiplier = 2
            loseMultiplier = 3
        elif difference > 80:
            winMultiplier = 3
            loseMultiplier = 4
        
    elif winTeamAVG < loseTeamAVG:
        if difference >= 0 and difference <= 29:
            winMultiplier = 0
            loseMultiplier = 0
        elif difference >= 30 and difference <= 59:
            winMultiplier = 2
            loseMultiplier = 1
        elif difference >= 60 and difference <= 79:
            winMultiplier = 3
            loseMultiplier = 2
        elif difference > 80:
            winMultiplier = 4
            loseMultiplier = 3

    lpGain = baseNumber + winMultiplier
    lpLoss = baseNumber + loseMultiplier
    gain_loss = [lpGain, lpLoss]
    #print(f"WIN Gained: {lpGain}\nLOSE Lost: {lpLoss}")
    return gain_loss
    

if __name__ == "__main__":
    calculateMMR(1000, 1001)