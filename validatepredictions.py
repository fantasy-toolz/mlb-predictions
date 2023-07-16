


import numpy as np
import pandas as pd
from io import StringIO
import requests
import unicodedata


import matplotlib.pyplot as plt
import matplotlib.cm as cm
plt.ion()



# tuned parameters from first 60 games of the 2023 season
X = [0.49962572,0.05612191]
kernel_size = 10
kernel = np.ones(kernel_size) / kernel_size

# bins in meanrundiff go from -3,3
rdmin,rdmax = -6.,6.
#rdmin,rdmax = -4.,4.

nrd = 20
drd = (rdmax-rdmin)/nrd
rundiffrange = np.linspace(rdmin,rdmax,nrd)
winperc = np.zeros([rundiffrange.size,2])

for team in teams:
    T = np.genfromtxt('data/teams/{}.csv'.format(team),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiff5', '<i8'), ('runsscored5', '<i8')],delimiter=',')
    boxcar10rundiff = np.convolve(T['rundiff'], kernel, mode='same')
    for indx,date in enumerate(T['date']):
        if indx < 70:
            continue
        opp = T['opponent'][indx]
        #print(opp)
        try:
            O = np.genfromtxt('data/teams/{}.csv'.format(opp.decode()),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiff5', '<i8'), ('runsscored5', '<i8')],delimiter=',')
            oboxcar10rundiff = np.convolve(O['rundiff'], kernel, mode='same')
            oindx = np.where(O['date']==date)
        except:
            continue
        rundiffdelta = boxcar10rundiff[indx] - oboxcar10rundiff[oindx][0]
        print(date,team,opp,boxcar10rundiff[indx],oboxcar10rundiff[oindx][0],rundiffdelta*X[1]+X[0],T['rundiff'][indx]>0)
        bin1 = int(np.floor((rundiffdelta-rdmin)/drd)) # boxcar bin
        if bin1>=nrd: bin1=nrd-1
        if bin1<0: bin1=0
        if T['rundiff'][indx]>0:
            winperc[bin1,0] += 1.0
        winperc[bin1,1] += 1.0



plt.scatter(rundiffrange,winperc[:,0]/winperc[:,1],color='black',marker='.')

for b in range(0,rundiffrange.size):
    med = winperc[b,0]/winperc[b,1]
    diff = np.sqrt(winperc[b,0])/winperc[b,1]
    plt.plot([rundiffrange[b],rundiffrange[b]],[med-diff,med+diff],color='black',lw=1.)

plt.xlabel('run differential differential')
#plt.xlabel('runs scored differential')
plt.ylabel('win probability')

plt.plot(rundiffrange,rundiffrange*X[1]+X[0],color='red')

print(X)


plt.plot([rdmin,rdmax],[0.5,0.5],color='grey',lw=0.5,linestyle='dashed',zorder=-10)
plt.plot([0.,0.],[0.,1.],color='grey',lw=0.5,linestyle='dashed',zorder=-10)

plt.axis([rdmin,rdmax,0.,1.])

plt.savefig('figures/rundifferentialcheck.png',dpi=300)



boxcar10rundiff = np.convolve(T['rundiff'], kernel, mode='same')

boxcar10rundiff5 = np.convolve(T['rundiff5'], kernel, mode='same')


wins = int(np.nansum(np.ones(T['rundiff'].size)[G['rundiff']>0]))
loss = int(np.nansum(np.ones(T['rundiff'].size)[G['rundiff']<0]))


# who has big leads after 5 innings typically?
for team in teams:
    try:
        T = np.genfromtxt('data/teams/{}.csv'.format(team),dtype=[('date', 'S10'), ('team', 'S3'), ('opponent', 'S3'), ('rundiff', '<i8'), ('runsscored', '<i8'), ('rundiff5', '<i8'), ('runsscored5', '<i8')],delimiter=',')
    except:
        continue
    earlygameleads = np.nanmean(T['rundiff5']) # early game leads
    lategameleads  = np.nanmean(T['rundiff'])  # final scores
    print('{0:4s} {1:6.3f} {2:6.3f} {3:6.3f}'.format(team,np.round(earlygameleads*9./5.,3),np.round(lategameleads,3),np.round(lategameleads-(earlygameleads*9./5.),3)))
