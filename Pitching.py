import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import streamlit as st
import altair as alt
import functions as f
import baseball_metrics as sm
from pybaseball import *


# set a dashboard page configuration
st.set_page_config(page_title = 'Shohei Ohtani Stats Dashboard v1.0',
                   page_icon = ':baseball:', # small icon for the app https://www.webfx.com/tools/emoji-cheat-sheet/
                   layout = 'wide',
                   initial_sidebar_state = 'auto')
        
# load pitching data for all MLB pitchers in 2022
pitching_data_all_22 = pd.read_csv('pitching_data_all_22_df.csv')
# data for Shohei Ohtani 2022
pitching_data_sho_22 = pitching_data_all_22.loc[pitching_data_all_22['player_name'] == 'Ohtani, Shohei']
# data for Shohei Ohtani all seasons
pitching_data_sho_all = pd.read_csv('pitching_data_sho_all.csv')
pitching_data_sho_all = pitching_data_sho_all.loc[~pitching_data_sho_all['pitch_name'].isnull()]

# @st.cache_data

# ---- SIDEBAR part.1----
# Filter for key stats
# load all pitchers stats by season
season_pitcher_stats_all = pd.read_csv('season_pitchers_stats_all_br.csv')
# get only stats for Shohei Ohtani
season_pitcher_stats_sho = season_pitcher_stats_all.loc[season_pitcher_stats_all['Name'] == 'Shohei Ohtani']

st.sidebar.header('Filters:')
st.sidebar.subheader('Key Pitching Stats')
# TODO
stats_season = st.sidebar.multiselect(
    'Select Season(s):',
    options = season_pitcher_stats_sho['Season'].unique(),
    default = 2022
)


df_selection_stats = season_pitcher_stats_all.query(
    "Name == 'Shohei Ohtani' & Season == @stats_season")

# ---- SIDEBAR part.2----
# Filter 1
st.sidebar.subheader('Pitch Movement, Position, & Speed')
pitch_type = st.sidebar.multiselect(
    'Select pitch type:',
    options = pitching_data_sho_all['pitch_name'].unique(),
    default = pitching_data_sho_all['pitch_name'].unique()
)

# Filter 2
season = st.sidebar.multiselect(
    'Select season:',
    options = pitching_data_sho_all['game_year'].unique(),
    default = 2022
)

# Filter 3
# game date list for 2022
game_date_22 = pitching_data_sho_all.loc[pitching_data_sho_all['game_year'] == 2022]['game_date'].unique()
game_date = st.sidebar.multiselect(
    'Select Game Date:',
    options = pitching_data_sho_all['game_date'].unique(),
    default = game_date_22
)

df_selection = pitching_data_sho_all.query(
    'pitch_name == @pitch_type\
        & game_year == @season\
            & game_date == @game_date')
        # & player_name == @pitcher'


# ---- SIDEBAR part.3----
# create another df_selection for querying from another df
st.sidebar.subheader('Pitch Usage')

# data only for Shohei Ohtani
shohei_ohtani_mlbid = int(playerid_lookup('ohtani', 'shohei')['key_mlbam'])
current_year = datetime.today().year
five_years_ago = datetime.today().year - 5
individual_stats_all_sho = f.individual_pitcher_stats_v2(pitching_data_sho_all, shohei_ohtani_mlbid, five_years_ago, current_year)
individual_stats_all_sho['Year'] = individual_stats_all_sho['Year'].astype(int)
# data for all pitchers from 2015 to 2022
pitchers_stats_1522_all = pd.read_csv('pitch_stats_all_players_1522_df.csv')

st.sidebar.subheader('Shohei Ohtani')
# Filter 1
year = st.sidebar.selectbox(
    'Select Year:',
    individual_stats_all_sho['Year'].unique(),
    key='year'
)

df_selection_2 = individual_stats_all_sho.query(
    'Year == @year')

# -----------

