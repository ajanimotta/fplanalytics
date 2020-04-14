# FPL Analytics 19-20
Fantasy Premier League Data Analytics Dashboard

Features
- General
  - Web dashboard to aid FPL management using data-driven metrics
  - All plots & tables (plus legends) are user-interactive (hover, zoom, crosshair, pan, reset, save, sort, & filter features)
  
- Teams
  - Weekly team ratings plot (aggregate measure of points haul, goals for, & goals against)
  - Team ratings line plots to asssess how teams have fared throughout the season
  - Average & cumulative team statistics (overall, home, & away tables)
  - Table of upcoming fixtures including fixture difficulty (using binned team ratings)
  
- Players
  - Average & cumulative player statistics with positional data and current FPL price (sortable columns, filterable by team, position, & cost) 
  - By Position
    - Return on Investment Plots: ROI generated for each player using their FPL points haul and players' minutes played
    - Home vs. Away Form: Top home/away performers based on FPL points haul in respective domains (filterable by price)
    - Strength of Opposition: Top performers against strong/weak teams based on FPL points haul & opposition team rating
    - In-Form vs. Out of Form: Best/worst performers over the last 3 gameweeks based on FPL points haul

Technologies
- Web scrapes for data using Selenium & BeaultifulSoup
- Graphs and plots generated using Bokeh
- Web dashboard generated using Django framework
- Modelled data using Python
- Web dashboard deployed through Heroku
