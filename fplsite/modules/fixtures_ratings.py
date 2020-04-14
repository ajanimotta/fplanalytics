#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time

#%%
# BUILD FIXTURE DATAFRAME containing info ('event', 'id', 'stats', 'team_a', 'team_a_difficulty', 'team_a_score', 'team_h', 
# 'team_h_difficulty', 'team_h_score')
def get_fixtures():
    f = open("csv/fixtures.csv", "r")
    fixtures_df = pd.read_csv(f)
    abbr_dict = {
        1: "ARS", 2: "AVL", 3: "BOU", 4: "BHA",
        5: "BUR", 6: "CHE", 7: "CRY", 8: "EVE",
        9: "LEI", 10: "LIV", 11: "MCI", 12: "MUN",
        13: "NEW", 14: "NOR", 15: "SHU", 16: "SOU",
        17: "TOT", 18: "WAT", 19: "WHU", 20: "WOL" 
    }
    fixtures_df = fixtures_df[['event', 'finished', 'id', 'stats', 'team_h', 'team_h_difficulty', 'team_h_score',
    'team_a', 'team_a_difficulty', 'team_a_score']]
    fixtures_df['home_team_name'] = fixtures_df['team_h'].map(abbr_dict)
    fixtures_df['away_team_name'] = fixtures_df['team_a'].map(abbr_dict)
    return fixtures_df


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

# Add team rating to fixture dataframe to assess strength of teams throughout season
def team_rating(fixtures):
    temp_df = fixtures.loc[fixtures['finished'] == True]
    team_rating_df = pd.DataFrame()
    for row in temp_df.iterrows():
        row = row[1]
        team_rating_df = team_rating_df.append({
            'GW': row['event'],
            'team': row['team_h'],
            'opponent': row['team_a'],
            'team_name': row['home_team_name'],
            'opponent_name': row['away_team_name'],
            'GF': row['team_h_score'],
            'GA': row['team_a_score'],
            'was_home': 1,
            }, ignore_index=True)
        team_rating_df = team_rating_df.append({
            'GW': row['event'],
            'team': row['team_a'],
            'opponent': row['team_h'],
            'team_name': row['away_team_name'],
            'opponent_name': row['home_team_name'],
            'GF': row['team_a_score'],
            'GA': row['team_h_score'],
            'was_home': 0,
            }, ignore_index=True)
    def get_pts_won(x):
        if x['GF'] > x['GA']:
            return 3
        elif x['GF'] < x['GA']:
            return 0 
        else:
            return 1

    team_rating_df['pts_won'] = team_rating_df.apply(lambda x : get_pts_won(x), axis=1)
    team_rating_df['GA'] = team_rating_df.GA.astype(int)
    team_rating_df['GF'] = team_rating_df.GF.astype(int)
    team_rating_df['GW'] = team_rating_df.GW.astype(int)
    team_rating_df['opponent'] = team_rating_df.opponent.astype(int)
    team_rating_df['team'] = team_rating_df.team.astype(int)
    team_rating_df['was_home'] = team_rating_df.was_home.astype(int)
    team_rating_df = team_rating_df.sort_values(['team', 'GW'], ascending=[True, True])
    team_rating_df['pts_total'] = team_rating_df['pts_won']

    #ADD 'pts_total' column to dataframe
    helper_pts_total = []
    groups = team_rating_df.groupby(['team'])
    for group in groups:
        group[1]['pts_total'] = group[1]['pts_won'].cumsum()
        group[1]['GF'] = group[1]['GF'].cumsum()
        group[1]['GA'] = group[1]['GA'].cumsum()
        helper_pts_total.append(group[1])
    team_fixtures_df = pd.DataFrame()
    for team in helper_pts_total:
        team_fixtures_df = pd.concat([team_fixtures_df, team])
    team_fixtures_df['rating'] = team_fixtures_df['pts_total'] + team_fixtures_df['GF'] - team_fixtures_df['GA']

    #Add standardized rating to dataframe
    agg_df = team_fixtures_df.groupby('GW')
    helper_rating = []
    for group in agg_df:
        group[1]['rating_standardized'] = (group[1]['rating']- group[1]['rating'].mean()) / group[1]['rating'].std()
        helper_rating.append(group[1])
    final_team_fixtures_df = pd.DataFrame()
    for team in helper_rating:
        final_team_fixtures_df = pd.concat([final_team_fixtures_df, team])

    #Bin teams by rating (add bin to df_column 'binned_rating')
    def bin_rating(score):
        if score <= -1.0:
            return 1
        elif score <= -0.5:
            return 2
        elif score <= 0:
            return 3
        elif score <= 0.5:
            return 4
        elif score <= 1:
            return 5
        else:
            return 6
    final_team_fixtures_df['binned_rating'] = final_team_fixtures_df['rating_standardized'].apply(lambda x : bin_rating(x))
    
    final_team_fixtures_df.to_csv('csv/team_ratings.csv', index = False)

    return final_team_fixtures_df


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

# Read team_ratings.csv --> return team_ratings df (to reduce computation at runtime)
def get_team_ratings():
    f = open("csv/team_ratings.csv", "r")
    ratings_df = pd.read_csv(f)
    return ratings_df