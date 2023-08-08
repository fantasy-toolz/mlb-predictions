


import numpy as np
import pandas as pd
from io import StringIO
import requests
import unicodedata
import os


import matplotlib.pyplot as plt
import matplotlib.cm as cm
plt.ion()


teams = ['LAA', 'HOU', 'OAK', 'TOR', 'ATL', 'MIL', 'STL','CHC', 'AZ', 'LAD', 'SF', 'CLE', 'SEA', 'MIA','NYM', 'WSH', 'BAL', 'SD', 'PHI', 'PIT', 'TEX','TB', 'BOS', 'CIN', 'COL', 'KC', 'DET', 'MIN','CWS', 'NYY']

mlbteams = {'Oakland Athletics': 'OAK', 'Pittsburgh Pirates': 'PIT', 'Seattle Mariners': 'SEA', 'San Diego Padres': 'SD', 'Kansas City Royals': 'KC', 'Miami Marlins': 'MIA', 'Minnesota Twins': 'MIN', 'Tampa Bay Rays': 'TB', 'Arizona Diamondbacks': 'AZ', 'Washington Nationals': 'WSH', 'Houston Astros': 'HOU', 'Toronto Blue Jays': 'TOR', 'Boston Red Sox': 'BOS', 'Cleveland Guardians': 'CLE', 'Los Angeles Dodgers': 'LAD', 'Cincinnati Reds': 'CIN', 'New York Mets': 'NYM', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Milwaukee Brewers': 'MIL', 'St. Louis Cardinals': 'STL', 'Texas Rangers': 'TEX', 'San Francisco Giants': 'SF', 'Colorado Rockies': 'COL', 'Chicago Cubs': 'CHC', 'Los Angeles Angels': 'LAA', 'Detroit Tigers': 'DET', 'Philadelphia Phillies': 'PHI', 'Chicago White Sox': 'CWS', 'New York Yankees': 'NYY'}

rotation_size = 5

g = open('rotations/nextup.csv','w')
print('team,nextup,ondeck',file=g)

for team in teams:
    #try:
    #    f = open('rotations/teams/{}.csv'.format(team),'a')
    #except:
    f = open('rotations/teams/{}.csv'.format(team),'w')
    print('cycle,ace,no2,no3,no4,no5,',file=f)
    T = np.genfromtxt('data/teams/{}.csv'.format(team),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiffI', '<i8'), ('runsscoredI', '<i8'),('pitcher','S20'),('opppitcher','S20')],delimiter=',')

    ngames = len(T['pitcher'])
    ncycles = int(np.ceil(ngames/rotation_size))
    rotation_order = np.empty([ncycles,5],dtype='S30')

    for n in range(0,ngames):
        norder = n % rotation_size
        ncycle = int(np.floor(n / rotation_size))
        #ncycle =
        #print(norder,ncycle)
        if norder==0:
            print(ncycle,end=',',file=f)
        print(T['pitcher'][n].decode(),end=',',file=f)
        if norder==rotation_size-1:
            print('',file=f)

        rotation_order[ncycle,norder] = T['pitcher'][n]

    # finish the last line:
    for nf in range(norder+1,5):
        print('',end=',',file=f)

    #print(team,T['pitcher'][0],ncycles)
    #print(rotation_order)
    f.close()

    # to find the next up, take the pitcher from the most recent game, scroll back, and see who followed them
    most_recent_pitcher = T['pitcher'][n]
    print(most_recent_pitcher)
    n -= 1
    while T['pitcher'][n] != most_recent_pitcher:
        n -= 1
        #print(T['pitcher'][n])
    #print(T['pitcher'][n],most_recent_pitcher)
    #print(T['pitcher'][n+1])
    print('{},{},{}'.format(team,T['pitcher'][n+1].decode(),T['pitcher'][n+2].decode()),file=g)


g.close()
