#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time

#%%
# BUILD PLAYER DATAFRAME containing info (first_name, second_name, goals_scored, assists, total_points, minutes, goals_conceded,
    # creativity, threat, bonus, bps, ict_index, clean_sheets, red_cards, yellow_cards, selected_by_percent, now_cost
    # , team_name, position)

def fpl_player_to_csv():
    # SCRAPE "https://fantasy.premierleague.com/player-list" for position data
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get("https://fantasy.premierleague.com/player-list")
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # grab web_name/ position data from tables
    position_data = {}
    counter = 1
    tables = soup.findAll('table', attrs={'class': 'Table-ziussd-1 hOInPp'})
    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            web_name = tds[0]
            team = tds[1]
            points = tds[2]
            if 0 < counter < 3:
                position = 'GKP'
            elif 2 < counter < 5:
                position = 'DEF'
            elif 4 < counter < 7:
                position = 'MID'
            else:
                position = 'FWD'
            position_data[(web_name.text, team.text, points.text)] = position
        counter = counter + 1

    # Build dataframe containing info (first_name, second_name, goals_scored, assists, total_points, minutes, goals_conceded,
    # creativity, threat, bonus, bps, ict_index, clean_sheets, red_cards, yellow_cards, selected_by_percent, now_cost
    # , team_name, position)

    f = open("csv/cleaned_players.csv", "r")
    player_stats_df = pd.read_csv(f)
    player_stats_df = player_stats_df[['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes',
    'goals_conceded', 'clean_sheets', 'red_cards', 'yellow_cards', 'bonus', 'selected_by_percent', 'now_cost']]

    # Build dataframe containing info (id, team, web_name)
    f1 = open("csv/players_raw.csv", "r")
    raw_player_df = pd.read_csv(f1)
    raw_player_df = raw_player_df[['id', 'team', 'web_name', 'form']]

    #Build dictionary containing info (team, team_name) / (team, team_abbr)
    teams_dict = {
        1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brighton",
        5: "Burnley", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton",
        9: "Leicester", 10: "Liverpool", 11: "Man City", 12: "Man Utd",
        13: "Newcastle", 14: "Norwich", 15: "Sheffield Utd", 16: "Southampton",
        17: "Spurs", 18: "Watford", 19: "West Ham", 20: "Wolves" 
    }
    abbr_dict = {
        1: "ARS", 2: "AVL", 3: "BOU", 4: "BHA",
        5: "BUR", 6: "CHE", 7: "CRY", 8: "EVE",
        9: "LEI", 10: "LIV", 11: "MCI", 12: "MUN",
        13: "NEW", 14: "NOR", 15: "SHU", 16: "SOU",
        17: "TOT", 18: "WAT", 19: "WHU", 20: "WOL" 
    }
    # JOIN TWO DFs AND ADD POSITION FROM 'data'
    frames = [player_stats_df, raw_player_df]
    player_fpl_df = pd.concat(frames, axis=1)

    # CONVERT 'now_cost' from int64 with no decimals to float64 with decimal
    player_fpl_df['cost'] = player_fpl_df['now_cost'] / 10.0

    player_fpl_df['position'] = 'NONE'
    for i in list(range(0, len(player_fpl_df))):
        web_name = player_fpl_df.at[i, 'web_name']
        team_id = player_fpl_df.at[i, 'team']
        team_name = teams_dict[team_id]
        team_abbr = abbr_dict[team_id]
        points = player_fpl_df.at[i, 'total_points']
        player_fpl_df.at[i, 'team_name'] = team_name
        player_fpl_df.at[i, 'team_abbr'] = team_abbr
        player_fpl_df.at[i, 'position'] = position_data[(web_name, team_name, str(points))]

    player_fpl_df.to_csv('csv/player_fpl.csv', index = False)

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#%%
# Build FPL_PLAYER dataframe from fpl_player.csv 
def fpl_player():
    f = open("csv/player_fpl.csv", "r")
    fpl_players_df = pd.read_csv(f)
    fpl_players_df = fpl_players_df[['web_name', 'id', 'goals_scored', 'assists', 'total_points', 'minutes',
    'goals_conceded', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'form','cost', 'bonus', 'position', 'team', 'team_name', 'team_abbr']]

    # MAKE 'web_name' column distinct for plotting purposes
    indices = list(np.where(fpl_players_df['web_name'].duplicated(keep=False))[0])
    for i in indices:
        name = fpl_players_df.iloc[i]['web_name']
        team_abbr = fpl_players_df.iloc[i]['team_abbr']
        fpl_players_df.at[i, 'web_name'] = name + ' (' + team_abbr + ')'
    return fpl_players_df

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#%%
# Grab advanced player data from whoscored (BY SECTION: 'summary', 'defensive', 'offensive', 'passing') 
# and create corresponding csv
def whoscored_all_players_to_csv(section):
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/7811/Stages/17590/PlayerStatistics/England-Premier-League-2019-2020')

    count_dict = {'summary': 0, 'defensive': 1, 'offensive': 1, 'passing': 1}

    section_df = pd.DataFrame()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="stage-top-player-stats-options"]').find_element_by_link_text(section.capitalize()).click() 
    time.sleep(3)
    all_players = driver.find_element_by_link_text('All players')
    all_players.click() 
    while True:
        while driver.find_element_by_xpath('//*[@id="statistics-table-%s"]' % section).get_attribute('class') == 'is-updating':  # string formatting on the xpath to change for each section that is iterated over
            time.sleep(1)

        table = driver.find_element_by_xpath('//*[@id="statistics-table-%s"]' % section)  # string formatting on the xpath to change for each section that is iterated over
        table_html = table.get_attribute('innerHTML')
        df = pd.read_html(table_html)[0]
        section_df = pd.concat([section_df, df])
        next_link = driver.find_elements_by_xpath('//*[@id="next"]')[count_dict[section]]  # makes sure it's selecting the correct index of 'next' items 
        if 'disabled' in next_link.get_attribute('class'):
            break
        time.sleep(5)
        next_link.click()
    section_df.to_csv('csv/%s_players.csv' % section, index = False)
    return section_df

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

