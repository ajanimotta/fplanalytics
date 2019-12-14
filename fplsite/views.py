from django.shortcuts import render
import math
from collections import OrderedDict
import pandas as pd
from .modules.gather_data import fpl_player, get_players, get_gws, get_fixtures, advanced_team, get_team_ratings, get_gkps_home_away, get_defs_home_away, get_mids_home_away, get_fwds_home_away, get_strong_weak, get_form
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend, LegendItem, Panel, Tabs, CustomJS, StringFormatter
from bokeh.models.widgets import DataTable, TableColumn, Select, HTMLTemplateFormatter, CheckboxButtonGroup, Button
from bokeh.models.tools import HoverTool
from bokeh.embed import components
from bokeh.layouts import layout, gridplot, column, row



# homepage view--------------------------------------------------------------------------------------------------------------------------
def homepage(request):
    return render(request, 'pages/index.html', {})

# elements view--------------------------------------------------------------------------------------------------------------------------
def elements(request):
    return render(request, 'pages/elements.html', {})

# teams view--------------------------------------------------------------------------------------------------------------------------
def teams(request):
    #TODO: create bokeh components for roi,home/away,etc. plots and return them to render

    #PLOT TEAM RATINGS FOR CURRENT GW----------------------------------------------------------------------------------------
    ratings = get_team_ratings()
    current_gw = ratings['GW'].max()
    ratings_curr = ratings.loc[ratings['GW'] == current_gw]
    
    #Assign team colors for line plot
    team_colors = {
        1:'red', 2:'firebrick', 3:'black', 4:'royalblue', 5:'maroon',
        6:'blue', 7:'mediumblue', 8:'blue', 9:'mediumblue', 10:'red',
        11:'lightskyblue', 12:'red', 13:'black', 14:'yellow', 15:'red',
        16:'firebrick', 17:'navy', 18:'gold', 19:'maroon', 20:'darkorange'
    }
    ratings_curr['color'] = ratings_curr['team'].map(team_colors)
    

    curr_cds = ColumnDataSource(ratings_curr)
    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    ratings_plot = figure(x_axis_label='Team', y_axis_label='Team Rating', title=' Team Strength: Gameweek {}'.format(current_gw), 
                   plot_width=900, plot_height=500, x_range=ratings_curr['team_name'], tools=TOOLS, toolbar_location="above")

    ratings_plot.circle("team_name", "rating_standardized", source=curr_cds, color='color', alpha=0.8, size=8)
    
    hover_ratings = ratings_plot.select(dict(type=HoverTool))
    hover_ratings.tooltips = OrderedDict([
        ("Name", "@team_name"),
        ("Team Rating", "@rating_standardized")
    ])
    ratings_plot.xaxis.major_label_orientation = math.pi/4
    ratings_script, ratings_div = components(ratings_plot)

    # TOP 5 (by current gameweek): RATINGS THROUGHOUT THE SEASON-------------------------------------------------------
    #Grab this week's top 5 teams
    top5_copy = ratings
    top5 = ratings_curr.nlargest(5, ['rating_standardized', 'pts_total'], keep='last')
    top5_team_names = top5['team_name']
    top5_teams = []
    for team_name in top5_team_names:
        top5_teams.append(top5_copy.loc[top5_copy['team_name'] == team_name])
    for team in top5_teams:
        team['color'] = team['team'].map(team_colors)
    
    #Plot top 5 teams' ratings throughout the season    
    cds0 = ColumnDataSource(top5_teams[0])
    cds1 = ColumnDataSource(top5_teams[1])
    cds2 = ColumnDataSource(top5_teams[2])
    cds3 = ColumnDataSource(top5_teams[3])
    cds4 = ColumnDataSource(top5_teams[4])
    
    top5_plot = figure(x_axis_label='Gameweek', y_axis_label='Team Rating', title=' Team Strength (Top 5): Through the Gameweeks', 
    plot_width=700, plot_height=400, tools=TOOLS, toolbar_location="above")
    
    plot0 = top5_plot.line("GW", "rating_standardized", source=cds0, color=cds0.data['color'][0], alpha=0.8)
    plot1 = top5_plot.line("GW", "rating_standardized", source=cds1, color=cds1.data['color'][0], alpha=0.8)
    plot2 = top5_plot.line("GW", "rating_standardized", source=cds2, color=cds2.data['color'][0], alpha=0.8)
    plot3 = top5_plot.line("GW", "rating_standardized", source=cds3, color=cds3.data['color'][0], alpha=0.8)
    plot4 = top5_plot.line("GW", "rating_standardized", source=cds4, color=cds4.data['color'][0], alpha=0.8)
    
    top5_legend = Legend(items=[(cds0.data['team_name'][0] , [plot0]), (cds1.data['team_name'][0] , [plot1]),
                          (cds2.data['team_name'][0] , [plot2]), (cds3.data['team_name'][0] , [plot3]),
                          (cds4.data['team_name'][0] , [plot4])], location=(15,80), orientation="vertical", 
                    click_policy='hide', glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    top5_plot.add_layout(top5_legend, 'right')
    
    hover_top5 =top5_plot.select(dict(type=HoverTool))
    hover_top5.tooltips = OrderedDict([
        ("Name", "@team_name"),
        ("Gameweek", "@GW"),
        ("Team Rating", "@rating_standardized")
    ])
    #top5_script, top5_div = components(top5_plot)

    # TOP 6 to 10 (by current gameweek): RATINGS THROUGHOUT THE SEASON-------------------------------------------------------
    top6to10_copy = ratings
    top10 = ratings_curr.nlargest(10, ['rating_standardized', 'pts_total'], keep='last')
    top6to10 = top10.nsmallest(5, ['rating_standardized', 'pts_total'], keep='last')
    top6to10_team_names = top6to10['team_name']
    top6to10_teams = []
    for team_name in top6to10_team_names:
        top6to10_teams.append(top6to10_copy.loc[top6to10_copy['team_name'] == team_name])
    
    for team in top6to10_teams:
        team['color'] = team['team'].map(team_colors)
    
    #Plot top 5 teams' ratings throughout the season    
    cds5 = ColumnDataSource(top6to10_teams[0])
    cds6 = ColumnDataSource(top6to10_teams[1])
    cds7 = ColumnDataSource(top6to10_teams[2])
    cds8 = ColumnDataSource(top6to10_teams[3])
    cds9 = ColumnDataSource(top6to10_teams[4])
    
    top6to10_plot = figure(x_axis_label='Gameweek', y_axis_label='Team Rating', title=' Team Strength (Top 6 to 10): Through the Gameweeks', 
    plot_width=700, plot_height=400, tools=TOOLS, toolbar_location="above")
    
    plot5 = top6to10_plot.line("GW", "rating_standardized", source=cds5, color=cds5.data['color'][0], alpha=0.8)
    plot6 = top6to10_plot.line("GW", "rating_standardized", source=cds6, color=cds6.data['color'][0], alpha=0.8)
    plot7 = top6to10_plot.line("GW", "rating_standardized", source=cds7, color=cds7.data['color'][0], alpha=0.8)
    plot8 = top6to10_plot.line("GW", "rating_standardized", source=cds8, color=cds8.data['color'][0], alpha=0.8)
    plot9 = top6to10_plot.line("GW", "rating_standardized", source=cds9, color=cds9.data['color'][0], alpha=0.8)
    
    top6to10_legend = Legend(items=[(cds5.data['team_name'][0] , [plot5]), (cds6.data['team_name'][0] , [plot6]),
                          (cds7.data['team_name'][0] , [plot7]), (cds8.data['team_name'][0] , [plot8]),
                          (cds9.data['team_name'][0] , [plot9])], location=(15,80), orientation="vertical", 
                    click_policy='hide', glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    top6to10_plot.add_layout(top6to10_legend, 'right')
    
    hover_top6to10 =top6to10_plot.select(dict(type=HoverTool))
    hover_top6to10.tooltips = OrderedDict([
        ("Name", "@team_name"),
        ("Gameweek", "@GW"),
        ("Team Rating", "@rating_standardized")
    ])
    #top6to10_script, top6to10_div = components(top6to10_plot)

    # TOP 11 to 15 (by current gameweek): RATINGS THROUGHOUT THE SEASON-------------------------------------------------------
    top11to15_copy = ratings # to avoid runtime error:models must be owned by a single document
    top15 = ratings_curr.nlargest(15, ['rating_standardized', 'pts_total'], keep='last')
    top11to15 = top15.nsmallest(5, ['rating_standardized', 'pts_total'], keep='last')
    top11to15_team_names = top11to15['team_name']
    top11to15_teams = []
    for team_name in top11to15_team_names:
        top11to15_teams.append(top11to15_copy.loc[top11to15_copy['team_name'] == team_name])
    for team in top11to15_teams:
        team['color'] = team['team'].map(team_colors)
    
    #Plot top 5 teams' ratings throughout the season    
    cds10 = ColumnDataSource(top11to15_teams[0])
    cds11 = ColumnDataSource(top11to15_teams[1])
    cds12 = ColumnDataSource(top11to15_teams[2])
    cds13 = ColumnDataSource(top11to15_teams[3])
    cds14 = ColumnDataSource(top11to15_teams[4])
    
    top11to15_plot = figure(x_axis_label='Gameweek', y_axis_label='Team Rating', title=' Team Strength (Top 11 to 15): Through the Gameweeks', 
    plot_width=700, plot_height=400, tools=TOOLS, toolbar_location="above")
    
    plot10 = top11to15_plot.line("GW", "rating_standardized", source=cds10, color=cds0.data['color'][0], alpha=0.8)
    plot11 = top11to15_plot.line("GW", "rating_standardized", source=cds11, color=cds1.data['color'][0], alpha=0.8)
    plot12 = top11to15_plot.line("GW", "rating_standardized", source=cds12, color=cds2.data['color'][0], alpha=0.8)
    plot13 = top11to15_plot.line("GW", "rating_standardized", source=cds13, color=cds3.data['color'][0], alpha=0.8)
    plot14 = top11to15_plot.line("GW", "rating_standardized", source=cds14, color=cds4.data['color'][0], alpha=0.8)
    
    top11to15_legend = Legend(items=[(cds10.data['team_name'][0] , [plot10]), (cds11.data['team_name'][0] , [plot11]),
                          (cds12.data['team_name'][0] , [plot12]), (cds13.data['team_name'][0] , [plot13]),
                          (cds14.data['team_name'][0] , [plot14])], location=(15,80), orientation="vertical", 
                    click_policy='hide', glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    top11to15_plot.add_layout(top11to15_legend, 'right')
    
    hover_top11to15 =top11to15_plot.select(dict(type=HoverTool))
    hover_top11to15.tooltips = OrderedDict([
        ("Name", "@team_name"),
        ("Gameweek", "@GW"),
        ("Team Rating", "@rating_standardized")
    ])

    # TOP 11 to 15 (by current gameweek): RATINGS THROUGHOUT THE SEASON-------------------------------------------------------
    top16to20_copy = ratings # to avoid runtime error:models must be owned by a single document
    top16to20 = ratings_curr.nsmallest(5, ['rating_standardized', 'pts_total'], keep='last')
    top16to20_team_names = top16to20['team_name']
    top16to20_teams = []
    for team_name in top16to20_team_names:
        top16to20_teams.append(top16to20_copy.loc[top16to20_copy['team_name'] == team_name])

    for team in top16to20_teams:
        team['color'] = team['team'].map(team_colors)
    
    #Plot top 5 teams' ratings throughout the season    
    cds15 = ColumnDataSource(top16to20_teams[0])
    cds16 = ColumnDataSource(top16to20_teams[1])
    cds17 = ColumnDataSource(top16to20_teams[2])
    cds18 = ColumnDataSource(top16to20_teams[3])
    cds19 = ColumnDataSource(top16to20_teams[4])

    top16to20_plot = figure(x_axis_label='Gameweek', y_axis_label='Team Rating', title=' Team Strength (Top 16 to 20): Through the Gameweeks', 
    plot_width=700, plot_height=400, tools=TOOLS, toolbar_location="above")
    
    plot15 = top16to20_plot.line("GW", "rating_standardized", source=cds15, color=cds15.data['color'][0], alpha=0.8)
    plot16 = top16to20_plot.line("GW", "rating_standardized", source=cds16, color=cds16.data['color'][0], alpha=0.8)
    plot17 = top16to20_plot.line("GW", "rating_standardized", source=cds17, color=cds17.data['color'][0], alpha=0.8)
    plot18 = top16to20_plot.line("GW", "rating_standardized", source=cds18, color=cds18.data['color'][0], alpha=0.8)
    plot19 = top16to20_plot.line("GW", "rating_standardized", source=cds19, color=cds19.data['color'][0], alpha=0.8)
    
    top16to20_legend = Legend(items=[(cds15.data['team_name'][0] , [plot15]), (cds16.data['team_name'][0] , [plot16]),
                          (cds17.data['team_name'][0] , [plot17]), (cds18.data['team_name'][0] , [plot18]),
                          (cds19.data['team_name'][0] , [plot19])], location=(15,80), orientation="vertical", 
                    click_policy='hide', glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    top16to20_plot.add_layout(top16to20_legend, 'right')
    
    hover_top16to20 = top16to20_plot.select(dict(type=HoverTool))
    hover_top16to20.tooltips = OrderedDict([
        ("Name", "@team_name"),
        ("Gameweek", "@GW"),
        ("Team Rating", "@rating_standardized")
    ])

    grid = gridplot([[top5_plot, top6to10_plot], [top11to15_plot, top16to20_plot]])
    top_script, top_div = components(grid)

    #TEAM TABLE (Overall)-----------------------------------------------------------------------------
    teams = advanced_team()
    teams_ov = teams[[
        'short_name', 'spg',  'scpg', 'sot', 
        'P_Overall', 'W_Overall', 'D_Overall', 'L_Overall', 'GF_Overall', 'GA_Overall', 'Pts_Overall'
    ]]

    source_ov = ColumnDataSource(teams_ov)
    columns_ov = [
        TableColumn(field="short_name", title="Team", formatter=StringFormatter(font_style="bold")),
        TableColumn(field="P_Overall", title="Games Played"),
        TableColumn(field="Pts_Overall", title="Points"),
        TableColumn(field="W_Overall", title="Wins"),
        TableColumn(field="D_Overall", title="Draws"),
        TableColumn(field="L_Overall", title="Losses"),
        TableColumn(field="GF_Overall", title="GF"),
        TableColumn(field="GA_Overall", title="GA"),
        TableColumn(field="spg", title="Shots pg"),
        TableColumn(field="sot", title="Shots OT pg"),
        TableColumn(field="scpg", title="Shots conceded pg")
    ]
    table_ov = DataTable(source=source_ov, columns=columns_ov,  width=1250, height=600)
    table_ov_script, table_ov_div = components(table_ov)

     #TEAM TABLE (Home)-----------------------------------------------------------------------------
    teams_home = teams[[
        'short_name', 'spg_home',  'scpg_home', 'sot_home', 
        'P_Home', 'W_Home', 'D_Home', 'L_Home', 'GF_Home', 'GA_Home', 'Pts_Home'
    ]]

    source_home = ColumnDataSource(teams_home)
    columns_home = [
        TableColumn(field="short_name", title="Team", formatter=StringFormatter(font_style="bold")),
        TableColumn(field="P_Home", title="Games Played"),
        TableColumn(field="Pts_Home", title="Points"),
        TableColumn(field="W_Home", title="Wins"),
        TableColumn(field="D_Home", title="Draws"),
        TableColumn(field="L_Home", title="Losses"),
        TableColumn(field="GF_Home", title="GF"),
        TableColumn(field="GA_Home", title="GA"),
        TableColumn(field="spg_home", title="Shots pg"),
        TableColumn(field="sot_home", title="Shots OT pg"),
        TableColumn(field="scpg_home", title="Shots conceded pg")
    ]
    table_home = DataTable(source=source_home, columns=columns_home,  width=1250, height=600)
    table_home_script, table_home_div = components(table_home)

    #TEAM TABLE (Away)-----------------------------------------------------------------------------
    teams_away = teams[[
        'short_name', 'spg_away',  'scpg_away', 'sot_away', 
        'P_Away', 'W_Away', 'D_Away', 'L_Away', 'GF_Away', 'GA_Away', 'Pts_Away'
    ]]

    source_away = ColumnDataSource(teams_away)
    columns_away = [
        TableColumn(field="short_name", title="Team", formatter=StringFormatter(font_style="bold")),
        TableColumn(field="P_Away", title="Games Played"),
        TableColumn(field="Pts_Away", title="Points"),
        TableColumn(field="W_Away", title="Wins"),
        TableColumn(field="D_Away", title="Draws"),
        TableColumn(field="L_Away", title="Losses"),
        TableColumn(field="GF_Away", title="GF"),
        TableColumn(field="GA_Away", title="GA"),
        TableColumn(field="spg_away", title="Shots pg"),
        TableColumn(field="sot_away", title="Shots OT pg"),
        TableColumn(field="scpg_away", title="Shots conceded pg")
    ]
    table_away = DataTable(source=source_away, columns=columns_away,  width=1250, height=600)
    table_away_script, table_away_div = components(table_away)

    max_gw = current_gw + 7
    ratings = ratings.loc[ratings['GW'] == current_gw]
    abbr_dict = {
        1: "ARS", 2: "AVL", 3: "BOU", 4: "BHA",
        5: "BUR", 6: "CHE", 7: "CRY", 8: "EVE",
        9: "LEI", 10: "LIV", 11: "MCI", 12: "MUN",
        13: "NEW", 14: "NOR", 15: "SHU", 16: "SOU",
        17: "TOT", 18: "WAT", 19: "WHU", 20: "WOL" 
    }
    ratings['team_abbr'] = ratings['team'].map(abbr_dict)
    ratings = ratings[['team_abbr', 'binned_rating']]
    ratings_dict = dict(zip(ratings.team_abbr, ratings.binned_rating))

    fixtures = get_fixtures()
    
    fixture_array = []
    for i in range(current_gw + 1, max_gw):
        gw_fixtures = fixtures.loc[fixtures['event'] == i]

        gw_fixture_dict = {
            'ARS':[], 'AVL':[], 'BOU':[], 'BHA':[], 'BUR':[], 'CHE':[], 'CRY':[], 'EVE':[], 'LEI':[], 'LIV':[],
            'MCI':[], 'MUN':[], 'NEW':[], 'NOR':[], 'SHU':[], 'SOU':[], 'TOT':[], 'WAT':[], 'WHU':[], 'WOL':[]
        }
        for row in gw_fixtures.iterrows():
            row = row[1]
            home_fixture_str = row['away_team_name'] + ' (H)'
            away_fixture_str = row['home_team_name'] + ' (A)'
            gw_fixture_dict[row['home_team_name']].append(home_fixture_str)
            gw_fixture_dict[row['away_team_name']].append(away_fixture_str)
        for key, value in gw_fixture_dict.items():
            if (len(value) == 0):
                gw_fixture_dict[key] = ['None']
        fixture_array.append(gw_fixture_dict)
    
    fixture_dict = {
            'ARS':[], 'AVL':[], 'BOU':[], 'BHA':[], 'BUR':[], 'CHE':[], 'CRY':[], 'EVE':[], 'LEI':[], 'LIV':[],
            'MCI':[], 'MUN':[], 'NEW':[], 'NOR':[], 'SHU':[], 'SOU':[], 'TOT':[], 'WAT':[], 'WHU':[], 'WOL':[]
        }
    for gw_dict in fixture_array:
        for key, value in gw_dict.items():
            for fix in value:
                fixture_dict[key].append(fix)
    
    cols = []
    color_cols = ['color0', 'color1', 'color2', 'color3', 'color4', 'color5']
    for i in range(current_gw + 1, max_gw):
        cols.append('GW' + str(i))
    upcoming_fixtures = pd.DataFrame(fixture_dict, index=cols)
    upcoming_fixtures = upcoming_fixtures.T
    upcoming_fixtures.index.name = 'team'
    
    def get_colors(x):
        colors = []
        for fix in x:
            if fix == 'None':
                colors.append('white')
            else:
                team = fix[0:3]
                rating = ratings_dict[team]
                if rating == 1:
                    colors.append('green')
                elif rating == 2:
                    colors.append('lawngreen')
                elif rating == 3:
                    colors.append('yellow')
                elif rating == 4:
                    colors.append('orange')
                elif rating == 5:
                    colors.append('red')
                else: 
                    colors.append('darkred')
        return colors
    colors_df = upcoming_fixtures.apply(lambda x: get_colors(x))
    colors_df.columns = color_cols
    upcoming_fixtures = pd.concat([upcoming_fixtures, colors_df], axis=1)

    source = ColumnDataSource(upcoming_fixtures)
    template0="""
            <div style="background:<%= 
                (function colorfromint(){
                    return (color0)
                }()) %>; 
                color: black"> 
            <b><%= value %></b>
            </div>
            """

    template1="""
            <div style="background:<%= 
                (function colorfromint(){
                    return (color1)
                }()) %>; 
                color: black"> 
            <b><%= value %></b>
            </div>
            """
    template2="""
            <div style="background:<%= 
                (function colorfromint(){
                    return (color2)
                }()) %>; 
                color: black"> 
            <b><%= value %></b>
            </div>
            """
    template3="""
            <div style="background:<%= 
                (function colorfromint(){
                    return (color3)
                }()) %>; 
                color: black"> 
            <b><%= value %></b>
            </div>
            """
    template4="""
            <div style="background:<%= 
                (function colorfromint(){
                    return (color4)
                }()) %>; 
                color: black"> 
            <b><%= value %></b>
            </div>
            """
    template5="""
            <div style="background:<%= 
                (function colorfromint(){
                    return (color5)
                }()) %>; 
                color: black"> 
            <b><%= value %></b>
            </div>
            """

    formatter0 =  HTMLTemplateFormatter(template=template0)
    formatter1 =  HTMLTemplateFormatter(template=template1)
    formatter2 =  HTMLTemplateFormatter(template=template2)
    formatter3 =  HTMLTemplateFormatter(template=template3)
    formatter4 =  HTMLTemplateFormatter(template=template4)
    formatter5 =  HTMLTemplateFormatter(template=template5)
    
    columns = [
        TableColumn(field="team", title='Team', formatter=StringFormatter(font_style="bold")),
        TableColumn(field=cols[0], title=cols[0], formatter=formatter0),
        TableColumn(field=cols[1], title=cols[1], formatter=formatter1),
        TableColumn(field=cols[2], title=cols[2], formatter=formatter2),
        TableColumn(field=cols[3], title=cols[3], formatter=formatter3),
        TableColumn(field=cols[4], title=cols[4], formatter=formatter4),
        TableColumn(field=cols[5], title=cols[5], formatter=formatter5)
    ]
    table = DataTable(source=source, columns=columns,  width=950, height=600)

    fixture_table_script, fixture_table_div = components(table)


    context = {
        'ratings_script':ratings_script, 'ratings_div':ratings_div,
        'top_script':top_script, 'top_div':top_div,
        'table_ov_script': table_ov_script, 'table_ov_div': table_ov_div,
        'table_home_script': table_home_script, 'table_home_div': table_home_div,
        'table_away_script': table_away_script, 'table_away_div': table_away_div,
        'fixture_table_script': fixture_table_script, 'fixture_table_div': fixture_table_div
    }

    return render(request, 'pages/teams.html', context=context)

# players view--------------------------------------------------------------------------------------------------------------------------
def players(request):
    players = get_players()
    players = players[['web_name', 'position', 'team_abbr', 'cost', 'games', 'mpg', 'ppg', 'gpg', 'gcpg', 'apg', 'cspg', 'bppg']]
    source = ColumnDataSource(players)
    og_source = ColumnDataSource(players)
    teams = [
        "ALL", "ARS", "AVL", "BOU", "BRI", "BUR", "CHE", "CRY", "EVE",
        "LEI", "LIV", "MCI", "MUN", "NEW", "NOR", "SHU", "SOU",
        "TOT", "WAT", "WHU", "WOL" 
    ]
    positions = ["ALL", "GKP", "DEF", "MID", "FWD"]
    costs = ["4.0", "5.0", "6.0", "7.0", "8.0", "9.0", "10.0", "11.0", "12.0", "13.0"]
    columns = [
        TableColumn(field="web_name", title="Name", formatter=StringFormatter(font_style="bold")),
        TableColumn(field="position", title="Position"),
        TableColumn(field="team_abbr", title="Team"),
        TableColumn(field="cost", title="Cost"),
        TableColumn(field="games", title="Games Played"),
        TableColumn(field="mpg", title="Minutes pg"),
        TableColumn(field="ppg", title="Points pg"),
        TableColumn(field="gpg", title="Goals pg"),
        TableColumn(field="gcpg", title="Goals Conceded pg"),
        TableColumn(field="apg", title="Assists pg"),
        TableColumn(field="cspg", title="Clean Sheets pg"),
        TableColumn(field="bppg", title="Bonus Points pg"),
    ]
    table = DataTable(source=source, columns=columns,  width=1250, height=600)

    # callback code to be used by all the filter widgets
    # requires (source, original_source, country_select_obj, year_select_obj, target_object)
    callback_js = """
        var data = source.data;
        var og_data = og_source.data;
        var team = team_select_obj.value;
        console.log("team: " + team);
        var pos = pos_select_obj.value;
        console.log("position: " + pos);
        var maxCost = cost_select_obj.value;
        console.log("max cost: " + maxCost);
        for (var key in og_data) {
            data[key] = [];
            for (var i = 0; i < og_data['team_abbr'].length; ++i) {
                if ((team === "ALL" || og_data['team_abbr'][i] === team) &&
                (pos === "ALL" || og_data['position'][i] === pos) &&
                (og_data['cost'][i] <= parseFloat(maxCost) )) {
                    data[key].push(og_data[key][i]);
                }
            }
        }

        source.change.emit();
        target_obj.change.emit();
        """

    team_select = Select(title="Team:", value=teams[0], options=teams)
    pos_select = Select(title="Position:", value=positions[0], options=positions)
    cost_select = Select(title="Max Cost:", value=costs[9], options=costs)

    # now define the callback objects now that the filter widgets exist
    callback = CustomJS(
        args=dict(
            source=source, og_source=og_source, 
            team_select_obj=team_select, pos_select_obj=pos_select,
            cost_select_obj=cost_select, target_obj=table
        ), 
        code=callback_js
    )
    team_select.js_on_change('value', callback)
    pos_select.js_on_change('value', callback)
    cost_select.js_on_change('value', callback)

    selects = column(team_select, pos_select, cost_select)
    layout = row(selects, table)
    table_script, table_div = components(layout)
    context = {
        'table_script':table_script, 'table_div': table_div
    }
    return render(request, 'pages/players.html', context=context)

# gkps view--------------------------------------------------------------------------------------------------------------------------
def gkps(request):
    #TODO: create bokeh components for roi,home/away,etc. plots and return them to render

    #ROI---------------------------------------------------------------------------------------------------------------------
    ratings = get_team_ratings()
    current_gw = ratings['GW'].max()
    max_minutes = current_gw * 90
    players = fpl_player()
    players_gkp = players.loc[players['position'] == 'GKP']
    players_gkp_roi = players_gkp[['id', 'web_name', 'minutes','total_points', 'cost', 'team_abbr', 'team','selected_by_percent']]
    players_gkp_roi['ppc'] = players_gkp_roi['total_points'] / players_gkp_roi['cost']
    players_gkp_roi['modified_ppc'] = (players_gkp_roi['total_points'] / players_gkp_roi['cost']) * (players_gkp_roi['minutes'] / max_minutes)
    players_gkp_roi = players_gkp_roi.loc[players_gkp_roi['minutes'] > 0]
    agg_df = players_gkp_roi.groupby(['web_name']).mean()
    agg_df = agg_df.reset_index()
    avg_ppc = agg_df['ppc'].mean()
    avg_mppc = agg_df['modified_ppc'].mean()
    
    TOOLS="crosshair,pan,box_zoom,reset,hover,previewsave"
    
    #source = ColumnDataSource(players_gkp_roi)
    #og_source = ColumnDataSource(players_gkp_roi)

    data_source = ColumnDataSource(players_gkp_roi)
    source = ColumnDataSource(dict(web_name=[], ppc=[], modified_ppc=[], team_abbr=[], selected_by_percent=[]))

    roi_plot = figure(x_axis_label='Name', y_axis_label='ROI', title=' Player ROI: Goalkeepers (Click Legend to toggle averages)', 
               plot_width=1300, plot_height=600, x_range=players_gkp_roi["web_name"],tools=TOOLS, toolbar_location="above")

    roi = roi_plot.circle("web_name", "ppc", source=source, color='blue', alpha=0.8, size=7),
    mod_roi = roi_plot.circle("web_name", "modified_ppc", source=source, color='green', alpha=0.8, size=7)

    avg_ppc_line = roi_plot.line("web_name", avg_ppc, color='blue', alpha=0.4, source=ColumnDataSource(players_gkp_roi))
    avg_ppc_line.visible = False
    avg_mppc_line = roi_plot.line("web_name", avg_mppc, color='green', alpha=0.4, source=ColumnDataSource(players_gkp_roi))
    avg_mppc_line.visible = False

    roi_legend = Legend(items=[], location=(70,20), orientation="horizontal", click_policy='hide', 
        glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    roi_legend.items.append(LegendItem(label="Average ROI", renderers=[avg_ppc_line]))
    roi_legend.items.append(LegendItem(label="Average Modified ROI", renderers=[avg_mppc_line]))
    roi_plot.add_layout(roi_legend, 'below')
    
    roi_hover =roi_plot.select(dict(type=HoverTool))
    roi_hover.tooltips = OrderedDict([
            ("Name", "@web_name"),
            ("Team", "@team_abbr"),
            ("ROI", "@ppc"),
            ("Modified ROI", "@modified_ppc"),
            ("Selected by Percent", "@selected_by_percent")
        ])
    roi_plot.xaxis.major_label_orientation = math.pi/2
    
    
    teams = [
        "ARS", "AVL", "BOU", "BHA",
        "BUR", "CHE", "CRY", "EVE",
        "LEI", "LIV", "MCI", "MUN",
        "NEW", "NOR", "SHU", "SOU",
        "TOT", "WAT", "WHU", "WOL"
    ]
    #TODO: Figure out why all button is not working as envisioned
    

    # callback code to be used by all the filter widgets
    # requires (source, original_source, country_select_obj, year_select_obj, target_object)
    code = """
        var data = data_source.data;
        var s_data = source.data;
        var abbr = data['team_abbr'];
        var teams = team_selection_obj.active.map(x => team_selection_obj.labels[x]);
        console.log("teams: " + teams);
        var names = data['web_name'];
        var roi = data['ppc'];
        var modRoi = data['modified_ppc'];
        var selected = data['selected_by_percent'];
        var newNames = s_data['web_name'];
        newNames.length = 0;
        var newRoi = s_data['ppc'];
        newRoi.length = 0;
        var newMod = s_data['modified_ppc'];
        newMod.length = 0;
        var newAbbr = s_data['team_abbr'];
        newAbbr.length = 0;
        var newSelected = s_data['selected_by_percent'];
        newSelected.length = 0;
        for (var i = 0; i < names.length; i++) {
            if (teams.indexOf(abbr[i]) >= 0) {
                newNames.push(names[i]);
                newRoi.push(roi[i]);
                newMod.push(modRoi[i]);
                newAbbr.push(abbr[i]);
                newSelected.push(selected[i]);
            }
        }
        console.log("names: " + newNames);
        console.log("ROIs: " + newRoi);
        console.log("Modified ROIs: " + newMod);
        console.log("Teams: " + newAbbr);
        source.change.emit();
        target_obj.change.emit();
    """

    team_selection = CheckboxButtonGroup(labels=teams, active = [0, 1])

    clear_all = Button(label="Clear all")
    clear_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = []
    """))

    select_all = Button(label="Select all")
    select_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    """))


    # now define the callback objects now that the filter widgets exist
    callback = CustomJS(
        args=dict(
            data_source=data_source, source=source, team_selection_obj=team_selection, target_obj=roi_plot
        ), 
        code=code
    )
    team_selection.js_on_change('active', callback)
    all_controls = row(select_all, clear_all)
    selects = column(all_controls, team_selection)
    roi_plot_layout = column(selects, roi_plot)
    roi_script, roi_div = components(roi_plot_layout)


    #HOME/AWAY---------------------------------------------------------------------------------------------------------------------
    gkps_home_away = get_gkps_home_away()
    gws_by_player_home = gkps_home_away[0]
    gws_by_player_away = gkps_home_away[1]

    avg_pts_home = gws_by_player_home['avg_points'].mean()
    avg_pts_away = gws_by_player_away['avg_points'].mean()

    max45_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] < 4.5])
    max5_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(4.5, 4.9)])
    max55_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.0, 5.4)])
    max6_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.5, 5.9)])
    min6_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] >= 6.0])

    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    home_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Home Performers: Goalkeepers (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_home["web_name"],tools=TOOLS, toolbar_location="above")
    sect45_home = home_plot.circle("web_name", "avg_points", source=max45_home, color='color', alpha=0.8, size=7)
    sect5_home = home_plot.circle("web_name", "avg_points", source=max5_home, color='color', alpha=0.8, size=7)
    sect55_home = home_plot.circle("web_name", "avg_points", source=max55_home, color='color', alpha=0.8, size=7) 
    sect6_home = home_plot.circle("web_name", "avg_points", source=max6_home, color='color', alpha=0.8, size=7)
    sect7_home = home_plot.circle("web_name", "avg_points", source=min6_home, color='color', alpha=0.8, size=7)
    avg_pts_home_line = home_plot.line("web_name", avg_pts_home, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_home))
    avg_pts_home_line.visible = False

    home_legend = Legend(items=[("Less than 4.5" , [sect45_home]), ("4.5 to 4.9", [sect5_home]), ("5.0 to 5.4" , [sect55_home]), 
                             ("5.5 to 5.9", [sect6_home]), ("6.0 and over" , [sect7_home]), ("Average Home Tally", [avg_pts_home_line])],
                      location=(70,20), orientation="horizontal", click_policy='hide',
                    glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    home_plot.add_layout(home_legend, 'below')
    hover_home =home_plot.select(dict(type=HoverTool))
    hover_home.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    home_plot.xaxis.major_label_orientation = math.pi/2


    max45_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] < 4.5])
    max5_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(4.5, 4.9)])
    max55_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(5.0, 5.4)])
    max6_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(5.5, 5.9)])
    min6_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] >= 6.0])

    away_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Away Performers: Goalkeepers (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_away["web_name"],tools=TOOLS, toolbar_location="above")
    sect45_away = away_plot.circle("web_name", "avg_points", source=max45_away, color='color', alpha=0.8, size=7)
    sect5_away = away_plot.circle("web_name", "avg_points", source=max5_away, color='color', alpha=0.8, size=7)
    sect55_away = away_plot.circle("web_name", "avg_points", source=max55_away, color='color', alpha=0.8, size=7) 
    sect6_away = away_plot.circle("web_name", "avg_points", source=max6_away, color='color', alpha=0.8, size=7)
    sect7_away = away_plot.circle("web_name", "avg_points", source=min6_away, color='color', alpha=0.8, size=7)
    avg_pts_away_line = away_plot.line("web_name", avg_pts_away, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_away))
    avg_pts_away_line.visible = False

    away_legend = Legend(items=[("Less than 4.5" , [sect45_away]), ("4.5 to 4.9", [sect5_away]), ("5.0 to 5.4" , [sect55_away]), 
        ("5.5 to 5.9", [sect6_away]), ("6.0 and over" , [sect7_away]), ("Average Away Tally", [avg_pts_away_line])],
        location=(70,20), orientation="horizontal", click_policy='hide',glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    away_plot.add_layout(away_legend, 'below')
    hover_away =away_plot.select(dict(type=HoverTool))
    hover_away.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    away_plot.xaxis.major_label_orientation = math.pi/2 
    home_tab = Panel(child=home_plot, title='Home Form')
    away_tab = Panel(child=away_plot, title='Away Form')
    home_away_tabs = Tabs(tabs=[home_tab, away_tab], height=500)
    home_away_plot = layout(home_away_tabs)
    home_away_script, home_away_div = components(home_away_plot)

    #STRONG/WEAK---------------------------------------------------------------------------------------------------------------------
    gkps_strong_weak = get_strong_weak('GKP')
    top20_strong = gkps_strong_weak[0]

    strong_cds = ColumnDataSource(top20_strong)
    strong_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Strong Opponents: Goalkeepers', 
                   plot_width=1050, plot_height=600, x_range=top20_strong['web_name'], tools=TOOLS, toolbar_location="above")
    strong_plot.circle("web_name", "total_points", source=strong_cds, color='green', alpha=0.8, size=7)
    hover_strong =strong_plot.select(dict(type=HoverTool))
    hover_strong.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    strong_plot.xaxis.major_label_orientation = math.pi/4
    #WEAK-------------------------------------------------------------------
    top20_weak = gkps_strong_weak[1]
    weak_cds = ColumnDataSource(top20_weak)
    weak_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Weak Opponents: Goalkeepers', 
                   plot_width=1050, plot_height=600, x_range=top20_weak['web_name'], tools=TOOLS, toolbar_location="above")
    weak_plot.circle("web_name", "total_points", source=weak_cds, color='green', alpha=0.8, size=7)
    hover_weak =weak_plot.select(dict(type=HoverTool))
    hover_weak.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    weak_plot.xaxis.major_label_orientation = math.pi/4
    strong_tab = Panel(child=strong_plot, title='Against Strong Opponents')
    weak_tab = Panel(child=weak_plot, title='Against Weak Opponents')
    strong_weak_tabs = Tabs(tabs=[strong_tab, weak_tab], height=500)
    strong_weak_layout = layout(strong_weak_tabs)
    strong_weak_script, strong_weak_div = components(strong_weak_layout)

    #IN FORM/OUT OF FORM---------------------------------------------------------------------------------------------------------------------
    #IN FORM-------------------------------------------------------------------
    gkps_form = get_form('GKP')
    top20_form = gkps_form[0]
    in_form_cds = ColumnDataSource(top20_form)
    in_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' In Form Goalkeepers (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=top20_form['web_name'], tools=TOOLS, toolbar_location="above")

    in_form_plot.circle("web_name", "total_points", source=in_form_cds, color='green', alpha=0.8, size=7)
    hover_in_form =in_form_plot.select(dict(type=HoverTool))
    hover_in_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    in_form_plot.xaxis.major_label_orientation = math.pi/4

    #OUT OF FORM-------------------------------------------------------------------
    bot20_form = gkps_form[1]
    out_form_cds = ColumnDataSource(bot20_form)
    out_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Out of Form Goalkeepers (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=bot20_form['web_name'], tools=TOOLS, toolbar_location="above")

    out_form_plot.circle("web_name", "total_points", source=out_form_cds, color='green', alpha=0.8, size=7)
    hover_out_form =out_form_plot.select(dict(type=HoverTool))
    hover_out_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    out_form_plot.xaxis.major_label_orientation = math.pi/4
    in_form_tab = Panel(child=in_form_plot, title='In Form')
    out_form_tab = Panel(child=out_form_plot, title='Out of Form')
    form_tabs = Tabs(tabs=[in_form_tab, out_form_tab], height=500)
    form_layout = layout(form_tabs)
    form_script, form_div = components(form_layout)



    context = {
        'roi_script':roi_script, 'roi_div':roi_div, 
        'home_away_script':home_away_script, 'home_away_div':home_away_div,
        'strong_weak_script':strong_weak_script, 'strong_weak_div':strong_weak_div,
        'form_script':form_script, 'form_div':form_div
    }

    return render(request, 'pages/gkps.html', context=context)

