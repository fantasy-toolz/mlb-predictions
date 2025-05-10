


import numpy as np
import pandas as pd
from io import StringIO
import requests
import unicodedata

indexinning = 6


# this is 2023 season specific
year = '2023'
yeardates = [str(pd.to_datetime(day, unit='D', origin=str(year))).split()[0] for day in range(88,365)]

# this is 2024 season specific
year = '2024'
yeardates = [str(pd.to_datetime(day, unit='D', origin=str(year))).split()[0] for day in range(77,365)]

# this is 2025 season specific
year = '2025'
yeardates = [str(pd.to_datetime(day, unit='D', origin=str(year))).split()[0] for day in range(85,365)]


todaynum = np.where(np.array(yeardates)==str(pd.to_datetime("today").date()))[0][0]

alldates = yeardates[0:todaynum]
print(alldates)

# check just the past couple of days
alldates = yeardates[max(0,todaynum-15):todaynum]


# create a file that stamps the last time run
f = open('data/{}/lasttouched.txt'.format(year),'w')
print(pd.to_datetime("today"),file=f)
f.close()



teams = ['LAA', 'HOU','OAK', 'TOR', 'ATL', 'MIL', 'STL','CHC', 'AZ', 'LAD', 'SF', 'CLE', 'SEA', 'MIA','NYM', 'WSH', 'BAL', 'SD', 'PHI', 'PIT', 'TEX','TB', 'BOS', 'CIN', 'COL', 'KC', 'DET', 'MIN','CWS', 'NYY']

