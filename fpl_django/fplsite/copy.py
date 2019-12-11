from django.shortcuts import render

import math
from collections import OrderedDict
import pandas as pd
from .modules.gather_data import get_players, get_gws, get_fixtures, team_rating

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend, LegendItem, Panel, Tabs
from bokeh.models.tools import HoverTool
from bokeh.embed import components
from bokeh.layouts import layout

def gkps(request):
    #TODO: create bokeh components for roi,home/away,etc. plots and return them to render

    #ROI---------------------------------------------------------------------------------------------------------------------
    gws = get_gws()
    gws_gkp_roi = gws[['id', 'minutes','GW']]
    current_gw = gws_gkp_roi['GW'].max()
    max_minutes = current_gw * 90.0
    gws_gkp_roi = gws_gkp_roi.groupby(['id']).mean()
    gws_gkp_roi = gws_gkp_roi.loc[gws_gkp_roi['minutes'] > 45.0]
    gws_gkp_roi = gws_gkp_roi.reset_index()
    gws_gkp_roi['id'] = gws_gkp_roi.id.astype(int)
    
    players = get_players()
    players_gkp = players.loc[players['position'] == 'GKP']
    players_gkp_roi = players_gkp[['id', 'web_name', 'minutes','total_points', 'cost', 'team_name', 'selected_by_percent']]
    players_gkp_roi['ppc'] = players_gkp_roi['total_points'] / players_gkp_roi['cost']
    players_gkp_roi['modified_ppc'] = (players_gkp_roi['total_points'] / players_gkp_roi['cost']) * (players_gkp_roi['minutes'] / max_minutes)
    agg_df = players_gkp_roi.groupby(['web_name']).mean()
    agg_df = agg_df.reset_index()
    avg_ppc = agg_df['ppc'].mean()
    avg_mppc = agg_df['modified_ppc'].mean()
    
    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    
    roi_plot = figure(x_axis_label='Name', y_axis_label='ROI', title=' Player ROI: Goalkeepers (Click Legend to filter by team)', 
               plot_width=2050, plot_height=600, x_range=players_gkp_roi["web_name"],tools=TOOLS, toolbar_location="below")
    
    #print(players_gkp_roi.loc[players_gkp_roi['web_name'] == 'Taylor'])
    
    teams = [
        "Arsenal", "Aston Villa", "Bournemouth", "Brighton",
        "Burnley", "Chelsea", "Crystal Palace", "Everton",
        "Leicester", "Liverpool", "Man City", "Man Utd",
        "Newcastle", "Norwich", "Sheffield Utd", "Southampton",
        "Spurs", "Watford", "West Ham", "Wolves"
    ]
    cds_array = []
    circle_array = []
    # Iterate through all the teams
    for i, team_name in enumerate(teams):

        #Subset of players_gkp_roi on team
        team = players_gkp_roi.loc[players_gkp_roi['team_name'] == team_name]
        cds_team = ColumnDataSource(team)
        cds_array.append(cds_team)
        circle_array.append([
            roi_plot.circle("web_name", "ppc", source=cds_team, color='blue', alpha=0.8),
            roi_plot.circle("web_name", "modified_ppc", source=cds_team, color='green', alpha=0.8)
        ])
    avg_ppc_line = roi_plot.line("web_name", avg_ppc, color='blue', alpha=0.4, source=ColumnDataSource(players_gkp_roi))
    avg_ppc_line.visible = False
    avg_mppc_line = roi_plot.line("web_name", avg_mppc, color='green', alpha=0.4, source=ColumnDataSource(players_gkp_roi))
    avg_mppc_line.visible = False
    
    roi_legend1 = Legend(items=[], location=(70,20), orientation="horizontal", click_policy='hide', 
                     glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    roi_legend2 = Legend(items=[], location=(70,10), orientation="horizontal", click_policy='hide', 
                     glyph_height=20, glyph_width=20, label_text_font_size = '7pt')
    
    for team_name, circle in zip(teams[:10], circle_array[:10]):
        legend_item = LegendItem(label=team_name, renderers=[circle[0], circle[1]])
        roi_legend1.items.append(legend_item)
    roi_legend1.items.append(LegendItem(label="Average ROI", renderers=[avg_ppc_line]))
    roi_legend1.items.append(LegendItem(label="Average Modified ROI", renderers=[avg_mppc_line]))
    
    for team_name, circle in zip(teams[10:], circle_array[10:]):
        legend_item = LegendItem(label=team_name, renderers=[circle[0], circle[1]])
        roi_legend2.items.append(legend_item)
    roi_legend2.items.append(LegendItem(label="ROI", renderers=[
        circle_array[0][0], circle_array[1][0], circle_array[2][0], circle_array[3][0], circle_array[4][0],
        circle_array[5][0], circle_array[6][0], circle_array[7][0], circle_array[8][0], circle_array[9][0],
        circle_array[10][0], circle_array[11][0], circle_array[12][0], circle_array[13][0], circle_array[14][0],
        circle_array[15][0], circle_array[16][0], circle_array[17][0], circle_array[18][0], circle_array[19][0]
    ]))
    roi_legend2.items.append(LegendItem(label="Modified ROI", renderers=[
        circle_array[0][1], circle_array[1][1], circle_array[2][1], circle_array[3][1], circle_array[4][1],
        circle_array[5][1], circle_array[6][1], circle_array[7][1], circle_array[8][1], circle_array[9][1],
        circle_array[10][1], circle_array[11][1], circle_array[12][1], circle_array[13][1], circle_array[14][1],
        circle_array[15][1], circle_array[16][1], circle_array[17][1], circle_array[18][1], circle_array[19][1]
    ]))

    roi_plot.add_layout(roi_legend1, 'below')
    roi_plot.add_layout(roi_legend2, 'below')
    
    roi_hover =roi_plot.select(dict(type=HoverTool))
    roi_hover.tooltips = OrderedDict([
            ("Name", "@web_name"),
            ("Team", "@team_name"),
            ("ROI", "@ppc"),
            ("Modified ROI", "@modified_ppc"),
            ("Selected by Percent", "@selected_by_percent")
        ])
    roi_plot.xaxis.major_label_orientation = math.pi/2

    roi_script, roi_div = components(roi_plot)

    #HOME/AWAY---------------------------------------------------------------------------------------------------------------------

    #home--get subsets of GW dataframe and format dataframe accordingly
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'GKP']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_gkp_home = players_gkp[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_gkp_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    avg_pts_home = gws_by_player_home['total_points'].mean()
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'GKP']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_gkp_away = players_gkp[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_gkp_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    avg_pts_away = gws_by_player_away['total_points'].mean()
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 4.5:
            return ["darkgreen", "Less than 4.5"]
        elif c < 5.0:
            return ["lime", "4.5 to 4.9"]
        elif c < 5.5:
            return ["gold", "5.0 to 5.4"]
        elif c < 6.0:
            return ["orange", "5.5 to 5.9"]
        else: return ["red", "6.0 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    max45_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] < 4.5])
    max5_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(4.5, 4.9)])
    max55_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.0, 5.4)])
    max6_home = ColumnDataSource(gws_by_player_home[gws_by_player_home['cost'].between(5.5, 5.9)])
    min6_home = ColumnDataSource(gws_by_player_home.loc[gws_by_player_home['cost'] >= 6.0])

    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    home_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Home Performers: Goalkeepers (Click Legend to filter by price)', 
               plot_width=1350, plot_height=600, x_range=gws_by_player_home["web_name"],tools=TOOLS, toolbar_location="below")
    sect45_home = home_plot.circle("web_name", "avg_points", source=max45_home, color='color', alpha=0.8)
    sect5_home = home_plot.circle("web_name", "avg_points", source=max5_home, color='color', alpha=0.8)
    sect55_home = home_plot.circle("web_name", "avg_points", source=max55_home, color='color', alpha=0.8) 
    sect6_home = home_plot.circle("web_name", "avg_points", source=max6_home, color='color', alpha=0.8)
    sect7_home = home_plot.circle("web_name", "avg_points", source=min6_home, color='color', alpha=0.8)
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
               plot_width=1350, plot_height=600, x_range=gws_by_player_away["web_name"],tools=TOOLS, toolbar_location="below")
    sect45_away = away_plot.circle("web_name", "avg_points", source=max45_away, color='color', alpha=0.8)
    sect5_away = away_plot.circle("web_name", "avg_points", source=max5_away, color='color', alpha=0.8)
    sect55_away = away_plot.circle("web_name", "avg_points", source=max55_away, color='color', alpha=0.8) 
    sect6_away = away_plot.circle("web_name", "avg_points", source=max6_away, color='color', alpha=0.8)
    sect7_away = away_plot.circle("web_name", "avg_points", source=min6_away, color='color', alpha=0.8)
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
    #STRONG-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    fixtures = get_fixtures()
    ratings = team_rating(fixtures)
    ratings = ratings[['GW', 'team', 'team_name','rating_standardized']]
    gws_ratings = gws.loc[gws['GW'] < current_gw]
    gws_ratings = gws_ratings[['id', 'web_name', 'GW', 'position', 'minutes', 'opponent_team', 'total_points', 'was_home']]
    gws_ratings = pd.merge(ratings, gws_ratings, left_on = ['team', 'GW'], right_on=['opponent_team', 'GW'], how = 'right')
    gws_ratings = gws_ratings.rename(columns={"team_name": "opponent_name", "rating_standardized": "opp_rating"})
    gws_ratings = gws_ratings.drop(columns = ['team']) 
    gws_strong_GKP = gws_ratings.loc[gws_ratings['position']== 'GKP']
    gws_strong_GKP = gws_strong_GKP.loc[gws_strong_GKP['opp_rating'] > 0.5]
    gws_strong_GKP = gws_strong_GKP.loc[gws_strong_GKP['minutes'] > 0]

    strong_player_avgs = gws_strong_GKP.groupby("web_name")["id"].count().reset_index(name="games")
    strong_player_avgs = pd.merge(strong_player_avgs, gws_strong_GKP, on = 'web_name', how = 'left')
    strong_player_avgs = strong_player_avgs.groupby('web_name')['total_points', 'minutes', 'games'].mean()
    top20_strong = strong_player_avgs.nlargest(10, 'total_points')
    top20_strong = top20_strong.reset_index()

    strong_cds = ColumnDataSource(top20_strong)
    strong_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Strong Opponents: Goalkeepers', 
                   plot_width=1050, plot_height=600, x_range=top20_strong['web_name'], tools=TOOLS, toolbar_location="below")
    strong_plot.circle("web_name", "total_points", source=strong_cds, color='green', alpha=0.8)
    hover_strong =strong_plot.select(dict(type=HoverTool))
    hover_strong.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Games Played", "@games")
    ])
    strong_plot.xaxis.major_label_orientation = math.pi/4
    #WEAK-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    gws_weak_GKP = gws_ratings.loc[gws_ratings['position']== 'GKP']
    gws_weak_GKP = gws_weak_GKP.loc[gws_weak_GKP['opp_rating'] < -0.5]
    gws_weak_GKP = gws_weak_GKP.loc[gws_weak_GKP['minutes'] > 0]

    weak_player_avgs = gws_weak_GKP.groupby("web_name")["id"].count().reset_index(name="games")
    weak_player_avgs = pd.merge(weak_player_avgs, gws_weak_GKP, on = 'web_name', how = 'left')
    weak_player_avgs = weak_player_avgs.groupby('web_name')['total_points', 'minutes', 'games'].mean()
    top20_weak = weak_player_avgs.nlargest(10, 'total_points')
    top20_weak = top20_weak.reset_index()

    weak_cds = ColumnDataSource(top20_weak)
    weak_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Top Performers against Weak Opponents: Goalkeepers', 
                   plot_width=1050, plot_height=600, x_range=top20_weak['web_name'], tools=TOOLS, toolbar_location="below")
    weak_plot.circle("web_name", "total_points", source=weak_cds, color='green', alpha=0.8)
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
    GKPs = players.loc[players['position'] == 'GKP']
    GKPs = GKPs[['id', 'selected_by_percent']]
    gws_form_GKP = gws.loc[gws['position']== 'GKP']
    gws_form_GKP = gws_form_GKP.loc[gws['GW'].isin([current_gw-2, current_gw-1, current_gw]) ]
    gws_form_GKP = gws_form_GKP[['id', 'web_name', 'GW', 'position', 'minutes', 'opponent_team', 'total_points', 'was_home']]
    gws_form_GKP = pd.merge(GKPs, gws_form_GKP, on='id', how = 'right')
    gws_form_GKP = gws_form_GKP.dropna()
    form_player_avgs = gws_form_GKP.groupby('web_name')['minutes','total_points', 'selected_by_percent'].mean()
    top20_form = form_player_avgs.nlargest(10, 'total_points')
    top20_form = top20_form.reset_index()

    in_form_cds = ColumnDataSource(top20_form)
    in_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' In Form Goalkeepers (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=top20_form['web_name'], tools=TOOLS, toolbar_location="below")

    in_form_plot.circle("web_name", "total_points", source=in_form_cds, color='green', alpha=0.8)
    
    hover_in_form =in_form_plot.select(dict(type=HoverTool))
    hover_in_form.tooltips = OrderedDict([
        ("Name", "@web_name"),
        ("Avg Points", "@total_points"),
        ("Avg Minutes", "@minutes"),
        ("Selected By %", "@selected_by_percent")
    ])
    in_form_plot.xaxis.major_label_orientation = math.pi/4
    #OUT OF FORM-------------------------------------------------------------------
    form_player_avgs = form_player_avgs.loc[form_player_avgs['selected_by_percent'] > 1.5]
    form_player_avgs = form_player_avgs.loc[form_player_avgs['minutes'] > 45]
    bot20_form = form_player_avgs.nsmallest(10, 'total_points')
    bot20_form = bot20_form.reset_index()

    out_form_cds = ColumnDataSource(bot20_form)
    out_form_plot = figure(x_axis_label='Name', y_axis_label='Avg Points', title=' Out of Form Goalkeepers (Last 3 GWs)', 
                   plot_width=1050, plot_height=600, x_range=bot20_form['web_name'], tools=TOOLS, toolbar_location="below")

    out_form_plot.circle("web_name", "total_points", source=out_form_cds, color='green', alpha=0.8)
    
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