# defs view--------------------------------------------------------------------------------------------------------------------------
def defs(request):
    #TODO: create bokeh components for roi,home/away,etc. plots and return them to render

    #ROI---------------------------------------------------------------------------------------------------------------------
    ratings = get_team_ratings()
    current_gw = ratings['GW'].max()
    max_minutes = current_gw * 90
    players = fpl_player()
    players_def = players.loc[players['position'] == 'DEF']
    players_def_roi = players_def[['id', 'web_name', 'minutes','total_points', 'cost', 'team_abbr', 'team','selected_by_percent']]
    players_def_roi['ppc'] = players_def_roi['total_points'] / players_def_roi['cost']
    players_def_roi['modified_ppc'] = (players_def_roi['total_points'] / players_def_roi['cost']) * (players_def_roi['minutes'] / max_minutes)
    players_def_roi = players_def_roi.loc[players_def_roi['minutes'] > 0]
    agg_df = players_def_roi.groupby(['web_name']).mean()
    agg_df = agg_df.reset_index()
    avg_ppc = agg_df['ppc'].mean()
    avg_mppc = agg_df['modified_ppc'].mean()
    
    TOOLS="crosshair,pan,box_zoom,reset,hover,previewsave"

    data_source = ColumnDataSource(players_def_roi)
    source = ColumnDataSource(dict(web_name=[], ppc=[], modified_ppc=[], team_abbr=[], selected_by_percent=[]))

    roi_plot = figure(x_axis_label='Name', y_axis_label='ROI', title=' Player ROI: Defenders (Click Legend to toggle averages)', 
               plot_width=2200, plot_height=600, x_range=players_def_roi["web_name"],tools=TOOLS, toolbar_location="above")

    roi = roi_plot.circle("web_name", "ppc", source=source, color='blue', alpha=0.8, size=7),
    mod_roi = roi_plot.circle("web_name", "modified_ppc", source=source, color='green', alpha=0.8, size=7)

    avg_ppc_line = roi_plot.line("web_name", avg_ppc, color='blue', alpha=0.4, source=data_source)
    avg_ppc_line.visible = False
    avg_mppc_line = roi_plot.line("web_name", avg_mppc, color='green', alpha=0.4, source=data_source)
    avg_mppc_line.visible = False

    roi_legend = Legend(items=[], location=(70,20), orientation="horizontal", click_policy='hide', 
        glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    roi_legend.items.append(LegendItem(label="Average ROI", renderers=[avg_ppc_line]))
    roi_legend.items.append(LegendItem(label="Average Modified ROI", renderers=[avg_mppc_line]))
    roi_plot.add_layout(roi_legend, 'below')
    
    roi_hover =roi_plot.select(dict(type=HoverTool))
    roi_hover.tooltips = OrderedDict([
            ("Name", "@web_name"),
            ("Team", "@team_abbr"),
            ("ROI", "@ppc"),
            ("Modified ROI", "@modified_ppc"),
            ("Selected by Percent", "@selected_by_percent")
        ])
    roi_plot.xaxis.major_label_orientation = math.pi/2
    
    
    teams = [
        "ARS", "AVL", "BOU", "BHA",
        "BUR", "CHE", "CRY", "EVE",
        "LEI", "LIV", "MCI", "MUN",
        "NEW", "NOR", "SHU", "SOU",
        "TOT", "WAT", "WHU", "WOL"
    ]
    
    # callback code to be used by all the filter widgets
    # requires (source, original_source, country_select_obj, year_select_obj, target_object)
    code = """
        var data = data_source.data;
        var s_data = source.data;
        var abbr = data['team_abbr'];
        var teams = team_selection_obj.active.map(x => team_selection_obj.labels[x]);
        console.log("teams: " + teams);
        var names = data['web_name'];
        var roi = data['ppc'];
        var modRoi = data['modified_ppc'];
        var selected = data['selected_by_percent'];
        var newNames = s_data['web_name'];
        newNames.length = 0;
        var newRoi = s_data['ppc'];
        newRoi.length = 0;
        var newMod = s_data['modified_ppc'];
        newMod.length = 0;
        var newAbbr = s_data['team_abbr'];
        newAbbr.length = 0;
        var newSelected = s_data['selected_by_percent'];
        newSelected.length = 0;
        for (var i = 0; i < names.length; i++) {
            if (teams.indexOf(abbr[i]) >= 0) {
                newNames.push(names[i]);
                newRoi.push(roi[i]);
                newMod.push(modRoi[i]);
                newAbbr.push(abbr[i]);
                newSelected.push(selected[i]);
            }
        }
        console.log("names: " + newNames);
        console.log("ROIs: " + newRoi);
        console.log("Modified ROIs: " + newMod);
        console.log("Teams: " + newAbbr);
        source.change.emit();
        target_obj.change.emit();
    """

    team_selection = CheckboxButtonGroup(labels=teams, active = [0, 1])

    clear_all = Button(label="Clear all")
    clear_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = []
    """))

    select_all = Button(label="Select all")
    select_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    """))


    # now define the callback objects now that the filter widgets exist
    callback = CustomJS(
        args=dict(
            data_source=data_source, source=source, team_selection_obj=team_selection, target_obj=roi_plot
        ), 
        code=code
    )
    team_selection.js_on_change('active', callback)
    all_controls = row(select_all, clear_all)
    selects = column(all_controls, team_selection)
    roi_plot_layout = column(selects, roi_plot)
    roi_script, roi_div = components(roi_plot_layout)

    #HOME/AWAY---------------------------------------------------------------------------------------------------------------------
    defs_home_away = get_defs_home_away()
    gws_by_player_home = defs_home_away[0]
    gws_by_player_away = defs_home_away[1]

    avg_pts_home = gws_by_player_home['avg_points'].mean()
    avg_pts_away = gws_by_player_away['avg_points'].mean()

    max43_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] < 4.3])
    max48_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(4.3, 4.7)])
    max53_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(4.8, 5.2)])
    max58_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.3, 5.7)])
    max63_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.8, 6.2)])
    max68_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(6.3, 6.7)])
    max73_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(6.8, 7.2)])
    min73_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] >= 7.3])

    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    home_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Home Performers: Defenders (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_home["web_name"],tools=TOOLS, toolbar_location="above")
    sect1_home = home_plot.circle("web_name", "avg_points", source=max43_home, color='color', alpha=0.8, size=7)
    sect2_home = home_plot.circle("web_name", "avg_points", source=max48_home, color='color', alpha=0.8, size=7)
    sect3_home = home_plot.circle("web_name", "avg_points", source=max53_home, color='color', alpha=0.8, size=7) 
    sect4_home = home_plot.circle("web_name", "avg_points", source=max58_home, color='color', alpha=0.8, size=7)
    sect5_home = home_plot.circle("web_name", "avg_points", source=max63_home, color='color', alpha=0.8, size=7)
    sect6_home = home_plot.circle("web_name", "avg_points", source=max68_home, color='color', alpha=0.8, size=7)
    sect7_home = home_plot.circle("web_name", "avg_points", source=max73_home, color='color', alpha=0.8, size=7)
    sect8_home = home_plot.circle("web_name", "avg_points", source=min73_home, color='color', alpha=0.8, size=7)
    avg_pts_home_line = home_plot.line("web_name", avg_pts_home, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_home))
    avg_pts_home_line.visible = False

    home_legend = Legend(items=[("Less than 4.3" , [sect1_home]), ('4.3 to 4.7', [sect2_home]), ("4.8 to 5.2" , [sect3_home]), 
                             ("5.3 to 5.7", [sect4_home]), ("5.8 to 6.2" , [sect5_home]), ("6.3 to 6.7" , [sect6_home]), 
                            ('6.8 to 7.2', [sect7_home]), ("7.3 and over" , [sect8_home]), ("Average Home Tally", [avg_pts_home_line])],
                      location=(70,20), orientation="horizontal", click_policy='hide',
                    glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    home_plot.add_layout(home_legend, 'below')
    hover_home =home_plot.select(dict(type=HoverTool))
    hover_home.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    home_plot.xaxis.major_label_orientation = math.pi/2


    max43_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] < 4.3])
    max48_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(4.3, 4.7)])
    max53_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(4.8, 5.2)])
    max58_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(5.3, 5.7)])
    max63_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(5.8, 6.2)])
    max68_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(6.3, 6.7)])
    max73_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(6.8, 7.2)])
    min73_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] >= 7.3])

    away_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Away Performers: Defenders (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_away["web_name"],tools=TOOLS, toolbar_location="above")
    sect1_away = away_plot.circle("web_name", "avg_points", source=max43_away, color='color', alpha=0.8, size=7)
    sect2_away = away_plot.circle("web_name", "avg_points", source=max48_away, color='color', alpha=0.8, size=7)
    sect3_away = away_plot.circle("web_name", "avg_points", source=max53_away, color='color', alpha=0.8, size=7) 
    sect4_away = away_plot.circle("web_name", "avg_points", source=max58_away, color='color', alpha=0.8, size=7)
    sect5_away = away_plot.circle("web_name", "avg_points", source=max63_away, color='color', alpha=0.8, size=7)
    sect6_away = away_plot.circle("web_name", "avg_points", source=max68_away, color='color', alpha=0.8, size=7)
    sect7_away = away_plot.circle("web_name", "avg_points", source=max73_away, color='color', alpha=0.8, size=7)
    sect8_away = away_plot.circle("web_name", "avg_points", source=min73_away, color='color', alpha=0.8, size=7)
    avg_pts_away_line = away_plot.line("web_name", avg_pts_away, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_away))
    avg_pts_away_line.visible = False

    away_legend = Legend(items=[("Less than 4.3" , [sect1_away]), ('4.3 to 4.7', [sect2_away]), ("4.8 to 5.2" , [sect3_away]), 
                             ("5.3 to 5.7", [sect4_away]), ("5.8 to 6.2" , [sect5_away]), ("6.3 to 6.7" , [sect6_away]), 
                            ('6.8 to 7.2', [sect7_away]), ("7.3 and over" , [sect8_away]), ("Average Away Tally", [avg_pts_away_line])],
                      location=(70,20), orientation="horizontal", click_policy='hide',
                    glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    away_plot.add_layout(away_legend, 'below')
    hover_away =away_plot.select(dict(type=HoverTool))
    hover_away.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    away_plot.xaxis.major_label_orientation = math.pi/2 
    home_tab = Panel(child=home_plot, title='Home Form')
    away_tab = Panel(child=away_plot, title='Away Form')
    home_away_tabs = Tabs(tabs=[home_tab, away_tab], height=500)
    home_away_plot = layout(home_away_tabs)
    home_away_script, home_away_div = components(home_away_plot)

    #STRONG/WEAK---------------------------------------------------------------------------------------------------------------------
    #STRONG-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    defs_strong_weak = get_strong_weak('DEF')
    top20_strong = defs_strong_weak[0]
    top20_weak = defs_strong_weak[1]

    strong_cds = ColumnDataSource(top20_strong)
    strong_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Strong Opponents: Defenders', 
                   plot_width=1050, plot_height=600, x_range=top20_strong['web_name'], tools=TOOLS, toolbar_location="above")
    strong_plot.circle("web_name", "total_points", source=strong_cds, color='green', alpha=0.8, size=7)
    hover_strong =strong_plot.select(dict(type=HoverTool))
    hover_strong.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    strong_plot.xaxis.major_label_orientation = math.pi/4

    #WEAK-------------------------------------------------------------------
    weak_cds = ColumnDataSource(top20_weak)
    weak_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Weak Opponents: Defenders', 
                   plot_width=1050, plot_height=600, x_range=top20_weak['web_name'], tools=TOOLS, toolbar_location="above")
    weak_plot.circle("web_name", "total_points", source=weak_cds, color='green', alpha=0.8, size=7)
    hover_weak =weak_plot.select(dict(type=HoverTool))
    hover_weak.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    weak_plot.xaxis.major_label_orientation = math.pi/4
    strong_tab = Panel(child=strong_plot, title='Against Strong Opponents')
    weak_tab = Panel(child=weak_plot, title='Against Weak Opponents')
    strong_weak_tabs = Tabs(tabs=[strong_tab, weak_tab], height=500)
    strong_weak_layout = layout(strong_weak_tabs)
    strong_weak_script, strong_weak_div = components(strong_weak_layout)

    #IN FORM/OUT OF FORM---------------------------------------------------------------------------------------------------------------------
    #IN FORM-------------------------------------------------------------------
    defs_form = get_form('DEF')
    top20_form = defs_form[0]
    bot20_form = defs_form[1]
    in_form_cds = ColumnDataSource(top20_form)
    in_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' In Form Defenders (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=top20_form['web_name'], tools=TOOLS, toolbar_location="above")

    in_form_plot.circle("web_name", "total_points", source=in_form_cds, color='green', alpha=0.8, size=7)
    
    hover_in_form =in_form_plot.select(dict(type=HoverTool))
    hover_in_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    in_form_plot.xaxis.major_label_orientation = math.pi/4

    #OUT OF FORM-------------------------------------------------------------------
    bot20_form = defs_form[1]
    out_form_cds = ColumnDataSource(bot20_form)
    out_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Out of Form Defenders (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=bot20_form['web_name'], tools=TOOLS, toolbar_location="above")

    out_form_plot.circle("web_name", "total_points", source=out_form_cds, color='green', alpha=0.8, size=7)
    hover_out_form =out_form_plot.select(dict(type=HoverTool))
    hover_out_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    out_form_plot.xaxis.major_label_orientation = math.pi/4
    in_form_tab = Panel(child=in_form_plot, title='In Form')
    out_form_tab = Panel(child=out_form_plot, title='Out of Form')
    form_tabs = Tabs(tabs=[in_form_tab, out_form_tab], height=500)
    form_layout = layout(form_tabs)
    form_script, form_div = components(form_layout)



    context = {
        'roi_script':roi_script, 'roi_div':roi_div, 
        'home_away_script':home_away_script, 'home_away_div':home_away_div,
        'strong_weak_script':strong_weak_script, 'strong_weak_div':strong_weak_div,
        'form_script':form_script, 'form_div':form_div
    }

    return render(request, 'pages/defs.html', context=context)