#%%
#Create whoscored player stats dataframe containing info () from WHOSCORED csv's
def whoscored_player():
    f_summary = open("csv/summary_players.csv", "r")
    summary_df = pd.read_csv(f_summary)
    summary_df = summary_df[['Player', 'SpG', 'PS%']]

    f_offensive = open("csv/offensive_players.csv", "r")
    offensive_df = pd.read_csv(f_offensive)
    offensive_df = offensive_df[['KeyP', 'Drb']]

    #f_defensive = open("defensive.csv", "r")
    #defensive_df = pd.read_csv(f_defensive)

    f_passing = open("csv/passing_players.csv", "r")
    passing_df = pd.read_csv(f_passing)
    passing_df = passing_df[['AvgP', 'Crosses', 'ThrB']]

    advanced_player_df = pd.concat([summary_df, offensive_df, passing_df], axis=1)

    # Get rid of '-' entries in dataframe
    advanced_player_df.loc[(advanced_player_df['SpG'] == '-'), 'SpG'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['PS%'] == '-'), 'PS%'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['KeyP'] == '-'), 'KeyP'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['Drb'] == '-'), 'Drb'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['AvgP'] == '-'), 'AvgP'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['Crosses'] == '-'), 'Crosses'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['ThrB'] == '-'), 'ThrB'] = float(0.0)

    # Rid player column of age and position information/add team column
    def rid_team(player_team):
        player_team_arr = player_team.split()
        teams = {
            "Arsenal", "Aston", "Bournemouth", "Brighton",
            "Burnley", "Chelsea", "Crystal", "Everton",
            "Leicester", "Liverpool", "Manchester",
            "Newcastle", "Norwich", "Sheffield", "Southampton",
            "Tottenham", "Watford", "West", "Wolverhampton" 
        }
        for i in range(0, len(player_team_arr)):
            if player_team_arr[i] in teams:
                player = " ".join(player_team_arr[0:i])
                team = " ".join(player_team_arr[i:])
                break
        return [player, team]

    player_team = advanced_player_df['Player'].apply(lambda x: x.split(',')[0])
    advanced_player_df['Player'] = player_team.apply(lambda x: rid_team(x)[0])
    advanced_player_df = advanced_player_df.rename(columns={"Player": "player_name"})
    return advanced_player_df

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------


