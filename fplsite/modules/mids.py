#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time
from .players import fpl_player
from .gws import get_gws

#GENERATE CSV FOR MID HOME/AWAY PLOT
def mids_home_away_csv():
    players = fpl_player()
    players_mid = players.loc[players['position'] == 'MID']

    #home--get subsets of GW dataframe and format dataframe accordingly
    gws = get_gws()
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'MID']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_mid_home = players_mid[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_mid_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'MID']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_mid_away = players_mid[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_mid_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 5.0:
            return ["darkgreen", "Less than 5.0"]
        elif c <6.0:
            return ["green", "5.0 to 5.9"]
        elif c < 7.0:
            return ["lime", "6.0 to 6.9"]
        elif c < 8.0:
            return ["greenyellow", "7.0 to 7.9"]
        elif c < 9.0:
            return ["gold", "8.0 to 8.9"]
        elif c < 10.0:
            return ["orange", "9.0 to 9.9"]
        elif c < 11.0:
            return ["darkorange", "10.0 to 10.9"]
        elif c < 12.0:
            return ["orangered", "11.0 to 11.9"]
        else: return ["red", "12.0 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    gws_by_player_home.to_csv('csv/mids_home.csv', index = False)
    gws_by_player_away.to_csv('csv/mids_away.csv', index = False)
    return

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#GRAB MIDS DF needed for home/away plot on mids.html
def get_mids_home_away():
    f_home = open('csv/mids_home.csv')
    mids_home = pd.read_csv(f_home)
    f_away = open('csv/mids_away.csv')
    mids_away = pd.read_csv(f_away)
    return [mids_home, mids_away]