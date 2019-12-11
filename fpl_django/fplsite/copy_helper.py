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