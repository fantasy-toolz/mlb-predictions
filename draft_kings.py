# -*- coding: utf-8 -*-
"""
Created on Thu May  2 06:07:01 2024

@author: rentz
"""

import requests
import json
from traceback import print_exc
import pandas as pd
from datetime import date

id_dict = {"NHL": "42133", "NFL": "88808", "NBA": "42648", "MLB":"84240"}

class DraftKings:
    def __init__(self, league = "MLB"):
        """
        Initializes a class object
        Include more leagues simply by adding the league with its ID to id_dict above

        :league str: Name of the league, NHL by default
        """
        self.pregame_url = f"https://sportsbook.draftkings.com//sites/US-SB/api/v5/eventgroups/{id_dict[league]}?format=json"
        


    def get_pregame_odds(self) -> list:
        """
        Collects the market odds for the main markets [the ones listed at the league's main url] for the league

        E.g. for the NHL, those are Puck Line, Total and Moneyline

        Returns a list with one object for each game

        :rtype: list
        """
        # List that will contain dicts [one for each game]
        games_list = []

        # Requests the content from DK's API, loops through the different games & collects all the material deemed relevant
        response = requests.get(self.pregame_url).json()
        games = response['eventGroup']['offerCategories'][0]['offerSubcategoryDescriptors'][0]['offerSubcategory']['offers']
        for game in games:
            # List that will contain dicts [one for each market]
            market_list = []
            for market in game:
                try:
                    market_name = market['label']
                    if market_name == "Moneyline":
                        home_team = market['outcomes'][0]['label']
                        away_team = market['outcomes'][1]['label']
                    # List that will contain dicts [one for each outcome]
                    outcome_list = []
                    for outcome in market['outcomes']:
                        try:
                            # if there's a line it should be included in the outcome description
                            line = outcome['line']
                            outcome_label = outcome['label'] + " " + str(line)
                        except:
                            outcome_label = outcome['label']
                        outcome_odds = outcome['oddsDecimal']
                        outcome_list.append({"label": outcome_label, "odds": outcome_odds})
                    market_list.append({"marketName": market_name, "outcomes": outcome_list})
                except:
                    # if there was a problem with a specific market, continue with the next one...
                    # for example odds for totals not available as early as the other markets for NBA
                    # games a few days away
                    print_exc()
                    print()
                    continue
            games_list.append({"game": f"{home_team} v {away_team}", "markets": market_list})

        return games_list
    
    def store_as_json(self, games_list, file_path: str = None):
        """
        Dumps the scraped content into a JSON-file in the same directory

        :rtype: None, simply creates the file and prints a confirmation
        """
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(games_list, file)
            print(f"Content successfully dumped into '{file_path}'")
        else:
            with open('predictions/MLB.json', 'w') as file:
                json.dump(games_list, file)
            print("Content successfully dumped into 'json'")

def convert_n_save(games):          
    pred_df = pd.read_csv("predictions/latest.csv")
    date_string = date.today().strftime("%Y-%m-%d")
    pred_df = pred_df.loc[pred_df['date']==date_string]
    
    team_equiv = {
        'CHI White Sox': 'CWS',
        'LA Angels': 'LAA',
        'CHI Cubs': 'CHC',
        'NY Mets': "NYM",
        'LA Dodgers': 'LAD',
        'NY Yankees': 'NYY'}
    
    rows = []
    for game in games:
        home_team = game['game'].split(" v ")[1]
        away_team = game['game'].split(" v ")[0]
        for outcome in game['markets']:
            if outcome['marketName'] == 'Moneyline':
                for line in outcome['outcomes']:
                    if line['label'] == home_team:
                        home_odds = line['odds']
                    if line['label'] == away_team:
                        away_odds = line['odds']
                        
        if home_team in team_equiv.keys():
            home_team = team_equiv[home_team]
        else:
            home_team = home_team.split(" ")[0]
        if away_team in team_equiv.keys():
            away_team = team_equiv[away_team]
        else:
            away_team = away_team.split(" ")[0]
        home_odds = home_odds/(home_odds + away_odds)
        rows.append([home_team, away_team, 1-home_odds, home_odds])
        
    line_df = pd.DataFrame(rows, columns = ['hometeam', 'awayteam', 'hometeamodds_dk', 'awayteamodds_dk'])
    line_df.to_csv("predictions/dk.csv", index = False)
    
    pred_df = pred_df.merge(line_df, on = ['hometeam', 'awayteam'], how = 'left')

dk = DraftKings(league = "MLB")
games = dk.get_pregame_odds()
# dk.store_as_json(games)
convert_n_save(games)

