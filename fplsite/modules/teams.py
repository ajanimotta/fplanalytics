#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time

#%%
# Grab advanced team data from whoscored (3 tabs: summary, defensive, offensive) and create corresponding csv's
def whoscored_team_to_csv(gametype):
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/7811/Stages/17590/TeamStatistics/England-Premier-League-2019-2020')

    statistics = {  # this is a list of all the tabs on the page
        'summary': DataFrame(),
        'defensive': DataFrame(),
        'offensive': DataFrame(),
    }

    count = 0
    time.sleep(3)
    tabs = driver.find_element_by_xpath('//*[@id="stage-team-stats-options"]').find_elements_by_tag_name('li')  # this pulls all the tab elements
    for tab in tabs[:-1]:  # iterate over the different tab sections
        print("tab text: ", tab.text)
        section = tab.text.lower()
        print("section: ", section, "section title: ", section.title())
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="stage-team-stats-options"]').find_element_by_link_text(section.title()).click()  # clicks the actual tab by using the dictionary's key (.proper() makes the first character in the string uppercase)
        time.sleep(3)
        while driver.find_element_by_xpath('//*[@id="statistics-team-table-%s"]' % section).get_attribute('class') == 'is-updating':  # string formatting on the xpath to change for each section that is iterated over
            time.sleep(1)
        view = driver.find_element_by_link_text(gametype)
        view.click() 
        time.sleep(3)
        table = driver.find_element_by_xpath('//*[@id="statistics-team-table-%s"]' % section)  # string formatting on the xpath to change for each section that is iterated over
        table_html = table.get_attribute('innerHTML')
        df = pd.read_html(table_html)[0]
        statistics[section] = pd.concat([statistics[section], df])
        count += 1

    statistics['summary'].to_csv('csv/summary_team_%s.csv' % gametype, index = False)
    statistics['defensive'].to_csv('csv/defensive_team_%s.csv' % gametype, index = False)
    statistics['offensive'].to_csv('csv/offensive_team_%s.csv' % gametype, index = False)
    return statistics

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#%%
def whoscored_team_table_to_csv():
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League')

    table_df = pd.DataFrame()
    time.sleep(5)
    wide = driver.find_element_by_link_text('Wide')
    wide.click()
    time.sleep(3) 
    table = driver.find_element_by_xpath('//*[@id="standings-17590"]')
    table_html = table.get_attribute('innerHTML')
    df = pd.read_html(table_html)[0]
    table_df = pd.concat([table_df, df])
    time.sleep(5)
    table_df.to_csv('csv/team_table.csv', index = False)
    return table_df

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#%%
def advanced_team():
    team_stats = {
        'overall': pd.DataFrame(),
        'home': pd.DataFrame(),
        'away': pd.DataFrame()
    }

    f = open("csv/teams.csv", "r")
    fpl_team_df = pd.read_csv(f)
    fpl_team_df = fpl_team_df[['id', 'name', 'short_name']]

    sum_ov = open('csv/summary_team_Overall.csv', "r")
    sum_ov_df = pd.read_csv(sum_ov)
    sum_ov_df = sum_ov_df [['Team', 'Goals', 'Shots pg', 'Possession%']]
    sum_ov_df = sum_ov_df.rename(columns={"Team": "name", "Goals": "total_goals", "Shots pg": "spg", "Possession%": "poss"})
    team_stats['overall'] = pd.concat([team_stats['overall'], sum_ov_df], axis=1)

    sum_home = open('csv/summary_team_Home.csv', "r")
    sum_home_df = pd.read_csv(sum_home)
    sum_home_df = sum_home_df [['Team', 'Goals', 'Shots pg', 'Possession%']]
    sum_home_df = sum_home_df.rename(columns={"Team": "name", "Goals": "goals_home", "Shots pg": "spg_home", "Possession%": "poss_home"})
    team_stats['home'] = pd.concat([team_stats['home'], sum_home_df], axis=1)

    sum_away = open('csv/summary_team_Away.csv', "r")
    sum_away_df = pd.read_csv(sum_away)
    sum_away_df = sum_away_df [['Team', 'Goals', 'Shots pg', 'Possession%']]
    sum_away_df = sum_away_df.rename(columns={"Team": "name", "Goals": "goals_away", "Shots pg": "spg_away", "Possession%": "poss_away"})
    team_stats['away'] = pd.concat([team_stats['away'], sum_away_df], axis=1)
    
    def_ov = open('csv/defensive_team_Overall.csv', "r")
    def_ov_df = pd.read_csv(def_ov)
    def_ov_df = def_ov_df[['Shots pg']]
    def_ov_df = def_ov_df.rename(columns={"Shots pg": "scpg"})
    team_stats['overall'] = pd.concat([team_stats['overall'], def_ov_df], axis=1)

    def_home = open('csv/defensive_team_Home.csv', "r")
    def_home_df = pd.read_csv(def_home)
    def_home_df = def_home_df[['Shots pg']]
    def_home_df = def_home_df.rename(columns={"Shots pg": "scpg_home"})
    team_stats['home'] = pd.concat([team_stats['home'], def_home_df], axis=1)

    def_away = open('csv/defensive_team_Away.csv', "r")
    def_away_df = pd.read_csv(def_away)
    def_away_df = def_away_df[['Shots pg']]
    def_away_df = def_away_df.rename(columns={"Shots pg": "scpg_away"})
    team_stats['away'] = pd.concat([team_stats['away'], def_away_df], axis=1)

    off_ov = open("csv/offensive_team_Overall.csv", "r")
    off_ov_df = pd.read_csv(off_ov)
    off_ov_df = off_ov_df[['Shots OT pg']]
    off_ov_df = off_ov_df.rename(columns={"Shots OT pg": "sot"})
    team_stats['overall'] = pd.concat([team_stats['overall'], off_ov_df], axis=1)

    off_home = open("csv/offensive_team_Home.csv", "r")
    off_home_df = pd.read_csv(off_home)
    off_home_df = off_home_df[['Shots OT pg']]
    off_home_df = off_home_df.rename(columns={"Shots OT pg": "sot_home"})
    team_stats['home'] = pd.concat([team_stats['home'], off_home_df], axis=1)

    off_away = open("csv/offensive_team_Away.csv", "r")
    off_away_df = pd.read_csv(off_away)
    off_away_df = off_away_df[['Shots OT pg']]
    off_away_df = off_away_df.rename(columns={"Shots OT pg": "sot_away"})
    team_stats['away'] = pd.concat([team_stats['away'], off_away_df], axis=1)

    f4 = open("csv/team_table.csv", "r")
    table_df = pd.read_csv(f4)
    table_df = table_df.rename(columns={'R': 'rank', "Team": "name"})

    teams_df = pd.merge(team_stats['overall'], team_stats['home'], on='name')
    teams_df = pd.merge(teams_df, team_stats['away'], on='name')
    teams_df = pd.merge(teams_df, table_df, on='name')
    team_names = {
        "Manchester City": "Man City", "Leicester": "Leicester", "Liverpool": "Liverpool", "Chelsea":"Chelsea",
        "Aston Villa":"Aston Villa", "Burnley":"Burnley", "Wolverhampton Wanderers":"Wolves", "Sheffield United":"Sheffield Utd",
         "Bournemouth":"Bournemouth", "Arsenal":"Arsenal", "Tottenham":"Spurs", "Manchester United":"Man Utd", 
         "West Ham":"West Ham", "Brighton":"Brighton", "Crystal Palace":"Crystal Palace",
          "Newcastle United":"Newcastle", "Everton":"Everton", "Norwich":"Norwich",
           "Watford":"Watford", "Southampton":"Southampton"
    }
    teams_df['name'] = teams_df['name'].map(team_names)
    teams_df = pd.merge(fpl_team_df,teams_df, on='name')
    
    return teams_df
