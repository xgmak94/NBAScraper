import requests
import re
import timeit
import pandas as pd
import datetime
from bs4 import BeautifulSoup

currDate = datetime.datetime.now()
default_url = "https://www.basketball-reference.com/leagues/NBA_{}.html".format(currDate.year)

baseSite = "https://www.basketball-reference.com"

def getParser(link:str):
    result = requests.get(link)
    parser = BeautifulSoup(result.text,"html.parser")
    return parser

def teamStats():
    parser = getParser(default_url)
    allTeams = parser.findAll("tr", "full_table", limit=30)
    
    standings, teams = ([] for i in range(2))
    wins, losses, winPercentage, gamesBehind = ([] for i in range(4))
    ppg, papg, pointDiff = ([] for i in range(3))
    
    for team in allTeams:
        teamName = team.find("a").text
        teamStanding = re.sub("[^0-9]","",team.find("span", "seed").text)
        teamData = team.findAll("td", "right")
        ##wins,losses,win%,games behind, points per game, points allowed per game, SRS
        teamWins, teamLosses, teamPercentage = int(teamData[0].text), int(teamData[1].text), float(teamData[2].text)
        teamBehind = 0 if teamData[3].text == "—" else teamData[3].text
        teamPPG, teamPAPG = float(teamData[4].text), float(teamData[5].text)
        
        teams.append(teamName)
        standings.append(teamStanding)
        wins.append(teamWins)
        losses.append(teamLosses)
        winPercentage.append(teamPercentage)
        gamesBehind.append(teamBehind)
        ppg.append(teamPPG)
        papg.append(teamPAPG)
        pointDiff.append(teamPPG - teamPAPG)

    data = pd.DataFrame({"Standing":standings,"Team":teams,"Wins":wins,"Losses":losses,"Win%":winPercentage,"GB":gamesBehind,"PPG":ppg,"PAPG":papg,"Diff":pointDiff})
    east = data.iloc[0:15]
    west = data.iloc[15:30]
    west.set_index("Standing", inplace = True)
    east.set_index("Standing", inplace = True)
    return west, east

def getRosterLinks():
    parser = getParser(default_url)
    allTeams = parser.findAll("tr", "full_table", limit=30)
    
    rosterLinks = []
    teamNames = []
    for team in allTeams:
        teamNames.append(team.find("a").text)
        for a in team.findAll("a", href=True):
            rosterLinks.append(baseSite + a["href"])
    return rosterLinks, teamNames

def getTeamRoster(link, teamName):
    playerNumber, playerName, playerPos = ([] for i in range(3))
    playerAge, playerGP, playerMin, playerFG, playerThree, playerFT, playerREB, playerAST, playerSTL, playerBLK, playerPTS = ([] for i in range(11))
    rosterParser = getParser(link)
    roster = rosterParser.find("tbody")
    player = roster.findAll("tr")
    for currPlayer in player:
        playerNumber.append(currPlayer.find("th").text)
        playerName.append(currPlayer.find("a").text)
        playerPos.append(currPlayer.find("td", "center").text)
        playerPage = baseSite + currPlayer.find("a")["href"]
        
        age,gp,minutes,fg,three,ft,reb,ast,stl,blk,pts = getPlayerStats(playerPage)
        playerAge.append(age)
        playerGP.append(gp)
        playerMin.append(minutes)
        playerFG.append(fg)
        playerThree.append(three)
        playerFT.append(ft)
        playerREB.append(reb)
        playerAST.append(ast)
        playerSTL.append(stl)
        playerBLK.append(blk)
        playerPTS.append(pts)
        
    data = pd.DataFrame({"Number":playerNumber, "Age":playerAge, "Name":playerName, "GP":playerGP, "Pos":playerPos, "Min":playerMin, "Points":playerPTS, "Rebounds":playerREB, "Assists":playerAST, "Steals":playerSTL, "Blocks":playerBLK, "FG%":playerFG, "3P%":playerThree})
    data.set_index("Number", inplace = True)
    data.to_csv(teamName +" roster.txt")
    print(data)

def getPlayerStats(link):
    print(link)
    parser = getParser(link)
    allSeasons = parser.findAll("tr", "full_table")
    age, gp, minutes, fg, threePoint, ft, rebounds, assists, steals, blocks, points = ("-" for i in range(11))
    if(len(allSeasons) == 0 or allSeasons[-1].find("th").text != "2019-20"): #if person is unplayed rookie?? or they have not played this season injury(klay,KD)?
        return age, gp, minutes, fg, threePoint, ft, rebounds, assists, steals, blocks, points
    else:
        seasonStats = allSeasons[-1] ##last one is current season
        allStats = seasonStats.findAll("td")
           
        age = int(allStats[0].text) #age
        gp = int(allStats[4].text) #games played
        minutes = float(allStats[6].text) #minutes
        fg = 0.0 if allStats[9].text == "" else float(allStats[9].text) #FG% dont have an entry if no shots
        threePt = 0.0 if allStats[12].text == "" else float(allStats[12].text) #3P% dont have an entry if no shots
        ft = 0.0 if allStats[19].text == "" else float(allStats[19].text) #FT% dont have an entry if no shots
        reb = float(allStats[22].text) #Rebounds
        ast = float(allStats[23].text) #Assists
        stl = float(allStats[24].text) #Steals
        blk = float(allStats[25].text) #Blocks
        pts = float(allStats[28].text) #Points
        return age, gp, minutes, fg, threePt, ft, reb, ast, stl, blk, pts
