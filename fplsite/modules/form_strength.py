#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time
from .gws import get_gws
from .players import fpl_player
from .fixtures_ratings import get_team_ratings

#GENERATE CSV FOR FORM PLOTS
def form_csv(position):
    gws = get_gws()
    players = fpl_player()
    ratings = get_team_ratings()
    ratings = ratings[['GW', 'team', 'team_name','rating_standardized']]
    current_gw = ratings['GW'].max()

    #IN FORM-------------------------------------------------------------------
    GKPs = players.loc[players['position'] == position]
    GKPs = GKPs[['id', 'selected_by_percent']]
    gws_form_GKP = gws.loc[gws['position']== position]
    gws_form_GKP = gws_form_GKP.loc[gws['GW'].isin([current_gw-2, current_gw-1, current_gw]) ]
    gws_form_GKP = gws_form_GKP[['id', 'web_name', 'GW', 'position', 'minutes', 'opponent_team', 'total_points', 'was_home']]
    gws_form_GKP = pd.merge(GKPs, gws_form_GKP, on='id', how = 'right')
    gws_form_GKP = gws_form_GKP.dropna()
    form_player_avgs = gws_form_GKP.groupby('web_name')['minutes','total_points', 'selected_by_percent'].mean()
    if position == 'GKP':
        top20_form = form_player_avgs.nlargest(5, 'total_points')
    elif position in ['DEF', 'MID']:
        top20_form = form_player_avgs.nlargest(20, 'total_points')
    else:
        top20_form = form_player_avgs.nlargest(15, 'total_points')
    top20_form = top20_form.reset_index()

    #OUT OF FORM-------------------------------------------------------------------
    form_player_avgs = form_player_avgs.loc[form_player_avgs['selected_by_percent'] > 1.5]
    form_player_avgs = form_player_avgs.loc[form_player_avgs['minutes'] > 45]
    if position == 'GKP':
        bot20_form = form_player_avgs.nsmallest(5, 'total_points')
    elif position in ['DEF', 'MID']:
        bot20_form = form_player_avgs.nsmallest(20, 'total_points')
    else:
        bot20_form = form_player_avgs.nsmallest(15, 'total_points')
    bot20_form = bot20_form.reset_index()

    top20_form.to_csv('csv/%s_in_form.csv' % position, index = False)
    bot20_form.to_csv('csv/%s_out_form.csv' % position, index = False)
    return

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#GRAB DF needed for form plot on gkps/defs/mids/fwds.html
def get_form(position):
    f_in = open('csv/%s_in_form.csv' % position)
    in_form = pd.read_csv(f_in)
    f_out = open('csv/%s_out_form.csv' % position)
    out_form = pd.read_csv(f_out)

    return [in_form, out_form]

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

def strong_weak_csv(position):
    #STRONG-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    gws = get_gws()
    ratings = get_team_ratings()
    ratings = ratings[['GW', 'team', 'team_name','rating_standardized']]
    current_gw = ratings['GW'].max()
    gws_ratings = gws.loc[gws['GW'] < current_gw]
    gws_ratings = gws_ratings[['id', 'web_name', 'GW', 'position', 'minutes', 'opponent_team', 'total_points', 'was_home']]
    gws_ratings = pd.merge(ratings, gws_ratings, left_on = ['team', 'GW'], right_on=['opponent_team', 'GW'], how = 'right')
    gws_ratings = gws_ratings.rename(columns={"team_name": "opponent_name", "rating_standardized": "opp_rating"})
    gws_ratings = gws_ratings.drop(columns = ['team']) 
    gws_strong_def = gws_ratings.loc[gws_ratings['position']== position]
    gws_strong_def = gws_strong_def.loc[gws_strong_def['opp_rating'] > 0.5]
    gws_strong_def = gws_strong_def.loc[gws_strong_def['minutes'] > 0]
    strong_player_avgs = gws_strong_def.groupby("web_name")["id"].count().reset_index(name="games")
    strong_player_avgs = pd.merge(strong_player_avgs, gws_strong_def, on = 'web_name', how = 'left')
    strong_player_avgs = strong_player_avgs.groupby('web_name')['total_points', 'minutes', 'games'].mean()

    #WEAK-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    gws_weak_def = gws_ratings.loc[gws_ratings['position']== position]
    gws_weak_def = gws_weak_def.loc[gws_weak_def['opp_rating'] < -0.5]
    gws_weak_def = gws_weak_def.loc[gws_weak_def['minutes'] > 0]
    weak_player_avgs = gws_weak_def.groupby("web_name")["id"].count().reset_index(name="games")
    weak_player_avgs = pd.merge(weak_player_avgs, gws_weak_def, on = 'web_name', how = 'left')
    weak_player_avgs = weak_player_avgs.groupby('web_name')['total_points', 'minutes', 'games'].mean()
    if position == 'GKP':
        top20_strong = strong_player_avgs.nlargest(10, 'total_points')
        top20_weak = weak_player_avgs.nlargest(10, 'total_points')
    elif position in ['DEF', 'MID']:
        top20_strong = strong_player_avgs.nlargest(20, 'total_points')
        top20_weak = weak_player_avgs.nlargest(20, 'total_points')
    else:
        top20_strong = strong_player_avgs.nlargest(15, 'total_points')
        top20_weak = weak_player_avgs.nlargest(15, 'total_points')
    top20_strong = top20_strong.reset_index()
    top20_weak = top20_weak.reset_index()

    top20_strong.to_csv('csv/%s_strong.csv' % position, index = False)
    top20_weak.to_csv('csv/%s_weak.csv' % position, index = False)
    return

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#GRAB DF needed for strong/weak plot on gkps/defs/mids/fwds.html
def get_strong_weak(position):
    f_strong = open('csv/%s_strong.csv' % position)
    strong = pd.read_csv(f_strong)
    f_weak = open('csv/%s_weak.csv' % position)
    weak = pd.read_csv(f_weak)
    return [strong, weak]