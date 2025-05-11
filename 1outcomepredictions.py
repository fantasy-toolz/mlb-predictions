
import numpy as np
import pandas as pd
from io import StringIO
import requests
import unicodedata
import os
import shutil

teams = ['LAA', 'HOU', 'OAK', 'TOR', 'ATL', 'MIL', 'STL','CHC', 'AZ', 'LAD', 'SF', 'CLE', 'SEA', 'MIA','NYM', 'WSH', 'BAL', 'SD', 'PHI', 'PIT', 'TEX','TB', 'BOS', 'CIN', 'COL', 'KC', 'DET', 'MIN','CWS', 'NYY']
teams = ['LAA', 'HOU', 'ATH', 'TOR', 'ATL', 'MIL', 'STL','CHC', 'AZ', 'LAD', 'SF', 'CLE', 'SEA', 'MIA','NYM', 'WSH', 'BAL', 'SD', 'PHI', 'PIT', 'TEX','TB', 'BOS', 'CIN', 'COL', 'KC', 'DET', 'MIN','CWS', 'NYY']

mlbteams = {'Oakland Athletics': 'OAK', 'Pittsburgh Pirates': 'PIT', 'Seattle Mariners': 'SEA', 'San Diego Padres': 'SD', 'Kansas City Royals': 'KC', 'Miami Marlins': 'MIA', 'Minnesota Twins': 'MIN', 'Tampa Bay Rays': 'TB', 'Arizona Diamondbacks': 'AZ', 'Washington Nationals': 'WSH', 'Houston Astros': 'HOU', 'Toronto Blue Jays': 'TOR', 'Boston Red Sox': 'BOS', 'Cleveland Guardians': 'CLE', 'Los Angeles Dodgers': 'LAD', 'Cincinnati Reds': 'CIN', 'New York Mets': 'NYM', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Milwaukee Brewers': 'MIL', 'St. Louis Cardinals': 'STL', 'Texas Rangers': 'TEX', 'San Francisco Giants': 'SF', 'Colorado Rockies': 'COL', 'Chicago Cubs': 'CHC', 'Los Angeles Angels': 'LAA', 'Detroit Tigers': 'DET', 'Philadelphia Phillies': 'PHI', 'Chicago White Sox': 'CWS', 'New York Yankees': 'NYY'}
mlbteams = {'Athletics': 'ATH', 'Pittsburgh Pirates': 'PIT', 'Seattle Mariners': 'SEA', 'San Diego Padres': 'SD', 'Kansas City Royals': 'KC', 'Miami Marlins': 'MIA', 'Minnesota Twins': 'MIN', 'Tampa Bay Rays': 'TB', 'Arizona Diamondbacks': 'AZ', 'Washington Nationals': 'WSH', 'Houston Astros': 'HOU', 'Toronto Blue Jays': 'TOR', 'Boston Red Sox': 'BOS', 'Cleveland Guardians': 'CLE', 'Los Angeles Dodgers': 'LAD', 'Cincinnati Reds': 'CIN', 'New York Mets': 'NYM', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Milwaukee Brewers': 'MIL', 'St. Louis Cardinals': 'STL', 'Texas Rangers': 'TEX', 'San Francisco Giants': 'SF', 'Colorado Rockies': 'COL', 'Chicago Cubs': 'CHC', 'Los Angeles Angels': 'LAA', 'Detroit Tigers': 'DET', 'Philadelphia Phillies': 'PHI', 'Chicago White Sox': 'CWS', 'New York Yankees': 'NYY'}

year = '2025'

# use the MLB API to get the full schedule
link = f'https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&startDate={year}-01-01&endDate={year}-12-31'
DF = pd.read_json(link)
# every DF value is a different date DF.values[indx][5]
# then games are DF.values[indx][5]['games']

# this is a decoder explanation
# DF.values[indx][5]['games'][0].keys()
# DF.values[indx][5]['games'][0]['seriesDescription'] == 'Regular Season'
indx,gnum = 27,0
ngames = len(DF.values[indx][5]['games'])
gamedate =  DF.values[indx][5]['date']
awayteam = DF.values[indx][5]['games'][gnum]['teams']['away']['team']['name']
hometeam = DF.values[indx][5]['games'][gnum]['teams']['home']['team']['name']
print(gamedate,hometeam,'v.',awayteam)

# tuned parameters from first 60 games of the 2023 season
X = [0.49962572,0.05612191]

# set the smoothing kernel size.
# in this case, we are using a boxcar of 10 games
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



# move the latest files to an archive file
try:
    P = pd.read_csv('predictions/latest.csv')
    zerodate = P['date'][0]
    os.rename('predictions/latest.csv',f'predictions/archive/{year}/{zerodate}.csv')
    Q = pd.read_csv('predictions/latestvalidation.csv')
    os.rename('predictions/latestvalidation.csv',f'predictions/archive/{year}/{zerodate}validation.csv')
except:
    pass

# open the new file for writing
f = open('predictions/latest.csv','w')
g = open('predictions/latestvalidation.csv','w')

# stamp the output file with the header
print('date,hometeamfull,hometeam,hometeamodds,awayteamfull,awayteam,awayteamodds,meanrundiff,homerollingdiff,homerollingruns,awayrollingruns',file=f)
print('date,hometeamfull,hometeamwin,hometeamscore,hometeamodds,awayteamfull,awayteamwin,awayteamscore,awayteamodds',file=g)

# start the calculation of gamedays, going two weeks forward
# the 59 is determined by hand, sadly. please automate!
today = pd.to_datetime("today").dayofyear - 59
today = pd.to_datetime("today").dayofyear - 54 # 2024
today = pd.to_datetime("today").dayofyear - 52 # 2025
yesterday = today - 1

doyesterday = True
if doyesterday:
    # check yesterdays scores
    gamedate =  DF.values[yesterday][5]['date']
    ngames = len(DF.values[yesterday][5]['games'])
    P = pd.read_csv(f'predictions/archive/{year}/{gamedate}.csv')
    Y = P.loc[P['date']==gamedate]

    for gnum in range(0,ngames):
        try:
            awayteam = DF.values[yesterday][5]['games'][gnum]['teams']['away']['team']['name']
            dYA = Y.loc[(Y['awayteamfull']==DF.values[yesterday][5]['games'][gnum]['teams']['away']['team']['name'])]
            awayteamprob = dYA['awayteamodds'].values[0]
            awayteamwin = DF.values[yesterday][5]['games'][gnum]['teams']['away']['isWinner']
            awayteamscore = DF.values[yesterday][5]['games'][gnum]['teams']['away']['score']
            hometeam = DF.values[yesterday][5]['games'][gnum]['teams']['home']['team']['name']
            dYH = Y.loc[(Y['hometeamfull']==DF.values[yesterday][5]['games'][gnum]['teams']['home']['team']['name'])]
            hometeamprob = dYH['hometeamodds'].values[0]
            hometeamwin = DF.values[yesterday][5]['games'][gnum]['teams']['home']['isWinner']
            hometeamscore = DF.values[yesterday][5]['games'][gnum]['teams']['home']['score']
        # now print to file
            print('{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(gamedate,hometeam,hometeamwin,hometeamscore,dYH['hometeamodds'].values[0],awayteam,awayteamwin,awayteamscore,dYA['awayteamodds'].values[0]),file=g)
        except:
            print('Failed on')
            print(DF.values[yesterday][5]['games'][gnum]['teams']['away']['team']['name'],DF.values[yesterday][5]['games'][gnum]['teams']['home']['team']['name'])

    g.close()

# need a maximum day (i.e. last day of season)
# failed at 217
maxday = 216 # this is the last day of the season (with the -59 applied)

for indx in range(today,np.nanmin([today+7,maxday])):
    ngames = len(DF.values[indx][5]['games'])
    gamedate =  DF.values[indx][5]['date']
    for gnum in range(0,ngames):
        awayteam = DF.values[indx][5]['games'][gnum]['teams']['away']['team']['name']
        hometeam = DF.values[indx][5]['games'][gnum]['teams']['home']['team']['name']
        try:
            H = np.genfromtxt('data/{}/teams/{}.csv'.format(year,mlbteams[hometeam]),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiffI', '<i8'), ('runsscoredI', '<i8'),('pitcher','S20'),('opppitcher','S20')],delimiter=',')
        except:
            print("outcomepredictions.py: unexpected team name: {}".format(hometeam))
            continue
            # example cases running into this would be things like the All Star game.

        # smooth the home team's run differential
        hrundiff = np.convolve(H['rundiff'], kernel, mode='same')
        hrunscored = np.convolve(H['runsscored'], kernel, mode='same')
        A = np.genfromtxt('data/{}/teams/{}.csv'.format(year,mlbteams[awayteam]),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiffI', '<i8'), ('runsscoredI', '<i8'),('pitcher','S20'),('opppitcher','S20')],delimiter=',')
        
        # smooth the opponent's run differential
        arundiff = np.convolve(A['rundiff'], kernel, mode='same')
        arunscored = np.convolve(A['runsscored'], kernel, mode='same')

        # compute the run differential differential
        rundiffdelta = hrundiff[-1] - arundiff[-1]

        meanrundiff = 0.5*(hrundiff[-1] + arundiff[-1])

        # compute the winning probabiligies
        hteamwin = rundiffdelta*X[1]+X[0]
        ateamwin = 1.-hteamwin

        betstring = compute_betline(np.nanmax([hteamwin,ateamwin]))

        # print to file
        print('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}'.format(gamedate,hometeam,mlbteams[hometeam],np.round(hteamwin,3),awayteam,mlbteams[awayteam],np.round(ateamwin,3),np.round(meanrundiff,2),np.round(hrundiff[-1],3),np.round(hrunscored[-1],3),np.round(arunscored[-1],3)),file=f)
        print('{0}: {1:22s} ({2:4.3f}) v. {3:22s} ({4:4.3f})'.format(gamedate,hometeam,np.round(hteamwin,3),awayteam,np.round(ateamwin,3)))

f.close()
