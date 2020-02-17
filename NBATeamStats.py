import requests
import re
import timeit
import pandas as pd
import datetime
import NBAScraper

currDate = datetime.datetime.now()
default_url = "https://www.basketball-reference.com/leagues/NBA_{}.html".format(currDate.year)

def main():
    westStats, eastStats = NBAScraper.teamStats()
    westStats.to_csv("West Standings " + currDate.strftime("%b %d %Y") + ".csv")
    eastStats.to_csv("East Standings " + currDate.strftime("%b %d %Y") + ".csv")

    rosterLinks, teamNames = NBAScraper.getRosterLinks()
    for i in range(0, 30):
        NBAScraper.getTeamRoster(rosterLinks[i], teamNames[i])
    
if __name__ == "__main__":
    main()