# mids view--------------------------------------------------------------------------------------------------------------------------
def mids(request):
    #TODO: create bokeh components for roi,home/away,etc. plots and return them to render

    #ROI---------------------------------------------------------------------------------------------------------------------
    ratings = get_team_ratings()
    current_gw = ratings['GW'].max()
    max_minutes = current_gw * 90
    players = fpl_player()
    players_mid = players.loc[players['position'] == 'MID']
    players_mid_roi = players_mid[['id', 'web_name', 'minutes','total_points', 'cost', 'team_abbr', 'team','selected_by_percent']]
    players_mid_roi['ppc'] = players_mid_roi['total_points'] / players_mid_roi['cost']
    players_mid_roi['modified_ppc'] = (players_mid_roi['total_points'] / players_mid_roi['cost']) * (players_mid_roi['minutes'] / max_minutes)
    players_mid_roi = players_mid_roi.loc[players_mid_roi['minutes'] > 0]
    agg_df = players_mid_roi.groupby(['web_name']).mean()
    agg_df = agg_df.reset_index()
    avg_ppc = agg_df['ppc'].mean()
    avg_mppc = agg_df['modified_ppc'].mean()
    
    TOOLS="crosshair,pan,box_zoom,reset,hover,previewsave"

    data_source = ColumnDataSource(players_mid_roi)
    source = ColumnDataSource(dict(web_name=[], ppc=[], modified_ppc=[], team_abbr=[], selected_by_percent=[]))

    roi_plot = figure(x_axis_label='Name', y_axis_label='ROI', title=' Player ROI: Midfielders (Click Legend to toggle averages)', 
               plot_width=2900, plot_height=600, x_range=players_mid_roi["web_name"],tools=TOOLS, toolbar_location="above")

    roi = roi_plot.circle("web_name", "ppc", source=source, color='blue', alpha=0.8, size=7),
    mod_roi = roi_plot.circle("web_name", "modified_ppc", source=source, color='green', alpha=0.8, size=7)

    avg_ppc_line = roi_plot.line("web_name", avg_ppc, color='blue', alpha=0.4, source=data_source)
    avg_ppc_line.visible = False
    avg_mppc_line = roi_plot.line("web_name", avg_mppc, color='green', alpha=0.4, source=data_source)
    avg_mppc_line.visible = False

    roi_legend = Legend(items=[], location=(70,20), orientation="horizontal", click_policy='hide', 
        glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    roi_legend.items.append(LegendItem(label="Average ROI", renderers=[avg_ppc_line]))
    roi_legend.items.append(LegendItem(label="Average Modified ROI", renderers=[avg_mppc_line]))
    roi_plot.add_layout(roi_legend, 'below')
    
    roi_hover =roi_plot.select(dict(type=HoverTool))
    roi_hover.tooltips = OrderedDict([
            ("Name", "@web_name"),
            ("Team", "@team_abbr"),
            ("ROI", "@ppc"),
            ("Modified ROI", "@modified_ppc"),
            ("Selected by Percent", "@selected_by_percent")
        ])
    roi_plot.xaxis.major_label_orientation = math.pi/2
    
    
    teams = [
        "ARS", "AVL", "BOU", "BHA",
        "BUR", "CHE", "CRY", "EVE",
        "LEI", "LIV", "MCI", "MUN",
        "NEW", "NOR", "SHU", "SOU",
        "TOT", "WAT", "WHU", "WOL"
    ]
    
    # callback code to be used by all the filter widgets
    # requires (source, original_source, country_select_obj, year_select_obj, target_object)
    code = """
        var data = data_source.data;
        var s_data = source.data;
        var abbr = data['team_abbr'];
        var teams = team_selection_obj.active.map(x => team_selection_obj.labels[x]);
        console.log("teams: " + teams);
        var names = data['web_name'];
        var roi = data['ppc'];
        var modRoi = data['modified_ppc'];
        var selected = data['selected_by_percent'];
        var newNames = s_data['web_name'];
        newNames.length = 0;
        var newRoi = s_data['ppc'];
        newRoi.length = 0;
        var newMod = s_data['modified_ppc'];
        newMod.length = 0;
        var newAbbr = s_data['team_abbr'];
        newAbbr.length = 0;
        var newSelected = s_data['selected_by_percent'];
        newSelected.length = 0;
        for (var i = 0; i < names.length; i++) {
            if (teams.indexOf(abbr[i]) >= 0) {
                newNames.push(names[i]);
                newRoi.push(roi[i]);
                newMod.push(modRoi[i]);
                newAbbr.push(abbr[i]);
                newSelected.push(selected[i]);
            }
        }
        console.log("names: " + newNames);
        console.log("ROIs: " + newRoi);
        console.log("Modified ROIs: " + newMod);
        console.log("Teams: " + newAbbr);
        source.change.emit();
        target_obj.change.emit();
    """

    team_selection = CheckboxButtonGroup(labels=teams, active = [0, 1])

    clear_all = Button(label="Clear all")
    clear_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = []
    """))

    select_all = Button(label="Select all")
    select_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    """))


    # now define the callback objects now that the filter widgets exist
    callback = CustomJS(
        args=dict(
            data_source=data_source, source=source, team_selection_obj=team_selection, target_obj=roi_plot
        ), 
        code=code
    )
    team_selection.js_on_change('active', callback)
    all_controls = row(select_all, clear_all)
    selects = column(all_controls, team_selection)
    roi_plot_layout = column(selects, roi_plot)
    roi_script, roi_div = components(roi_plot_layout)

    #HOME/AWAY---------------------------------------------------------------------------------------------------------------------
    mids_home_away = get_mids_home_away()
    gws_by_player_home = mids_home_away[0]
    gws_by_player_away = mids_home_away[1]
    avg_pts_home = gws_by_player_home['avg_points'].mean()
    avg_pts_away = gws_by_player_away['avg_points'].mean()

    max5_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] < 5.0])
    max6_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.0, 5.9)])
    max7_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(6.0, 6.9)])
    max8_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(7.0, 7.9)])
    max9_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(8.0, 8.9)])
    max10_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(9.0, 9.9)])
    max11_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(10.0, 10.9)])
    max12_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(11.0, 11.9)])
    min12_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] >= 12.0])

    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    home_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Home Performers: Midfielders (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_home["web_name"],tools=TOOLS, toolbar_location="above")
    sect5_home = home_plot.circle("web_name", "avg_points", source=max5_home, color='color', alpha=0.8, size=7)
    sect6_home = home_plot.circle("web_name", "avg_points", source=max6_home, color='color', alpha=0.8, size=7)
    sect7_home = home_plot.circle("web_name", "avg_points", source=max7_home, color='color', alpha=0.8, size=7) 
    sect8_home = home_plot.circle("web_name", "avg_points", source=max8_home, color='color', alpha=0.8, size=7)
    sect9_home = home_plot.circle("web_name", "avg_points", source=max9_home, color='color', alpha=0.8, size=7)
    sect10_home = home_plot.circle("web_name", "avg_points", source=max10_home, color='color', alpha=0.8, size=7)
    sect11_home = home_plot.circle("web_name", "avg_points", source=max11_home, color='color', alpha=0.8, size=7)
    sect12_home = home_plot.circle("web_name", "avg_points", source=max12_home, color='color', alpha=0.8, size=7)
    sect13_home = home_plot.circle("web_name", "avg_points", source=min12_home, color='color', alpha=0.8, size=7)
    avg_pts_home_line = home_plot.line("web_name", avg_pts_home, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_home))
    avg_pts_home_line.visible = False

    home_legend = Legend(items=[("Less than 5.0" , [sect5_home]), ('5.0 to 5.9', [sect6_home]), ("6.0 to 6.9" , [sect7_home]), 
                             ("7.0 to 7.9", [sect8_home]), ("8.0 to 8.9" , [sect9_home]), ("9.0 to 9.9" , [sect10_home]), 
                            ('10.0 to 10.9', [sect11_home]), ("11.0 to 11.9" , [sect12_home]), ("12.0 and over", [sect13_home]), 
                            ("Average Home Tally", [avg_pts_home_line])],
                      location=(70,20), orientation="horizontal", click_policy='hide',
                    glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    home_plot.add_layout(home_legend, 'below')
    hover_home =home_plot.select(dict(type=HoverTool))
    hover_home.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    home_plot.xaxis.major_label_orientation = math.pi/2


    max5_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] < 5.0])
    max6_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(5.0, 5.9)])
    max7_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(6.0, 6.9)])
    max8_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(7.0, 7.9)])
    max9_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(8.0, 8.9)])
    max10_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(9.0, 9.9)])
    max11_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(10.0, 10.9)])
    max12_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(11.0, 11.9)])
    min12_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] >= 12.0])

    away_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Away Performers: Midfielders (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_away["web_name"],tools=TOOLS, toolbar_location="above")
    sect5_away = away_plot.circle("web_name", "avg_points", source=max5_away, color='color', alpha=0.8, size=7)
    sect6_away = away_plot.circle("web_name", "avg_points", source=max6_away, color='color', alpha=0.8, size=7)
    sect7_away = away_plot.circle("web_name", "avg_points", source=max7_away, color='color', alpha=0.8, size=7) 
    sect8_away = away_plot.circle("web_name", "avg_points", source=max8_away, color='color', alpha=0.8, size=7)
    sect9_away = away_plot.circle("web_name", "avg_points", source=max9_away, color='color', alpha=0.8, size=7)
    sect10_away = away_plot.circle("web_name", "avg_points", source=max10_away, color='color', alpha=0.8, size=7)
    sect11_away = away_plot.circle("web_name", "avg_points", source=max11_away, color='color', alpha=0.8, size=7)
    sect12_away = away_plot.circle("web_name", "avg_points", source=max12_away, color='color', alpha=0.8, size=7)
    sect13_away = away_plot.circle("web_name", "avg_points", source=min12_away, color='color', alpha=0.8, size=7)
    avg_pts_away_line = away_plot.line("web_name", avg_pts_away, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_away))
    avg_pts_away_line.visible = False

    away_legend = Legend(items=[("Less than 5.0" , [sect5_away]), ('5.0 to 5.9', [sect6_away]), ("6.0 to 6.9" , [sect7_away]), 
        ("7.0 to 7.9", [sect8_away]), ("8.0 to 8.9" , [sect9_away]), ("9.0 to 9.9" , [sect10_away]), ('10.0 to 10.9', [sect11_away]), 
        ("11.0 to 11.9" , [sect12_away]), ("12.0 and over", [sect13_away]), ("Average Away Tally", [avg_pts_away_line])],
        location=(70,20), orientation="horizontal", click_policy='hide',glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    away_plot.add_layout(away_legend, 'below')
    hover_away =away_plot.select(dict(type=HoverTool))
    hover_away.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    away_plot.xaxis.major_label_orientation = math.pi/2 
    home_tab = Panel(child=home_plot, title='Home Form')
    away_tab = Panel(child=away_plot, title='Away Form')
    home_away_tabs = Tabs(tabs=[home_tab, away_tab], height=500)
    home_away_plot = layout(home_away_tabs)
    home_away_script, home_away_div = components(home_away_plot)

    #STRONG/WEAK---------------------------------------------------------------------------------------------------------------------
    #STRONG-------------------------------------------------------------------
    mids_strong_weak = get_strong_weak('MID')
    top20_strong = mids_strong_weak[0]
    top20_weak = mids_strong_weak[1]
    strong_cds = ColumnDataSource(top20_strong)
    strong_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Strong Opponents: Midfielders', 
                   plot_width=1050, plot_height=600, x_range=top20_strong['web_name'], tools=TOOLS, toolbar_location="above")
    strong_plot.circle("web_name", "total_points", source=strong_cds, color='green', alpha=0.8, size=7)
    hover_strong =strong_plot.select(dict(type=HoverTool))
    hover_strong.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    strong_plot.xaxis.major_label_orientation = math.pi/4

    #WEAK-------------------------------------------------------------------
    weak_cds = ColumnDataSource(top20_weak)
    weak_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Weak Opponents: Midfielders', 
                   plot_width=1050, plot_height=600, x_range=top20_weak['web_name'], tools=TOOLS, toolbar_location="above")
    weak_plot.circle("web_name", "total_points", source=weak_cds, color='green', alpha=0.8, size=7)
    hover_weak =weak_plot.select(dict(type=HoverTool))
    hover_weak.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    weak_plot.xaxis.major_label_orientation = math.pi/4
    strong_tab = Panel(child=strong_plot, title='Against Strong Opponents')
    weak_tab = Panel(child=weak_plot, title='Against Weak Opponents')
    strong_weak_tabs = Tabs(tabs=[strong_tab, weak_tab], height=500)
    strong_weak_layout = layout(strong_weak_tabs)
    strong_weak_script, strong_weak_div = components(strong_weak_layout)

    #IN FORM/OUT OF FORM---------------------------------------------------------------------------------------------------------------------
    #IN FORM-------------------------------------------------------------------
    mids_form = get_form('MID')
    top20_form = mids_form[0]
    bot20_form = mids_form[1]
    in_form_cds = ColumnDataSource(top20_form)
    in_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' In Form Midfielders (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=top20_form['web_name'], tools=TOOLS, toolbar_location="above")

    in_form_plot.circle("web_name", "total_points", source=in_form_cds, color='green', alpha=0.8, size=7)
    hover_in_form =in_form_plot.select(dict(type=HoverTool))
    hover_in_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    in_form_plot.xaxis.major_label_orientation = math.pi/4

    #OUT OF FORM-------------------------------------------------------------------
    out_form_cds = ColumnDataSource(bot20_form)
    out_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Out of Form Midfielders (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=bot20_form['web_name'], tools=TOOLS, toolbar_location="above")

    out_form_plot.circle("web_name", "total_points", source=out_form_cds, color='green', alpha=0.8, size=7)
    
    hover_out_form =out_form_plot.select(dict(type=HoverTool))
    hover_out_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    out_form_plot.xaxis.major_label_orientation = math.pi/4
    in_form_tab = Panel(child=in_form_plot, title='In Form')
    out_form_tab = Panel(child=out_form_plot, title='Out of Form')
    form_tabs = Tabs(tabs=[in_form_tab, out_form_tab], height=500)
    form_layout = layout(form_tabs)
    form_script, form_div = components(form_layout)



    context = {
        'roi_script':roi_script, 'roi_div':roi_div, 
        'home_away_script':home_away_script, 'home_away_div':home_away_div,
        'strong_weak_script':strong_weak_script, 'strong_weak_div':strong_weak_div,
        'form_script':form_script, 'form_div':form_div
    }

    return render(request, 'pages/mids.html', context=context)




