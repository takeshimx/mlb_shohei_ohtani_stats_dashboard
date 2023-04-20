import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import baseball_metrics as sm
from pybaseball import *
import functions as f


# set a dashboard page configuration
st.set_page_config(page_title = 'Shohei Ohtani Batting Stats Dashboard v1.0',
                   page_icon = ':baseball:', # small icon for the app https://www.webfx.com/tools/emoji-cheat-sheet/
                   layout = 'wide',
                   initial_sidebar_state = 'auto')


@st.cache_data
# create a data frame for individual batter stats
def individual_batter_data(startDate, endDate, lastName, firstName):
    """
    INPUTS:
        startDate: format is 'YYYY-MM-DD'
        endDate: format is 'YYYY-MM-DD'
        lastName: string, lower case
        firstName: string, lower case
    
    OUTPUT:
        batter_player_data: a data frame
    """
    # find MLB player unique ID
    player_mlbid = int(playerid_lookup(lastName.lower(), firstName.lower())['key_mlbam'])
    # create a data frame with the given ID
    batter_player_data = statcast_batter(startDate, endDate, player_mlbid)
    # add a new column
    batter_player_data['launch_speed_angle_definition'] = batter_player_data.apply(f.launch_speed_angle_zone, axis=1)
    
    return batter_player_data

# ohtani_stats_batter_22 = individual_batter_data('2022-04-06', '2022-10-06', 'Ohtani', 'Shohei')
ohtani_stats_batter_1822 = pd.read_csv('ohtani_stats_batter_1822.csv')

# ---- SIDEBAR part.1----
# Filter for key stats
# load all batters stats by season
season_batter_stats_all = pd.read_csv('master_batting_stats_all_1522.csv')
# get only stats for Shohei Ohtani
season_batter_stats_sho = season_batter_stats_all.loc[season_batter_stats_all['Name'] == 'Shohei Ohtani']

st.sidebar.header('Filters:')
st.sidebar.subheader('Key Batting Stats')
# TODO
stats_season = st.sidebar.multiselect(
    'Select Season(s):',
    options = season_batter_stats_sho['Year'].unique(),
    default = 2022
)

df_selection_stats = season_batter_stats_all.query(
    "Name == 'Shohei Ohtani' & Year == @stats_season")


# ---- SIDEBAR part.2----
# Filter 1
st.sidebar.subheader('Stats by Batting Events')
batting_event_season = st.sidebar.multiselect(
    'Select Season(s):',
    options = ohtani_stats_batter_1822['game_year'].unique(),
    default = 2022
)

# Filter 2
batting_events = st.sidebar.multiselect(
    'Select batting events:',
    options = ohtani_stats_batter_1822['events'].unique(),
    default = ohtani_stats_batter_1822['events'].unique()
)

# Filter 3
batted_ball_categories = st.sidebar.multiselect(
    'Select batted ball categories:',
    options = ohtani_stats_batter_1822['launch_speed_angle_definition'].unique(),
    default = ohtani_stats_batter_1822['launch_speed_angle_definition'].unique()
)


df_selection = ohtani_stats_batter_1822.query(
    'events == @batting_events\
        & launch_speed_angle_definition == @batted_ball_categories\
        & game_year == @batting_event_season')


# ---- SIDEBAR part.3----
master_batting_stats_all_1522 = pd.read_csv('master_batting_stats_all_1522.csv')

# Filter 1
st.sidebar.subheader('Offense Analysis')
batting_season = st.sidebar.selectbox(
    'Select Season(s):',
    master_batting_stats_all_1522['Year'].unique(),
    key='batting_season'
)

# Filter 2
league = st.sidebar.multiselect(
    'Select League:',
    options = master_batting_stats_all_1522['League'].unique(),
    default = 'AL'
)

# Filter 3
max_pa = int(master_batting_stats_all_1522['PA'].max())
min_pa = int(master_batting_stats_all_1522['PA'].min())

pa = st.sidebar.slider(
    'Select Plate Appearance range:',
    # options=[min_pa, max_pa]
    value=(300, max_pa),
    step=50
)


df_selection_comparison = master_batting_stats_all_1522.query(
    'Year == @batting_season\
        & League == @league\
            & PA >= @pa[0] & PA <= @pa[1]')

st.markdown('---')


# ---- MAINPAGE ----
st.title(':baseball: Shohei Ohtani Batting Stats in MLB since 2018 Dashboard v1.0')
st.markdown(f'### :blue[{stats_season} Season Stats]')
st.markdown('####')


