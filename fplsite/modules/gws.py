#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time
from .players import fpl_player

#%%
# BUILD GAMEWEEK DATAFRAME containing info ('name', 'id', 'assists', 'bonus', 'bps', 'clean_sheets', 'fixture', 
# 'goals_conceded', 'goals_scored', 'minutes', 'opponent_team', 'saves', 'team_a_score', 'team_h_score', 
# 'total_points', 'was_home', 'GW', 'web_name', 'position')
def get_gws():
    player_fpl_df = fpl_player()
    f = open("csv/merged_gw.csv", "r")
    gws_df = pd.read_csv(f)
    gws_df = gws_df[['name', 'element', 'assists', 'bonus', 'bps', 'clean_sheets', 'fixture', 'goals_conceded', 'goals_scored', 
    'minutes', 'opponent_team', 'saves', 'team_a_score', 'team_h_score', 'value', 'transfers_balance', 'total_points', 'was_home', 'GW']]

    #Create 'web_name' column by matching ids in player_fpl_df
    gws_df['element'] = gws_df['element'].apply(lambda x: int(x))
    ids = pd.Series(gws_df['element'])
    name_dict = {}
    for i in range(0, len(ids)):
        player_name = player_fpl_df.loc[player_fpl_df['id'] == ids[i]]['web_name'].values
        name_dict[ids[i]] = player_name[0]
    gws_df['web_name'] = gws_df['element'].map(name_dict)

    # Create 'position' column by grabbing row in player_fpl_df with corresponding id
    position_dict = {}
    for i in range(0, len(gws_df)):
        player_id = gws_df.at[i, 'element']
        player_position = player_fpl_df.loc[player_fpl_df['id'] == player_id]['position'].values
        position_dict[player_id] = player_position[0]
    gws_df['position'] = gws_df['element'].map(position_dict)
    
    gws_df = gws_df.rename(columns={"element": "id"})
    return gws_df