#Load UNDERSTAT dataframe including ('games', 'goals', 'key_passes', 'xG', 'xA')
def understat_player():
    f1 = open('csv/player_idlist.csv', "r")
    ids_df = pd.read_csv(f1)
    ids_df['player_name'] = ids_df['first_name'] + ' ' + ids_df['second_name']
    f2 = open('csv/understat_player.csv', "r", encoding = 'ISO-8859-1')
    understat_player_df = pd.read_csv(f2)
    understat_player_df = understat_player_df[['player_name', 'games', 'goals', 'key_passes', 'xG', 'xA']]
    understat_player_df = pd.merge(understat_player_df, ids_df, on = 'player_name', how = 'left')

    # ADD FPL PLAYER IDs to understat_player_df (using fpl_id_helper.csv)
    f = open('csv/fpl_id_helper.csv', 'r')
    id_filler_df = pd.read_csv(f)
    id_filler_df = id_filler_df[['player_name', 'id']]  
    understat_player_df = pd.merge(understat_player_df, id_filler_df, on = 'player_name', how = 'left')
    #print(understat_player_df.isnull().sum())
    #print(len(understat_player_df[understat_player_df['id_x'].isnull()]))
    #print(understat_player_df[understat_player_df['id_x'].isnull()])
    understat_player_df['id_x'] = understat_player_df['id_x'].mask(understat_player_df['id_x'].isnull(), understat_player_df['id_y'])
    understat_player_df = understat_player_df.rename(columns={"id_x": "id"})
    understat_player_df['id'] = understat_player_df['id'].apply(lambda x: int(x))
    understat_player_df = understat_player_df.drop(columns = ['id_y', 'first_name', 'second_name'])  
    return understat_player_df

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

# Merge WHOSCORED AND UNDERSTAT DFs --> output result into advanced_player.csv 
# --> input missing data resulting from discrepancy in 'player_name' USING 'advanced_player_helper.csv'
def merge_advanced_player():
    whoscored_player_df = whoscored_player()
    understat_player_df = understat_player()

    #Maps discrepant player names to match that of whoscored 'player_name' --for clean merging purposes
    discrepant_understat_names = [
        'Rodri', 'Caglar Söyüncü', 'N&#039;Golo Kanté', 'Johann Berg Gudmundsson', 'Nicolas Pepe', 'Jack O&#039;Connell',
        'Tanguy NDombele Alvaro', 'Djibril Sidibe', 'Angelino', 'Ezri Konsa Ngoyo', 'Seamus Coleman', 'Romain Saiss',
        'Alex Oxlade-Chamberlain', 'Eric Garcia', 'Ahmed Elmohamady', 'Kepa', 'Joseph Gomez'
    ]
    discrepant_names_dict = {
        'Rodri': 'Rodrigo', 'Caglar Söyüncü': 'Çaglar Söyüncü', 'N&#039;Golo Kanté': "N'Golo Kanté", 
        'Johann Berg Gudmundsson': 'Johann Gudmundsson', 'Nicolas Pepe': 'Nicolas Pépé', 'Jack O&#039;Connell': "Jack O'Connell",
        'Tanguy NDombele Alvaro': "Tanguy Ndombele", 'Djibril Sidibe': "Djibril Sidibé", 'Angelino': "Angeliño", 
        'Ezri Konsa Ngoyo': "Ezri Konsa", 'Seamus Coleman': "Séamus Coleman", 'Romain Saiss': "Romain Saïss",
        'Alex Oxlade-Chamberlain': "Alex Oxlade Chamberlain", 'Eric Garcia': "Eric García", 
        'Ahmed Elmohamady': "Ahmed El Mohamady", 'Kepa': "Kepa Arrizabalaga", 'Joseph Gomez': "Joe Gomez"
    }
    understat_player_df.loc[understat_player_df.player_name.isin(discrepant_understat_names), 'player_name'] = understat_player_df['player_name'].map(discrepant_names_dict)
    advanced_player_df = pd.merge(understat_player_df, whoscored_player_df, on = 'player_name', how = 'right')
    return advanced_player_df

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

def get_players():
    players = fpl_player()
    understat_player_df = understat_player()
    players = pd.merge(players, understat_player_df, on= 'id', how = 'inner')
    players['ppg'] = round((players['total_points'] / players['games']), 1)
    players['mpg'] = round((players['minutes'] / players['games']), 1)
    players['gpg'] = round((players['goals_scored'] / players['games']), 1)
    players['gcpg'] = round((players['goals_conceded'] / players['games']), 1)
    players['apg'] = round((players['assists'] / players['games']), 1)
    players['cspg'] = round((players['clean_sheets'] / players['games']), 1)
    players['bppg'] = round((players['bonus'] / players['games']), 1)
    return players