st.sidebar.subheader('MLB Pitcher to Compare')
# Filter 2.1: Year
year_comparison = st.sidebar.selectbox(
    'Select Year:',
    pitchers_stats_1522_all['Year'].unique(),
    key='year_2'
)

# Filter 2.2: Pitcher name
pitcher_comparison = st.sidebar.selectbox(
    'Select Pitcher:',
    pitchers_stats_1522_all['Name'].unique(),
    key='pitcher_2'
)

df_selection_2b = pitchers_stats_1522_all.query(
    'Year == @year_comparison\
        & Name == @pitcher_comparison')

# ---- SIDEBAR part.4----
# Filter 1
st.sidebar.subheader('Pitching Defense Analysis')
pitching_season = st.sidebar.selectbox(
    'Select Season(s):',
    season_pitcher_stats_all['Season'].unique(),
    key='pitching_season'
)

# Filter 2
# league = st.sidebar.multiselect(
#     'Select League:',
#     options = master_batting_stats_all_1522['League'].unique(),
#     default = 'AL'
# )

# Filter 3
max_ip = int(season_pitcher_stats_all['IP'].max())
min_ip = int(season_pitcher_stats_all['IP'].min())

ip = st.sidebar.slider(
    'Select Innings Pitched range:',
    # options=[min_pa, max_pa]
    value=(130, max_ip),
    step=10
)

df_selection_comparison = season_pitcher_stats_all.query(
    'Season == @pitching_season\
            & IP >= @ip[0] & IP <= @ip[1]')

# ---- MAINPAGE ----
st.title(':baseball: Shohei Ohtani Pitching Stats in MLB since 2018 Dashboard v1.0')
st.markdown(f'### :blue[{stats_season} Key Pitching Stats]')
st.markdown('####')

# pitching stats for Shohei Ohtani by season
era_sho = df_selection_stats['ERA'].mean()
eraplus_sho = df_selection_stats['ERA+'].mean()
win_sho = df_selection_stats['W'].sum()
fip_sho = df_selection_stats['FIP'].mean()
ip_sho = df_selection_stats['IP'].sum()
k9_sho = df_selection_stats['K/9'].mean()
pitch_bwar_sho = df_selection_stats['bWAR_pitcher'].sum()
whip_sho = df_selection_stats['WHIP'].mean()
so_sho_b = df_selection_stats['SO'].sum()

# variable KPIs
so_sho = len(df_selection.loc[df_selection['events'] == 'strikeout'])
whiff_pct_sho = sm.whiff(df_selection, df_selection['pitch_name'])
# chase_rate_sho = sm.chase_rate(df_selection, df_selection['pitch_name'])


# Create columns for KPIs
# 1st row
left_column_1, left_column_2, middle_column_1, middle_column_2, right_column_1, right_column_2, extra_column_1, extra_column_2, extra_column_3 = st.columns(9)
with left_column_1:
    st.metric(label=':orange[ERA]', value=era_sho, help='Earned run average represents the number of earned runs a pitcher allows per nine innings -- with earned runs being any runs that scored without the aid of an error or a passed ball.')
with left_column_2:
    st.metric(label=':orange[ERA+]', value=int(eraplus_sho), help="ERA+ takes a player's ERA and normalizes it across the entire league. It accounts for external factors like ballparks and opponents. It then adjusts, so a score of 100 is league average, and 150 is 50 percent better than the league average.")
with middle_column_1:
    st.metric(label=':orange[WIN]', value=win_sho, help='Number of wins')
with middle_column_2:
    st.metric(label=':orange[FIP]', value=round(fip_sho, 2), help='FIP is similar to ERA, but it focuses solely on the events a pitcher has the most control over -- strikeouts, unintentional walks, hit-by-pitches and home runs.')
with right_column_1:
    st.metric(label=':orange[K/9]', value=round(k9_sho, 2), help='K/9 rate measures how many strikeouts a pitcher averages for every nine innings pitched. It is determined by dividing his strikeout total by his innings pitched total and multiplying the result by nine.') # tentative number