# fwds view--------------------------------------------------------------------------------------------------------------------------
def fwds(request):
    #TODO: create bokeh components for roi,home/away,etc. plots and return them to render

    #ROI---------------------------------------------------------------------------------------------------------------------
    ratings = get_team_ratings()
    current_gw = ratings['GW'].max()
    max_minutes = current_gw * 90
    players = fpl_player()
    players_fwd = players.loc[players['position'] == 'FWD']
    players_fwd_roi = players_fwd[['id', 'web_name', 'minutes','total_points', 'cost', 'team_abbr', 'team','selected_by_percent']]
    players_fwd_roi['ppc'] = players_fwd_roi['total_points'] / players_fwd_roi['cost']
    players_fwd_roi['modified_ppc'] = (players_fwd_roi['total_points'] / players_fwd_roi['cost']) * (players_fwd_roi['minutes'] / max_minutes)
    players_fwd_roi = players_fwd_roi.loc[players_fwd_roi['minutes'] > 0]
    agg_df = players_fwd_roi.groupby(['web_name']).mean()
    agg_df = agg_df.reset_index()
    avg_ppc = agg_df['ppc'].mean()
    avg_mppc = agg_df['modified_ppc'].mean()
    
    TOOLS="crosshair,pan,box_zoom,reset,hover,previewsave"

    data_source = ColumnDataSource(players_fwd_roi)
    source = ColumnDataSource(dict(web_name=[], ppc=[], modified_ppc=[], team_abbr=[], selected_by_percent=[]))

    roi_plot = figure(x_axis_label='Name', y_axis_label='ROI', title=' Player ROI: Forwards (Click Legend to toggle averages)', 
               plot_width=1500, plot_height=600, x_range=players_fwd_roi["web_name"],tools=TOOLS, toolbar_location="above")

    roi = roi_plot.circle("web_name", "ppc", source=source, color='blue', alpha=0.8, size=7),
    mod_roi = roi_plot.circle("web_name", "modified_ppc", source=source, color='green', alpha=0.8, size=7)

    avg_ppc_line = roi_plot.line("web_name", avg_ppc, color='blue', alpha=0.4, source=data_source)
    avg_ppc_line.visible = False
    avg_mppc_line = roi_plot.line("web_name", avg_mppc, color='green', alpha=0.4, source=data_source)
    avg_mppc_line.visible = False

    roi_legend = Legend(items=[], location=(70,20), orientation="horizontal", click_policy='hide', 
        glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    roi_legend.items.append(LegendItem(label="Average ROI", renderers=[avg_ppc_line]))
    roi_legend.items.append(LegendItem(label="Average Modified ROI", renderers=[avg_mppc_line]))
    roi_plot.add_layout(roi_legend, 'below')
    
    roi_hover =roi_plot.select(dict(type=HoverTool))
    roi_hover.tooltips = OrderedDict([
            ("Name", "@web_name"),
            ("Team", "@team_abbr"),
            ("ROI", "@ppc"),
            ("Modified ROI", "@modified_ppc"),
            ("Selected by Percent", "@selected_by_percent")
        ])
    roi_plot.xaxis.major_label_orientation = math.pi/2
    
    
    teams = [
        "ARS", "AVL", "BOU", "BHA",
        "BUR", "CHE", "CRY", "EVE",
        "LEI", "LIV", "MCI", "MUN",
        "NEW", "NOR", "SHU", "SOU",
        "TOT", "WAT", "WHU", "WOL"
    ]
    
    # callback code to be used by all the filter widgets
    # requires (source, original_source, country_select_obj, year_select_obj, target_object)
    code = """
        var data = data_source.data;
        var s_data = source.data;
        var abbr = data['team_abbr'];
        var teams = team_selection_obj.active.map(x => team_selection_obj.labels[x]);
        console.log("teams: " + teams);
        var names = data['web_name'];
        var roi = data['ppc'];
        var modRoi = data['modified_ppc'];
        var selected = data['selected_by_percent'];
        var newNames = s_data['web_name'];
        newNames.length = 0;
        var newRoi = s_data['ppc'];
        newRoi.length = 0;
        var newMod = s_data['modified_ppc'];
        newMod.length = 0;
        var newAbbr = s_data['team_abbr'];
        newAbbr.length = 0;
        var newSelected = s_data['selected_by_percent'];
        newSelected.length = 0;
        for (var i = 0; i < names.length; i++) {
            if (teams.indexOf(abbr[i]) >= 0) {
                newNames.push(names[i]);
                newRoi.push(roi[i]);
                newMod.push(modRoi[i]);
                newAbbr.push(abbr[i]);
                newSelected.push(selected[i]);
            }
        }
        console.log("names: " + newNames);
        console.log("ROIs: " + newRoi);
        console.log("Modified ROIs: " + newMod);
        console.log("Teams: " + newAbbr);
        source.change.emit();
        target_obj.change.emit();
    """

    team_selection = CheckboxButtonGroup(labels=teams, active = [0, 1])

    clear_all = Button(label="Clear all")
    clear_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = []
    """))

    select_all = Button(label="Select all")
    select_all.js_on_click(CustomJS(args=dict(team_selection=team_selection), code="""
        team_selection.active = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    """))


    # now define the callback objects now that the filter widgets exist
    callback = CustomJS(
        args=dict(
            data_source=data_source, source=source, team_selection_obj=team_selection, target_obj=roi_plot
        ), 
        code=code
    )
    team_selection.js_on_change('active', callback)
    all_controls = row(select_all, clear_all)
    selects = column(all_controls, team_selection)
    roi_plot_layout = column(selects, roi_plot)
    roi_script, roi_div = components(roi_plot_layout)

    #HOME/AWAY---------------------------------------------------------------------------------------------------------------------
    fwds_home_away = get_fwds_home_away()
    gws_by_player_home = fwds_home_away[0]
    gws_by_player_away = fwds_home_away[1]
    avg_pts_home = gws_by_player_home['avg_points'].mean()
    avg_pts_away = gws_by_player_away['avg_points'].mean()

    max5_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] < 5.0])
    max6_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.0, 5.9)])
    max7_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(6.0, 6.9)])
    max8_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(7.0, 7.9)])
    max9_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(8.0, 8.9)])
    max10_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(9.0, 9.9)])
    max11_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(10.0, 10.9)])
    max12_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(11.0, 11.9)])
    min12_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] >= 12.0])

    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    home_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Home Performers: Forwards (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_home["web_name"],tools=TOOLS, toolbar_location="above")
    sect5_home = home_plot.circle("web_name", "avg_points", source=max5_home, color='color', alpha=0.8, size=7)
    sect6_home = home_plot.circle("web_name", "avg_points", source=max6_home, color='color', alpha=0.8, size=7)
    sect7_home = home_plot.circle("web_name", "avg_points", source=max7_home, color='color', alpha=0.8, size=7) 
    sect8_home = home_plot.circle("web_name", "avg_points", source=max8_home, color='color', alpha=0.8, size=7)
    sect9_home = home_plot.circle("web_name", "avg_points", source=max9_home, color='color', alpha=0.8, size=7)
    sect10_home = home_plot.circle("web_name", "avg_points", source=max10_home, color='color', alpha=0.8, size=7)
    sect11_home = home_plot.circle("web_name", "avg_points", source=max11_home, color='color', alpha=0.8, size=7)
    sect12_home = home_plot.circle("web_name", "avg_points", source=max12_home, color='color', alpha=0.8, size=7)
    sect13_home = home_plot.circle("web_name", "avg_points", source=min12_home, color='color', alpha=0.8, size=7)
    avg_pts_home_line = home_plot.line("web_name", avg_pts_home, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_home))
    avg_pts_home_line.visible = False

    home_legend = Legend(items=[("Less than 5.0" , [sect5_home]), ('5.0 to 5.9', [sect6_home]), ("6.0 to 6.9" , [sect7_home]), 
                             ("7.0 to 7.9", [sect8_home]), ("8.0 to 8.9" , [sect9_home]), ("9.0 to 9.9" , [sect10_home]), 
                            ('10.0 to 10.9', [sect11_home]), ("11.0 to 11.9" , [sect12_home]), ("12.0 and over", [sect13_home]), 
                            ("Average Home Tally", [avg_pts_home_line])],
                      location=(70,20), orientation="horizontal", click_policy='hide',
                    glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    home_plot.add_layout(home_legend, 'below')
    hover_home =home_plot.select(dict(type=HoverTool))
    hover_home.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    home_plot.xaxis.major_label_orientation = math.pi/2


    max5_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] < 5.0])
    max6_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(5.0, 5.9)])
    max7_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(6.0, 6.9)])
    max8_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(7.0, 7.9)])
    max9_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(8.0, 8.9)])
    max10_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(9.0, 9.9)])
    max11_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(10.0, 10.9)])
    max12_away = ColumnDataSource(gws_by_player_away[gws_by_player_away['cost'].between(11.0, 11.9)])
    min12_away = ColumnDataSource(gws_by_player_away.loc[gws_by_player_away['cost'] >= 12.0])

    away_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Away Performers: Forwards (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_away["web_name"],tools=TOOLS, toolbar_location="above")
    sect5_away = away_plot.circle("web_name", "avg_points", source=max5_away, color='color', alpha=0.8, size=7)
    sect6_away = away_plot.circle("web_name", "avg_points", source=max6_away, color='color', alpha=0.8, size=7)
    sect7_away = away_plot.circle("web_name", "avg_points", source=max7_away, color='color', alpha=0.8, size=7) 
    sect8_away = away_plot.circle("web_name", "avg_points", source=max8_away, color='color', alpha=0.8, size=7)
    sect9_away = away_plot.circle("web_name", "avg_points", source=max9_away, color='color', alpha=0.8, size=7)
    sect10_away = away_plot.circle("web_name", "avg_points", source=max10_away, color='color', alpha=0.8, size=7)
    sect11_away = away_plot.circle("web_name", "avg_points", source=max11_away, color='color', alpha=0.8, size=7)
    sect12_away = away_plot.circle("web_name", "avg_points", source=max12_away, color='color', alpha=0.8, size=7)
    sect13_away = away_plot.circle("web_name", "avg_points", source=min12_away, color='color', alpha=0.8, size=7)
    avg_pts_away_line = away_plot.line("web_name", avg_pts_away, color='black', alpha=0.4, source=ColumnDataSource(gws_by_player_away))
    avg_pts_away_line.visible = False

    away_legend = Legend(items=[("Less than 5.0" , [sect5_away]), ('5.0 to 5.9', [sect6_away]), ("6.0 to 6.9" , [sect7_away]), 
        ("7.0 to 7.9", [sect8_away]), ("8.0 to 8.9" , [sect9_away]), ("9.0 to 9.9" , [sect10_away]), ('10.0 to 10.9', [sect11_away]), 
        ("11.0 to 11.9" , [sect12_away]), ("12.0 and over", [sect13_away]), ("Average Away Tally", [avg_pts_away_line])],
        location=(70,20), orientation="horizontal", click_policy='hide',glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    away_plot.add_layout(away_legend, 'below')
    hover_away =away_plot.select(dict(type=HoverTool))
    hover_away.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Points Avg", "@avg_points"),
        ("Price", "@cost")
    ])
    away_plot.xaxis.major_label_orientation = math.pi/2 
    home_tab = Panel(child=home_plot, title='Home Form')
    away_tab = Panel(child=away_plot, title='Away Form')
    home_away_tabs = Tabs(tabs=[home_tab, away_tab], height=500)
    home_away_plot = layout(home_away_tabs)
    home_away_script, home_away_div = components(home_away_plot)

    #STRONG/WEAK---------------------------------------------------------------------------------------------------------------------
    #STRONG-------------------------------------------------------------------
    fwds_strong_weak = get_strong_weak('FWD')
    top20_strong = fwds_strong_weak[0]
    top20_weak = fwds_strong_weak[1]
    strong_cds = ColumnDataSource(top20_strong)
    strong_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Strong Opponents: Forwards', 
                   plot_width=1050, plot_height=600, x_range=top20_strong['web_name'], tools=TOOLS, toolbar_location="above")
    strong_plot.circle("web_name", "total_points", source=strong_cds, color='green', alpha=0.8, size=7)
    hover_strong =strong_plot.select(dict(type=HoverTool))
    hover_strong.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    strong_plot.xaxis.major_label_orientation = math.pi/4

    #WEAK-------------------------------------------------------------------
    weak_cds = ColumnDataSource(top20_weak)
    weak_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Weak Opponents: Forwards', 
                   plot_width=1050, plot_height=600, x_range=top20_weak['web_name'], tools=TOOLS, toolbar_location="above")
    weak_plot.circle("web_name", "total_points", source=weak_cds, color='green', alpha=0.8, size=7)
    hover_weak =weak_plot.select(dict(type=HoverTool))
    hover_weak.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    weak_plot.xaxis.major_label_orientation = math.pi/4
    strong_tab = Panel(child=strong_plot, title='Against Strong Opponents')
    weak_tab = Panel(child=weak_plot, title='Against Weak Opponents')
    strong_weak_tabs = Tabs(tabs=[strong_tab, weak_tab], height=500)
    strong_weak_layout = layout(strong_weak_tabs)
    strong_weak_script, strong_weak_div = components(strong_weak_layout)

    #IN FORM/OUT OF FORM---------------------------------------------------------------------------------------------------------------------
    #IN FORM-------------------------------------------------------------------
    fwds_form = get_form('FWD')
    top20_form = fwds_form[0]
    bot20_form = fwds_form[1]
    in_form_cds = ColumnDataSource(top20_form)
    in_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' In Form Forwards (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=top20_form['web_name'], tools=TOOLS, toolbar_location="above")

    in_form_plot.circle("web_name", "total_points", source=in_form_cds, color='green', alpha=0.8, size=7)
    
    hover_in_form =in_form_plot.select(dict(type=HoverTool))
    hover_in_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    in_form_plot.xaxis.major_label_orientation = math.pi/4

    #OUT OF FORM-------------------------------------------------------------------
    out_form_cds = ColumnDataSource(bot20_form)
    out_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Out of Form Forwards (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=bot20_form['web_name'], tools=TOOLS, toolbar_location="above")

    out_form_plot.circle("web_name", "total_points", source=out_form_cds, color='green', alpha=0.8, size=7)
    
    hover_out_form =out_form_plot.select(dict(type=HoverTool))
    hover_out_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    out_form_plot.xaxis.major_label_orientation = math.pi/4
    in_form_tab = Panel(child=in_form_plot, title='In Form')
    out_form_tab = Panel(child=out_form_plot, title='Out of Form')
    form_tabs = Tabs(tabs=[in_form_tab, out_form_tab], height=500)
    form_layout = layout(form_tabs)
    form_script, form_div = components(form_layout)



    context = {
        'roi_script':roi_script, 'roi_div':roi_div, 
        'home_away_script':home_away_script, 'home_away_div':home_away_div,
        'strong_weak_script':strong_weak_script, 'strong_weak_div':strong_weak_div,
        'form_script':form_script, 'form_div':form_div
    }

    return render(request, 'pages/fwds.html', context=context)