# # batting KPI's for Shohei Ohtani
# season KPIs
ops_sho = round(df_selection_stats['OPS'].mean(), 3)
ops_plus_sho = int(df_selection_stats['OPS+'].mean())
slg_sho = round(df_selection_stats['SLG'].mean(), 3)
obp_sho = round(df_selection_stats['OBP'].mean(), 3)
ba_sho = round(df_selection_stats['BA'].mean(), 3)
hr_sho = df_selection_stats['HR'].sum()
rbi_sho = df_selection_stats['RBI'].sum()
# barrel_pct_sho = ''
wrc_plus_sho = int(df_selection_stats['wRC+'].mean())
batting_bwar_sho = round(df_selection_stats['bWAR_batter'].sum(), 2)


# Create columns for KPIs
# 1st row
col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9 = st.columns(9)
with col_1:
    st.metric(label=':orange[BA]', value=ba_sho, help='')
with col_2:
    st.metric(label=':orange[OBP]', value=obp_sho, help="")
with col_3:
    st.metric(label=':orange[SLG]', value=slg_sho, help='')
with col_4:
    st.metric(label=':orange[OPS]', value=ops_sho, help='')
with col_5:
    st.metric(label=':orange[OPS+]', value=ops_plus_sho, help='')
with col_6:
    st.metric(label=':orange[wRC+]', value=wrc_plus_sho, help='')
with col_7:
    st.metric(label=':orange[HR]', value=hr_sho)
with col_8:
    st.metric(label=':orange[RBI]', value=rbi_sho, help='')
with col_9:
    st.metric(label=':orange[bWAR]', value=batting_bwar_sho, help='')



st.markdown('---')


# Create charts from here
st.markdown('### :blue[Stats by Batting Events]')

# Chart 1: relationship between launch angle and exit velocity, identifying sweet spot

# filter out null values from events columns
batter_events_sho = df_selection.loc[~df_selection['events'].isnull()]
# filter out rows where launch speed is null
batter_events_sho = batter_events_sho.loc[~batter_events_sho['launch_speed'].isnull()]

fig_1 = px.scatter(batter_events_sho,
                    x='launch_speed',
                    y='launch_angle',
                    color='events', 
                    hover_name='events',
                    size='launch_speed',
                    size_max=10,
                    template='plotly_dark')

fig_1.update_layout(
    title=f'Launch Speed and Angle Analysis in {batting_event_season}<br><sup></sup>',
    legend=dict(
        title='Batting events'
    ),
    xaxis=dict(
        title='Launch Speed (mph)',
        dtick=5
    ),
    yaxis=dict(
        title='Launch Angle (Degree)',
        dtick=5
    ),
    width=800,
    height=700,
)

# Chart 2: wOBA for each batting event

fig_2 = px.scatter(batter_events_sho,
                    x='launch_speed',
                    y='launch_angle',
                    color='events', 
                    hover_name='events',
                    size='woba_value',
                    size_max=10,
                    template='plotly_dark')

fig_2.update_layout(
    title=f'wOBA Analysis by Launch Speed and Angle in {batting_event_season}<br><sup></sup>',
    legend=dict(
        title='Batting events'
    ),
    xaxis=dict(
        title='Launch Speed (mph)',
        dtick=5
    ),
    yaxis=dict(
        title='Launch Angle (Degree)',
        dtick=5
    ),
    width=800,
    height=700,
)

# # Chart 3: barrel analysis
fig_3 = px.scatter(batter_events_sho,
                    x='launch_speed',
                    y='launch_angle',
                    color='launch_speed_angle_definition', 
                    hover_name='events',
                    size='launch_speed',
                    size_max=10,
                    template='plotly_dark')

fig_3.update_layout(
    title=f'Barrel Analysis in {batting_event_season}<br><sup></sup>',
    legend=dict(
        title='Batted ball categories'
    ),
    xaxis=dict(
        title='Launch Speed (mph)',
        dtick=5
    ),
    yaxis=dict(
        title='Launch Angle (Degree)',
        dtick=5
    ),
    width=800,
    height=700,
)


# Chart 4: OPS+ ranking in 2022
# PA >= 400
# batting_stats_all_1522_filtered = df_selection_comparison\
#                             .loc[df_selection_comparison['PA'].astype(int) >= 400]\
#                                 .sort_values('OPS+', ascending=False)