with right_column_2:
    st.metric(label=':orange[bWAR]', value=pitch_bwar_sho, help="WAR measures a player's value in all facets of the game by deciphering how many more wins he's worth than a replacement-level player at his same position (e.g., a Minor League replacement or a readily available fill-in free agent).") # tentative number
with extra_column_1:
    st.metric(label=':orange[WHIP]', value=round(whip_sho, 2), help='Walks And Hits Per Inning Pitched')
with extra_column_2:
    st.metric(label=':orange[IP]', value=ip_sho, help='Inning pitched')
with extra_column_3:
    st.metric(label=':orange[SO]', value=so_sho_b, help='Number of Strike Out')
    

st.markdown('---')
st.markdown('### :blue[Pitch Movement, Position, & Speed]')


# Create charts from here
# Chart 1: pitch type ditribution and speed by game

# fig_3 = px.scatter(df_selection,
#                     x='game_date',
#                     y='release_speed',
#                     color='pitch_name',
#                     hover_name='pitch_name'
#                     )

# fig_3.update_layout(
#         title='Shohei Ohtani Pitch Speed by Game<br><sup></sup>',
#         showlegend=True,
#         xaxis=dict(
#             title='Game date',
#             gridcolor='white',
#             gridwidth=2,
#             dtick='M1',
#             tickformat='%b'
#         ),
#         yaxis=dict(
#             title='Release Spped (mph)',
#             dtick=5,
#             gridcolor='white',
#             gridwidth=2,
#         )
#     )

# plot with altair
# define scale for pitch name and colors to each pitch type
scale = alt.Scale(
    domain=list(pitching_data_sho_all['pitch_name'].unique()),
    range=["#e7ba52", "#274472", "#eabeb4", "#1f77b4", "#9467bd", "#4d8731", "#bf5958", "#7c501a"],
)
color = alt.Color('pitch_name:N', scale=scale, title='Pitch type')

# We create two selections:
# - a brush that is active on the top panel
# - a multi-click that is active on the bottom panel
brush = alt.selection_interval(encodings=["x"])
click = alt.selection_multi(encodings=["color"])

# Top panel is scatter plot of pitching release speed vs. game date
points = (
    alt.Chart()
    .mark_point()
    .encode(
        x=alt.X('game_date:T',
                title=f'Game Date in {season}'),
        y=alt.Y('release_speed:Q',
                title='Release Speed (mph)',
                scale=alt.Scale(domain=[55, 105])),
        # color=alt.Color('pitch_name:N', title='Pitch type'),
        color=alt.condition(brush, color, alt.value("lightgray")),
    )
    .properties(width=650, height=350)
    .add_selection(brush)
    .transform_filter(click)
)

# Bottom panel is a bar chart of pitch type
bars = (
    alt.Chart()
    .mark_bar()
    .encode(
        x=alt.X("count():Q", title='Pitch Counts'),
        y=alt.Y('pitch_name:N', title=''),
        # color='pitch_name:N',
        color=alt.condition(click, color, alt.value("lightgray")),
    )
    .transform_filter(brush)
    .properties(
        width=650,
    )
    .add_selection(click)
)

fig_3 = alt.vconcat(points,
                    bars,
                    data=df_selection,
                    title=f'Shohei Ohtani Pitch Speed by Game in {season}')


# Chart 2: pitch movements distribution for Ohtani san
# change volumes for breaking balls such as horizontal break, downward vertical break
# ref: https://baseballsavant.mlb.com/pitchmix#656605_2023
pitch_dstribution_sho = df_selection[['game_date', 'release_speed', 'release_pos_x', 'release_pos_z',
                                      'pfx_x', 'pfx_z', 'plate_x', 'plate_z', 'pitch_name', 'description', 'events', 'type', 'zone']]

fig_1 = px.scatter(pitch_dstribution_sho,
                    x='pfx_x',
                    y='pfx_z',
                    color='pitch_name',
                    hover_name='pitch_name')

