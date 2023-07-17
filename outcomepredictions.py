
import numpy as np
import pandas as pd
from io import StringIO
import requests
import unicodedata



teams = ['LAA', 'HOU', 'OAK', 'TOR', 'ATL', 'MIL', 'STL','CHC', 'AZ', 'LAD', 'SF', 'CLE', 'SEA', 'MIA','NYM', 'WSH', 'BAL', 'SD', 'PHI', 'PIT', 'TEX','TB', 'BOS', 'CIN', 'COL', 'KC', 'DET', 'MIN','CWS', 'NYY']

mlbteams = {'Oakland Athletics': 'OAK', 'Pittsburgh Pirates': 'PIT', 'Seattle Mariners': 'SEA', 'San Diego Padres': 'SD', 'Kansas City Royals': 'KC', 'Miami Marlins': 'MIA', 'Minnesota Twins': 'MIN', 'Tampa Bay Rays': 'TB', 'Arizona Diamondbacks': 'AZ', 'Washington Nationals': 'WSH', 'Houston Astros': 'HOU', 'Toronto Blue Jays': 'TOR', 'Boston Red Sox': 'BOS', 'Cleveland Guardians': 'CLE', 'Los Angeles Dodgers': 'LAD', 'Cincinnati Reds': 'CIN', 'New York Mets': 'NYM', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Milwaukee Brewers': 'MIL', 'St. Louis Cardinals': 'STL', 'Texas Rangers': 'TEX', 'San Francisco Giants': 'SF', 'Colorado Rockies': 'COL', 'Chicago Cubs': 'CHC', 'Los Angeles Angels': 'LAA', 'Detroit Tigers': 'DET', 'Philadelphia Phillies': 'PHI', 'Chicago White Sox': 'CWS', 'New York Yankees': 'NYY'}



# use the MLB API to get the full schedule
link = 'https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&startDate=2023-01-01&endDate=2023-12-31'
DF = pd.read_json(link)
# every DF value is a different date DF.values[indx][5]
# then games are DF.values[indx][5]['games']

# DF.values[indx][5]['games'][0].keys()
# DF.values[indx][5]['games'][0]['seriesDescription'] == 'Regular Season'
indx,gnum = 102,0
ngames = len(DF.values[indx][5]['games'])
gamedate =  DF.values[indx][5]['date']
awayteam = DF.values[indx][5]['games'][gnum]['teams']['away']['team']['name']
hometeam = DF.values[indx][5]['games'][gnum]['teams']['home']['team']['name']
print(gamedate,hometeam,'v.',awayteam)

# tuned parameters from first 60 games of the 2023 season
X = [0.49962572,0.05612191]
kernel_size = 10
kernel = np.ones(kernel_size) / kernel_size

linedict = {0.50:'EVS',0.51:'21/20',0.52:'11/10',0.53:'23/20',0.54:'6/5',0.55:'5/4',0.56:'13/10',0.57:'27/20',0.58:'7/5',0.59:'29/20',0.60:'6/4'}

def compute_betline(odds):
    # return fractional bet lines
    roundedodds = np.round(odds,2)
    betstring = ''
    for i in linedict.keys():
        if i>=roundedodds:
            betstring += linedict[i]+' '
    return betstring


today = pd.to_datetime("today").dayofyear - 59
f = open('predictions/{}.csv'.format(str(pd.to_datetime("today").date())),'w')
print('date,hometeamfull,hometeam,hometeamodds,awayteamfull,awayteam,awayteamodds',file=f)
for indx in range(today,today+15):
    ngames = len(DF.values[indx][5]['games'])
    gamedate =  DF.values[indx][5]['date']
    for gnum in range(0,ngames):
        awayteam = DF.values[indx][5]['games'][gnum]['teams']['away']['team']['name']
        hometeam = DF.values[indx][5]['games'][gnum]['teams']['home']['team']['name']
        H = np.genfromtxt('data/teams/{}.csv'.format(mlbteams[hometeam]),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiffI', '<i8'), ('runsscoredI', '<i8')],delimiter=',')
        hrundiff = np.convolve(H['rundiff'], kernel, mode='same')
        A = np.genfromtxt('data/teams/{}.csv'.format(mlbteams[awayteam]),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiffI', '<i8'), ('runsscoredI', '<i8')],delimiter=',')
        arundiff = np.convolve(A['rundiff'], kernel, mode='same')
        rundiffdelta = hrundiff[-1] - arundiff[-1]
        hteamwin = rundiffdelta*X[1]+X[0]
        ateamwin = 1.-hteamwin
        betstring = compute_betline(np.nanmax([hteamwin,ateamwin]))
        print('{0},{1},{2},{3},{4},{5},{6}'.format(gamedate,hometeam,mlbteams[hometeam],np.round(hteamwin,3),awayteam,mlbteams[awayteam],np.round(ateamwin,3),betstring),file=f)
        print('{0}: {1:22s} ({2:4.3f}) v. {3:22s} ({4:4.3f})'.format(gamedate,hometeam,np.round(hteamwin,3),awayteam,np.round(ateamwin,3)))

f.close()
