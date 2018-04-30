import re
import json
import os
import requests
import toyplot
import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def FA_split(string):
    """Split a string of first ascentionist names by common separators"""
    split = re.split(', |: | and |, and | & |-| - |- |\(', string)
    
    return(split)

def FA_clean(FAlist):
    """Clean a list of first ascentionists to remove dates and first free ascents"""
    # find first list element containing a digit
    for i in range(len(FAlist)):
        if bool(re.search(r'\d', FAlist[i])):
            # if it is first element, ignore it
            if i == 0:
               pass
                
            # if it is not first element, check if first char is number
            else:
                # if first char, remove that element and all elements after
                if FAlist[i][0].isdigit():
                    newlist = FAlist[:i]
                    break
                
                # if not first char, split and remove digits and all elements after
                else:
                    #print('digit not in char 0 - split and remove digits and later elements')
                    newlist = FAlist[:i + 1]
                    for j in range(len(FAlist[i])):
                        if FAlist[i][j].isdigit():
                            newlist[i] = FAlist[i][:j-1]
                            break
                    break
        else:
            newlist = FAlist

    return(newlist)

## use Mountain Project API to get info from 500 routes near El Capitan

# base URL for Mountain Project API
baseurl = 'https://www.mountainproject.com/data/get-routes-for-lat-lon?'
userKey = None  # your personal key goes here

# latitude and longitude for El Capitan in Yosemite
lat = '37.732'
lon = '-119.638'

url = baseurl + 'lat=' + lat + '&lon=' + lon + '&maxDistance=1&maxResults=500&key=' + userKey

# request info for for all routes on El Capitan
response = requests.get(url)
rdict = response.json()

## filter results to only include climbs that are actually on El Capitan

# convert to pandas df
df = pd.DataFrame(rdict['routes'])

# filter results to only include climbs on El Capitan
def ElCap(x):
    return 'El Capitan' in x

climbs = df.loc[df['location'].apply(ElCap)]

## use BeautifulSoup to get FA info from all climbs

# data frame to hold all climbs and first ascentionists
zero_data = np.zeros(shape=(len(climbs), 2))
firsts = pd.DataFrame(zero_data, columns=['name', 'FA'])

len(firsts)

# iterate through climbs and record FAs
for i in range(len(firsts)):
    # get unique page for climb
    url = climbs.url.iloc[i]
    response = requests.get(url)
    
    # use BeautifulSoup to find FA field in HTML
    soup = BeautifulSoup(response.text, "html5lib")
    
    details = soup.find_all("table", {"class", "description-details"})    

    for detail in details:
        tdtag = detail.find('tbody')
    
    FAs = tdtag.contents[2].contents[3].contents[0].strip()
    
    # set name and FA in firsts df
    firsts.name.loc[i] = climbs.name.iloc[i]
    firsts.FA.loc[i] = FA_split(FAs)
    
clean = firsts.FA.apply(FA_clean)

# fix errors missed by FA_clean
clean[0] =  ['Warren Harding', 'Wayne Merry', 'George Whitmore']
clean[3] =  ['Frank Sacherer', 'Mike Sherrick']
clean[4] =  ['Allen Steck', 'Will Siri', 'Dick Long', 'Willi Unsoeld']
clean[5] =  ['Royal Robbins', 'Chuck Pratt', 'Tom Frost ']
clean[6] =  ['Dave Bircheff', 'Phil Bircheff', 'Jim Pettigrew']
clean[7] =  ['Herb Swedlund', 'Penny Carr']
clean[9] =  ['TM Herbert', 'Steve Roper']
clean[10] = ['Jack Turner', 'Royal Robbins']
clean[12] = ['Bob Kamps', 'Galen Rowell', 'Dan Doody', 'Wally Upton']
clean[14] = ['TM Herbert', 'Royal Robbins']
clean[16] = ['Alexander Huber', 'Thomas Huber']
clean[18] = ['Gary Bocarde', 'Charlie Porter']
clean[19] = ['Jim Bridwell', 'Kim Schmitz']
clean[21] = ['Charlie Porter', 'John-Paul de St. Croix']
clean[22] = ['Dale Bard']
clean[23] = ['Tobin Sorenson', 'John Bachar']
clean[24] = ['Alexander Huber', 'Max Reichel']
clean[25] = ['Royal Robbins', 'Yvon Chouinard', 'Chuck Pratt', 'Tom Frost']
clean[27] = ['Mason Earle', 'Brad Gobright']
clean[28] = ['Hugh Burton', 'Steve Sutton']
clean[29] = ['Walter Rosenthal', 'Tom Carter', 'Alan Bard']
clean[30] = ['Charlie Row', 'Bill Price', 'Guy Thompson']
clean[34] = ['Jacek Czyz']
clean[37] = ['Mead Hargis', 'Kim Schmitz']
clean[39] = ['Rick Lovelace']
clean[40] = ['Bruce Hawkins', 'Mark Chapman']
clean[43] = ['Bob Kamps', 'Jim Sims']
clean[46] = ['Tommy Caldwell', 'Kevin Jorgeson']
clean[47] = ['Yvon Chouinard', 'TM Herbert']
clean[48] = ['Joe Kelsey', 'Roman Laba', 'John Hudson']
clean[49] = ['Jim Beyer']
clean[50] = ['Chuck Pratt', 'Royal Robbins']
clean[53] = ['Mark Corbett', 'Gary Edmondson', 'Rich Albuschkat']

firsts.FA = clean

## bar graph of climbs by first ascentionists on El Capitan

# create array of counts for each climber
climbers = []

for i in range(len(clean)):
    climbers = climbers + clean.loc[i]

arr = np.unique(climbers, return_counts=True)
arr = np.core.records.fromarrays(arr)

counts = np.sort(arr, order='f1')[::-1]
counts[:25]

# plot all climbers with more than one first ascent; names on hover
canvas = toyplot.Canvas(700, 500)
axis = canvas.cartesian()
axis.bars(range(24), counts.f1[:24], title=counts.f0[:24]);