# fig_pitch_distribution_sho.add_selection(x0=-1.41667, y0=1.5748, x1=1.41667, y1=3.41207)

# add annotation that shows each pitch type summary

fig_1.update_layout(
    title='Shohei Ohtani Pitch Movement',
    legend=dict(
        title='Pitch Name'
    ),
    xaxis=dict(
        title='Horizontal movement (ft)',
        dtick=0.5
    ),
    yaxis=dict(
        title='Vertical movement (ft)',
        dtick=0.5
    ),
    width=800,
    height=600,
)

# # Chart 3: pitch distribution for Ohtani san
fig_2 = px.scatter(pitch_dstribution_sho,
                    x='plate_x',
                    y='plate_z',
                    color='pitch_name',
                    hover_name='pitch_name')

# fig_pitch_distribution_sho.add_selection(x0=-1.41667, y0=1.5748, x1=1.41667, y1=3.41207)

fig_2.update_layout(
    title='Shohei Ohtani Pitch Distribution',
    legend=dict(
        title='Pitch Name'
    ),
    xaxis=dict(
        title='Horizontal position (ft)',
        dtick=1
    ),
    yaxis=dict(
        title='Vertical position (ft)',
        dtick=1
    ),
    width=800,
    height=600,
)

# Chart 4: pitch usage
# create a data frame of individual stats for Shohei Ohtani
# shohei_ohtani_mlbid = int(playerid_lookup('ohtani', 'shohei')['key_mlbam'])
# individual_stats_all_sho = individual_pitcher_stats_v2(df_selection, shohei_ohtani_mlbid, 2018, 2022)
# current_year = datetime.today().year
# five_years_ago = datetime.today().year - 5
# individual_stats_all_sho = f.individual_pitcher_stats_v2(df_selection, shohei_ohtani_mlbid, five_years_ago, current_year)
# pitch_type_ratio_sho = round(df_selection['pitch_name'].value_counts() /\
#                                 df_selection['pitch_name'].value_counts().sum(), 3)

# plot
# TODO: Create color scale dictionary by pitch type
# pitch_type_color_dict = {
#     '4-Seam Fastball': '#e5866',
#     'Sweeper': '#52bca3',
#     'Curveball': '#daa51b',
#     'Sinker': '#24796c',
#     'Slider': '#99c945',
#     'Split-Finger': '#cc61b0',
#     'Cutter': '#5d69b1',
#     'Slow Curve': '#764e9f',
#     'Knuckle Curve': '',
#     'Changeup': '#2f8ac4',
#     'Slurve': '#ed645a',
#     'Knuckleball': '#a5aa99',
#     'Screwball': '',
#     'Eephus': '',
#     'Other': '',
# }

fig_4 = px.bar(df_selection_2,
                x=df_selection_2['Pitch type'],
                y=df_selection_2['Pitch %'],
                orientation='v',
                # color_discrete_map=pitch_type_color_dict,
                color='Pitch type',
                text_auto='.1%',
                template='seaborn')

fig_4.update_layout(
        title=f'Shohei Ohtani Pitch Usage in {year}<br><sup></sup>',
        xaxis=dict(
            title='Pitch type',
            gridcolor='white',
            gridwidth=2,
            showgrid=False
        ),
        yaxis=dict(
            title='Pitch Usage',
            gridcolor='white',
            gridwidth=2,
            tickformat='.1%'
        )
    )

# Chart 5: Pitch usage for comparison by choosing other MLB pitchers including Shohei Ohtani
# create a dat frame of individual stats for all MLB pitchers
fig_5 = px.bar(df_selection_2b,
                x=df_selection_2b['Pitch type'],
                y=df_selection_2b['Pitch %'],
                orientation='v',
                color='Pitch type',
                text_auto='.1%',
                template='seaborn')

