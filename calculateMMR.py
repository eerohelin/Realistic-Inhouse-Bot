

def calculateMMR(winTeamAVG, loseTeamAVG, K=30, scale=400, acc=0):
    '''calculates MMR using standard ELO system
    https://en.wikipedia.org/wiki/Elo_rating_system
    K -- affects how much elo changes after adjusted for probability of result
    scale -- how large difference means that there is 1/10 chance of winning
    acc -- how many decimals are in the accuracy of the update
    '''
    
    qwin = 10 ** (winTeamAVG / scale)
    qloss = 10 ** (loseTeamAVG / scale)
    winprob = qwin/(qwin+qloss)
    lossprob = 1 - winprob
    lpGain = round(K * winprob, acc)
    lpLoss = round(K * lossprob, acc)
    gain_loss = [lpGain, lpLoss]
    #print(f"WIN Gained: {lpGain}\nLOSE Lost: {lpLoss}")
    return gain_loss
    

if __name__ == "__main__":
    calculateMMR(1000, 1001)