mlbteams = {'Oakland Athletics': 'OAK', 'Pittsburgh Pirates': 'PIT', 'Seattle Mariners': 'SEA', 'San Diego Padres': 'SD', 'Kansas City Royals': 'KC', 'Miami Marlins': 'MIA', 'Minnesota Twins': 'MIN', 'Tampa Bay Rays': 'TB', 'Arizona Diamondbacks': 'AZ', 'Washington Nationals': 'WSH', 'Houston Astros': 'HOU', 'Toronto Blue Jays': 'TOR', 'Boston Red Sox': 'BOS', 'Cleveland Guardians': 'CLE', 'Los Angeles Dodgers': 'LAD', 'Cincinnati Reds': 'CIN', 'New York Mets': 'NYM', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Milwaukee Brewers': 'MIL', 'St. Louis Cardinals': 'STL', 'Texas Rangers': 'TEX', 'San Francisco Giants': 'SF', 'Colorado Rockies': 'COL', 'Chicago Cubs': 'CHC', 'Los Angeles Angels': 'LAA', 'Detroit Tigers': 'DET', 'Philadelphia Phillies': 'PHI', 'Chicago White Sox': 'CWS', 'New York Yankees': 'NYY'}

teams = ['LAA', 'HOU','ATH', 'TOR', 'ATL', 'MIL', 'STL','CHC', 'AZ', 'LAD', 'SF', 'CLE', 'SEA', 'MIA','NYM', 'WSH', 'BAL', 'SD', 'PHI', 'PIT', 'TEX','TB', 'BOS', 'CIN', 'COL', 'KC', 'DET', 'MIN','CWS', 'NYY']

mlbteams = {'Oakland Athletics': 'ATH', 'Pittsburgh Pirates': 'PIT', 'Seattle Mariners': 'SEA', 'San Diego Padres': 'SD', 'Kansas City Royals': 'KC', 'Miami Marlins': 'MIA', 'Minnesota Twins': 'MIN', 'Tampa Bay Rays': 'TB', 'Arizona Diamondbacks': 'AZ', 'Washington Nationals': 'WSH', 'Houston Astros': 'HOU', 'Toronto Blue Jays': 'TOR', 'Boston Red Sox': 'BOS', 'Cleveland Guardians': 'CLE', 'Los Angeles Dodgers': 'LAD', 'Cincinnati Reds': 'CIN', 'New York Mets': 'NYM', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Milwaukee Brewers': 'MIL', 'St. Louis Cardinals': 'STL', 'Texas Rangers': 'TEX', 'San Francisco Giants': 'SF', 'Colorado Rockies': 'COL', 'Chicago Cubs': 'CHC', 'Los Angeles Angels': 'LAA', 'Detroit Tigers': 'DET', 'Philadelphia Phillies': 'PHI', 'Chicago White Sox': 'CWS', 'New York Yankees': 'NYY'}


def get_team_game(year,date,team):
    link = 'https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea='+str(year)+'%7C&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt='+date+'&game_date_lt='+date+'&hfInfield=&team='+team+'&position=&hfOutfield=&hfRO=&home_road=&hfFlag=&hfBBT=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&min_pas=0&type=details&'
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }
    r = requests.get(link, headers=header)
    csvStringIO = StringIO(r.text)
    DF = pd.read_csv(csvStringIO, low_memory=False)
    return DF

def num_games(DF):
    gamenums = np.unique(DF['game_pk'])
    return len(gamenums)


# get redirected pitcher url

#D = get_team_game('2023','2023-07-17','MIN')

#playerid = D.loc[D['inning']==1].loc[D['inning_topbot']=='Top']['pitcher'].values[0]

def get_pitcher_name(D):
    playerid = D.loc[D['inning']==1]['pitcher'].values[0]
    template_url = 'https://baseballsavant.mlb.com/savant-player/{}'.format(playerid)
    response = requests.get(template_url)
    redirect = response.url
    playerstring = redirect.split('/')[-1].split('-')
    player = playerstring[0].capitalize()+' '+playerstring[1].capitalize()
    return player


# data we want
# date, rundiff, runsscored, boxcar10rundiff, opponent, oppboxcar10rundiff, winodds, winloss

# could try something like 'how many runs were scored by the 5th inning?'

for team in teams:
    print(team)
    try:
        try:
            T = np.genfromtxt('data/{}/teams/{}.csv'.format(year,team),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiffI', '<i8'), ('runsscoredI', '<i8'),('pitcher','S20'),('opppitcher','S20')],delimiter=',',skip_header=1)
            f = open('data/{}/teams/{}.csv'.format(year,team),'a')
        except:
            # the file doesn't exist yet!
            f = open('data/{}/teams/{}.csv'.format(year,team),'w')
            print('date,team,opponent,rundifferential,teamruns,rundifferential6,teamruns6,teamstarter,opponentstarter',file=f)
        for date in alldates:
            if date in T['date'].astype('str'):
                continue
            print(date)
            D = get_team_game(year,date,team)
            # are they home or away
            try:
                a = D['home_team'].values[0]
            except:
                continue
            if D['home_team'].values[0] == team: # team in question is home team
                teamscore = np.nanmax(D['post_home_score'].values)
                try:
                    tscoreI   = np.nanmax(D['post_home_score'].loc[D['inning']==indexinning].values)
                except:
                    tscoreI   = 0.0
                opponent  = D['away_team'].values[0]
            else: # team in question is away team
                teamscore = np.nanmax(D['post_away_score'].values)
                try:
                    tscoreI   = np.nanmax(D['post_away_score'].loc[D['inning']==indexinning].values)
                except:
                    tscoreI   = 0.0
                opponent  = D['home_team'].values[0]
            try:
                opppitcher = get_pitcher_name(D)
            except:
                opppitcher = '???'
            # get the opponent's game score
            O = get_team_game(year,date,opponent)
            if D['home_team'].values[0] == team: # team in question is home team
                oppscore  = np.nanmax(O['post_away_score'].values)
                try:
                    oppscoreI = np.nanmax(O['post_away_score'].loc[O['inning']==indexinning].values)
                except:
                    oppscoreI = 0.0
            else:
                oppscore  = np.nanmax(O['post_home_score'].values)
                try:
                    oppscoreI = np.nanmax(O['post_home_score'].loc[O['inning']==indexinning].values)
                except:
                    oppscoreI = 0.0
            try:
                teampitcher = get_pitcher_name(O)
            except:
                teampitcher = '???'
            rundiff   = teamscore - oppscore
            rundiffI  = tscoreI   - oppscoreI
            teamwin   = 0.
            if teamscore>oppscore:
                teamwin = 1.
            print('{},{},{},{},{},{},{},{},{}'.format(date,team,opponent,rundiff,teamscore,rundiffI,tscoreI,teampitcher,opppitcher))
            print('{},{},{},{},{},{},{},{},{}'.format(date,team,opponent,rundiff,teamscore,rundiffI,tscoreI,teampitcher,opppitcher),file=f)
        f.close()
    except:
        pass