fig_5.update_layout(
        title=f'{pitcher_comparison} Pitch Usage in {year_comparison}<br><sup></sup>',
        xaxis=dict(
            title='Pitch type',
            gridcolor='white',
            gridwidth=2,
            showgrid=False
        ),
        yaxis=dict(
            title='Pitch Usage',
            gridcolor='white',
            gridwidth=2,
            tickformat='.1%'
        )
    )

# Chart 6: ERA+ ranking
fig_6 = px.bar(df_selection_comparison.sort_values('ERA+', ascending=False)[:20],
                          x='Name',
                          y='ERA+',
                          orientation='v',
                          color='ERA+',
                          text_auto='.3s',
                          color_continuous_scale=px.colors.diverging.BrBG,
                          template='ggplot2')

fig_6.update_traces(textfont_size=12,
                               textangle=0,
                               textposition="outside",
                               cliponaxis=False
                              )

fig_6.update_layout(
    title=f'ERA+ Top 20 Players in {pitching_season}<br><sup>Average player ERA+ = 100</sup>',
    legend=dict(
        title='ERA+'
    ),
    xaxis=dict(
        title='Player'
    ),
    yaxis=dict(
        title='ERA+',
        dtick=10
    ),
    width=800,
    height=700,
)

# Chart 7: ERA+ vs. WAR
fig_7 = px.scatter(df_selection_comparison.sort_values('bWAR_pitcher', ascending=False)[:20],
                          x='bWAR_pitcher',
                          y='ERA',
                          color='bWAR_pitcher',
                          hover_name='Name',
                          size='bWAR_pitcher',
                          size_max=12,
                          text='Name',
                          color_continuous_scale=px.colors.diverging.Tealrose,
                         template='plotly_dark')

fig_7.update_traces(textposition='top center')

fig_7.update_layout(
    title=f'Pitching WAR vs. ERA for Top 20 MLB Players in {pitching_season}<br><sup></sup>',
    legend=dict(
        title='WAR'
    ),
    xaxis=dict(
        title='WAR'
    ),
    yaxis=dict(
        title='ERA',
        dtick=0.05
    ),
    width=800,
    height=700,
)

# row for granular level stats
stats_left_col, stats_middle_col, stats_right_col = st.columns(3)
with stats_left_col:
    st.metric(label=':orange[Total Strikeouts]', value=so_sho)
with stats_middle_col:
    st.metric(label=':orange[WHIFF%]', value=whiff_pct_sho*100, help="Whiff% is the percentage of whiffs across all swings from the batter.")
# with stats_right_col:
#     st.metric(label=':orange[Chase Rate]', value=chase_rate_sho)

# Create columns for charts
# Row 1
left_column, right_column = st.columns(2)
# Row 2. Spaces are devided by ratio 3:1.
left_column_r2, right_column_r2 = st.columns([3, 1])

st.markdown('---')
st.markdown('### :blue[Pitch Usage]')

# Row 3
left_column_r3, right_column_r3 = st.columns(2)
left_column.plotly_chart(fig_1, use_container_width=True)
right_column.plotly_chart(fig_2, use_container_width=True)
# left_column_r2.plotly_chart(fig_3, use_container_width=True)
left_column_r2.altair_chart(fig_3, use_container_width=True)
left_column_r3.plotly_chart(fig_4, use_container_width=True)
with right_column_r3:
    st.plotly_chart(fig_5, use_container_width=True)
    st.write('*Caveats: Data contains only pitchers whose IPs >= 100 and ERA < 4.00 in a given season.*')

st.markdown('---')
st.markdown('### :blue[Pitching Defense Analysis]')

# Row 4
left_column_r4, right_column_r4 = st.columns(2)
# left_column_r4.plotly_chart(fig_6, use_container_width=True)
with left_column_r4:
    tab1, tab2 = st.tabs(['Chart', 'Dataframe'])
    with tab1:
        st.plotly_chart(fig_6, use_container_width=True)
    with tab2:
        st.dataframe(df_selection_comparison)
right_column_r4.plotly_chart(fig_7, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)