fig_4 = px.bar(df_selection_comparison.sort_values('OPS+', ascending=False)[:20],
                          x='Name',
                          y='OPS+',
                          orientation='v',
                          color='OPS+',
                          hover_name='Name',
                          text_auto='.3s',
                          color_continuous_scale=px.colors.diverging.BrBG,
                          template='ggplot2')

fig_4.update_traces(textfont_size=12,
                               textangle=0,
                               textposition="outside",
                               cliponaxis=False
                              )

fig_4.update_layout(
    title=f'OPS+ {league} Top 20 Players in {batting_season}<br><sup>Average player OPS+ = 100</sup>',
    legend=dict(
        title='OPS+'
    ),
    xaxis=dict(
        title='Player'
    ),
    yaxis=dict(
        title='OPS+',
        dtick=10
    ),
    width=800,
    height=700,
)

# Chart 5: Barrels % rank

fig_5 = px.bar(df_selection_comparison.sort_values('brl_pa_decimal', ascending=False)[:10],
                x='Name',
                y='brl_pa_decimal',
                orientation='v',
                color='brl_pa_decimal',
                hover_name='Name',
                text_auto='.1%',
                template='seaborn')

fig_5.update_traces(textfont_size=12,
                               textangle=0,
                               textposition="outside",
                               cliponaxis=False
                              )

fig_5.update_layout(
    title=f'Barrels % {league} Top 10 Players in {batting_season}<br><sup>Barrel Analysis Against PA</sup>',
    legend=dict(
        title='Barrels'
    ),
    xaxis=dict(
        title='Player'
    ),
    yaxis=dict(
        title='Barrel %',
        dtick='.1%'
    ),
    width=800,
    height=700,
)

# Chart 6: WAR vs. OPS comparison with MLB top players and relationship with wRC+

fig_6 = px.scatter(df_selection_comparison.sort_values('bWAR_batter', ascending=False)[:20],
                          x='bWAR_batter',
                          y='OPS',
                          color='bWAR_batter',
                          hover_name='Name',
                          size='wRC+',
                          size_max=12,
                          text='Name',
                         template='plotly_dark')

fig_6.update_traces(textposition='top center')

fig_6.update_layout(
    title=f'Batting WAR vs. OPS for Top 20 MLB Players in {batting_season}<br><sup></sup>',
    legend=dict(
        title='WAR'
    ),
    xaxis=dict(
        title='WAR'
    ),
    yaxis=dict(
        title='OPS',
        dtick=0.05
    ),
    width=800,
    height=700,
)

# Chart 7: wRC+ ranking
fig_7 = px.bar(df_selection_comparison.sort_values('wRC+', ascending=False)[:20],
                          x='Name',
                          y='wRC+',
                          orientation='v',
                          color='wRC+',
                          hover_name='Name',
                          text_auto='.3s',
                          color_continuous_scale=px.colors.diverging.Tealrose,
                          template='ggplot2')

fig_7.update_traces(textfont_size=12,
                               textangle=0,
                               textposition="outside",
                               cliponaxis=False
                              )

fig_7.update_layout(
    title=f'wRC+ {league} Top 20 Players in {batting_season}<br><sup>Average player OPS+ = 100</sup>',
    legend=dict(
        title='wRC+'
    ),
    xaxis=dict(
        title='Player'
    ),
    yaxis=dict(
        title='wRC+',
        dtick=10
    ),
    width=800,
    height=700,
)

# Create columns for charts
left_column, right_column = st.columns(2)
left_column_r2, right_column_r2 = st.columns([3, 1])

st.markdown('---')
st.markdown('### :blue[Offence Analysis]')

left_column_r3, right_column_r3 = st.columns([2, 2])
left_column_r4, right_column_r4 = st.columns([2, 2])
# left_column_r5, right_column_r5 = st.columns([4, 1])

left_column.plotly_chart(fig_1, use_container_width=True)
right_column.plotly_chart(fig_2, use_container_width=True)
left_column_r2.plotly_chart(fig_3, use_container_width=True)

left_column_r3.plotly_chart(fig_4, use_container_width=True)
right_column_r3.plotly_chart(fig_5, use_container_width=True)
left_column_r4.plotly_chart(fig_7, use_container_width=True)
right_column_r4.plotly_chart(fig_6, use_container_width=True)
# with left_column_r5:
#     st.dataframe(df_selection_comparison)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)













