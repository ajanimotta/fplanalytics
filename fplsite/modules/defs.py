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

#GENERATE CSV FOR DEF HOME/AWAY PLOT
def defs_home_away_csv():
    players = fpl_player()
    players_def = players.loc[players['position'] == 'DEF']

    #home--get subsets of GW dataframe and format dataframe accordingly
    gws = get_gws()
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'DEF']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_def_home = players_def[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_def_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'DEF']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_def_away = players_def[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_def_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 4.3:
            return ["darkgreen", "Less than 4.3"]
        elif c < 4.8:
            return ["green", "4.3 to 4.7"]
        elif c < 5.3:
            return ["greenyellow", "4.8 to 5.2"]
        elif c < 5.8:
            return ["gold", "5.3 to 5.7"]
        elif c < 6.3:
            return ["orange", "5.8 to 6.2"]
        elif c < 6.8:
            return ["darkorange", "6.3 to 6.7"]
        elif c < 7.3:
            return ["orangered", "6.8 to 7.2"]
        else: return ["red", "7.3 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    gws_by_player_home.to_csv('csv/defs_home.csv', index = False)
    gws_by_player_away.to_csv('csv/defs_away.csv', index = False)
    return

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#GRAB DEFS DF needed for home/away plot on defs.html
def get_defs_home_away():
    f_home = open('csv/defs_home.csv')
    defs_home = pd.read_csv(f_home)
    f_away = open('csv/defs_away.csv')
    defs_away = pd.read_csv(f_away)
    return [defs_home, defs_away]