import pandas as pd
import plotly.express as px
import streamlit as st
from pybaseball import *
import chart_functions as cf
import database as db


# set a dashboard page configuration
st.set_page_config(
    page_title="Shohei Ohtani Batting Stats Dashboard v2.0",
    page_icon=":baseball:",  # small icon for the app https://www.webfx.com/tools/emoji-cheat-sheet/
    layout="wide",
    initial_sidebar_state="auto",
)


@st.cache_data
def load_file(file):
    df = pd.read_csv(file)
    return df


st.markdown("---")

# ---------------------- MAINPAGE ----------------------
st.title(":baseball: Batting Stats in MLB Dashboard")
# ------------ Key Batting Stats ------------
st.markdown("### :blue[Key Batting Stats]")
stats_col1, stats_col2 = st.columns(2)
with stats_col1:
    col1, col2 = st.columns(2)
    with col1:
        # Filter for key stats
        # load all batters stats by season
        # season_batter_stats_all = pd.read_csv(
        #     "./data/batting/master_batting_stats_all_1522.csv"
        # )
        # add database name and collection name from your MongoDB
        season_batter_stats_all = db.create_df_from_mongo(
            db_name="", collection_name=""
        )

        # Filter 1: a batter
        default_idx = list(season_batter_stats_all["Name"].unique()).index(
            "Shohei Ohtani"
        )
        stats_batter = col1.selectbox(
            "Select Batter:",
            options=season_batter_stats_all["Name"].unique(),
            index=default_idx,
        )

        # main data frame is filtered out with batter who is selected above
        season_batter_stats_all_player = season_batter_stats_all.loc[
            season_batter_stats_all["Name"] == stats_batter
        ]

        # Filter 2: season(s)
        game_season_latest = season_batter_stats_all_player["Year"].unique().max()
        stats_season = col2.multiselect(
            "Select Season(s):",
            options=season_batter_stats_all_player["Year"].unique(),
            default=game_season_latest,
        )

        df_selection_stats = season_batter_stats_all.query(
            "Name == @stats_batter \
            & Year == @stats_season"
        )

st.markdown("*Delta shows change from previous season.*")


# # batting KPI's for Shohei Ohtani
# KPIs
ops_sho = round(df_selection_stats["OPS"].mean(), 3)
ops_plus_sho = int(df_selection_stats["OPS+"].mean())
slg_sho = round(df_selection_stats["SLG"].mean(), 3)
obp_sho = round(df_selection_stats["OBP"].mean(), 3)
ba_sho = round(df_selection_stats["BA"].mean(), 3)
hr_sho = df_selection_stats["HR"].sum()
rbi_sho = df_selection_stats["RBI"].sum()
wrc_plus_sho = int(df_selection_stats["wRC+"].mean())
batting_bwar_sho = round(df_selection_stats["bWAR_batter"].sum(), 2)

# delta from previous season
ops_delta_sho = round(df_selection_stats["OPS_diff"].mean(), 3)
opsplus_delta_sho = df_selection_stats["OPS+_diff"].mean()
slg_delta_sho = round(df_selection_stats["SLG_diff"].mean(), 3)
obp_delta_sho = round(df_selection_stats["OBP_diff"].mean(), 3)
ba_delta_sho = round(df_selection_stats["BA_diff"].mean(), 3)
hr_delta_sho = df_selection_stats["HR_diff"].sum()
rbi_delta_sho = df_selection_stats["RBI_diff"].sum()
wrcplus_delta_sho = df_selection_stats["wRC+_diff"].mean()
batting_bwar_delta_sho = round(df_selection_stats["bWAR_batter_diff"].sum(), 3)


# Create columns for KPIs
# 1st row
col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9 = st.columns(9)
with col_1:
    st.metric(
        label=":orange[BA]",
        value=ba_sho,
        delta=ba_delta_sho,
        help="Batting average = number of hits / at-bats",
    )
with col_2:
    st.metric(
        label=":orange[OBP]",
        value=obp_sho,
        delta=obp_delta_sho,
        help="On-base Percentage: how frequently a batter reaches base per plate appearance.\
                Times on base include hits, walks and hit-by-pitches, but do not include errors, times reached on a fielder's choice or a dropped third strike.",
    )
with col_3:
    st.metric(
        label=":orange[SLG]",
        value=slg_sho,
        delta=slg_delta_sho,
        help="Slugging Percentage represents the total number of bases a player records per at-bat. Formula: (1B + 2Bx2 + 3Bx3 + HRx4)/AB",
    )
with col_4:
    st.metric(
        label=":orange[OPS]",
        value=ops_sho,
        delta=ops_delta_sho,
        help="On-base Plus Slugging: OPS adds on-base percentage and slugging percentage to get one number that unites the two.\
                It's meant to combine how well a hitter can reach base, with how well he can hit for average and for power.",
    )
with col_5:
    st.metric(
        label=":orange[OPS+]",
        value=ops_plus_sho,
        delta=opsplus_delta_sho,
        help="OPS+ takes a player's on-base plus slugging percentage and normalizes the number across the entire league.\
                It accounts for external factors like ballparks.\
                    It then adjusts so a score of 100 is league average, and 150 is 50 percent better than the league average.",
    )
with col_6:
    st.metric(
        label=":orange[wRC+]",
        value=wrc_plus_sho,
        delta=wrcplus_delta_sho,
        help="Weighted Runs Created Plus takes the statistic Runs Created and\
                adjusts that number to account for important external factors -- like ballpark or era.\
                    It's adjusted, so a wRC+ of 100 is league average and 150 would be 50 percent above league average.",
    )
with col_7:
    st.metric(label=":orange[HR]", value=hr_sho, delta=hr_delta_sho, help="Home Run")
with col_8:
    st.metric(
        label=":orange[RBI]", value=rbi_sho, delta=rbi_delta_sho, help="Runs Batted In"
    )
with col_9:
    st.metric(
        label=":orange[bWAR Batter]",
        value=batting_bwar_sho,
        delta=batting_bwar_delta_sho,
        help="Batting WAR provided by Baseball Reference",
    )


st.markdown("---")

# -------------------- Stats by Batting Events --------------------
# ---- SIDEBAR ----
st.sidebar.header("Filters:")

# batting data from statcast for Shohei Ohtani since 2018 his debut
# ohtani_stats_batter_1822_file = "./data/batting/ohtani_stats_batter_1822.csv"
# ohtani_stats_batter_1822 = load_file(ohtani_stats_batter_1822_file)

# add database name and collection name from your MongoDB
ohtani_stats_batter_1822 = db.create_df_from_mongo(db_name="", collection_name="")
# batting data from statcast for all MLB eligible players since 2015
# USE csv file due to file size limitation
# all_batters_stats_1522_masterdf_file = (
#     "./data/large_data/batted_resutls_statcast_all_1522_reg.csv"
# )
# all_batters_stats_1522_masterdf = load_file(all_batters_stats_1522_masterdf_file)

# add database name and collection name from your MongoDB
all_batters_stats_1522_masterdf = db.create_df_from_mongo(
    db_name="", collection_name=""
)

# Filter 1: a batter
default_idx = list(all_batters_stats_1522_masterdf["player_name"].unique()).index(
    "Ohtani, Shohei"
)
batter = st.sidebar.selectbox(
    "Select batter:",
    options=all_batters_stats_1522_masterdf["player_name"].unique(),
    index=default_idx,
)

# main data frame is filtered out with pitcher who is selected above
batting_data_all_1522_reg_player = all_batters_stats_1522_masterdf.loc[
    all_batters_stats_1522_masterdf["player_name"] == batter
]

# Filter 2: season
game_season_latest = batting_data_all_1522_reg_player["game_year"].unique().max()

batting_event_season = st.sidebar.multiselect(
    "Select Season(s):",
    options=batting_data_all_1522_reg_player["game_year"].unique(),
    default=game_season_latest,
)

# Filter 3
batting_events = st.sidebar.multiselect(
    "Select batting events:",
    options=batting_data_all_1522_reg_player["events"].unique(),
    default=batting_data_all_1522_reg_player["events"].unique(),
)

# Filter 4
batted_ball_categories = st.sidebar.multiselect(
    "Select batted ball categories:",
    options=batting_data_all_1522_reg_player["launch_speed_angle_definition"].unique(),
    default=batting_data_all_1522_reg_player["launch_speed_angle_definition"].unique(),
)


df_selection = all_batters_stats_1522_masterdf.query(
    "player_name == @batter\
        & events == @batting_events\
            & game_year == @batting_event_season\
                & launch_speed_angle_definition == @batted_ball_categories"
)


# ------- main section -------
st.markdown("### :blue[Stats by Batting Events]")
st.markdown("##### *Analysis from Batting Speed and Angle*")

# Create columns for charts
left_column, right_column = st.columns(2)

# Chart 1: relationship between launch angle and exit velocity, identifying sweet spot
with left_column:
    cf.fig_batting_speed_angle(
        df=df_selection,
        year=batting_event_season,
        sizeMetric="launch_speed",
        colorField="events",
        title=f"{batter} Launch Speed and Angle Analysis",
        legendTitle="Batting events",
    )

# Chart 2: wOBA for each batting event
with right_column:
    cf.fig_batting_speed_angle(
        df=df_selection,
        year=batting_event_season,
        sizeMetric="woba_value",
        colorField="events",
        title=f"{batter} wOBA Launch Speed and Angle Analysis",
        legendTitle="Batting events",
    )

# row 2
left_column_r2, right_column_r2 = st.columns([3, 1])

# Chart 3: barrel analysis
with left_column_r2:
    cf.fig_batting_speed_angle(
        df=df_selection,
        year=batting_event_season,
        sizeMetric="launch_speed",
        colorField="launch_speed_angle_definition",
        title=f"{batter} Barrel Analysis",
        legendTitle="Batted ball categories",
    )

# row 3
extra_col1, extra_col2 = st.columns(2)

# Chart 4: histogram for launch speed
with extra_col1:
    cf.fig_hist_speed_angle(
        df=df_selection,
        year=batting_event_season,
        x="launch_speed",
        xTitle=f"{batter} Launch Speed (mph)",
    )

# Chart 5: histogram for launch angle
with extra_col2:
    cf.fig_hist_speed_angle(
        df=df_selection,
        year=batting_event_season,
        x="launch_angle",
        xTitle=f"{batter} Launch Angle",
    )

st.markdown("---")

# -------------------- Stats by Batting Events part.2 --------------------
st.markdown("### :blue[Stats by Batting Events part.2]")
st.markdown("##### *Batting stats at strike count since 2015*")

mid_col_r2, mid_col2_r2 = st.columns([2, 2])

# plot for BA and HR at each strike count for Shohei Ohtani
with mid_col_r2:
    col1, col2 = st.columns([1, 3])

    # ba_at_strike_count_sho = pd.read_csv("./data/batting/ba_at_strike_count_sho.csv")
    # add database name and collection name from your MongoDB
    ba_at_strike_count_sho = db.create_df_from_mongo(db_name="", collection_name="")

    # Filter 1
    batting_season_sc = col1.selectbox(
        "Select Season:", ba_at_strike_count_sho["year"].unique(), key="batting_year"
    )

    df_selection_sc = ba_at_strike_count_sho.query("year == @batting_season_sc")

    cf.fig_ba_hr(
        df=df_selection_sc,
        playerSelectionVar="Shohei Ohtani",
        yearSelectionVar=batting_season_sc,
    )

# Chart for batting stats at each strike count for all players
with mid_col2_r2:
    col1, col2, col3 = st.columns([1, 2, 1])

    # ba_at_strike_count_all_1522 = pd.read_csv(
    #     "./data/batting/ba_at_strike_count_all_1522.csv"
    # )
    # add database name and collection name from your MongoDB
    ba_at_strike_count_all_1522 = db.create_df_from_mongo(
        db_name="", collection_name=""
    )

    # Filter 1
    batting_season_sc_all = col1.selectbox(
        "Select Season:", ba_at_strike_count_all_1522["year"].unique()
    )

    player_name_sc_all = col2.selectbox(
        "Select Player:", ba_at_strike_count_all_1522["player"].unique()
    )

    df_selection_sc_all = ba_at_strike_count_all_1522.query(
        "year == @batting_season_sc_all\
            & player == @player_name_sc_all"
    )

    cf.fig_ba_hr(
        df=df_selection_sc_all,
        playerSelectionVar=player_name_sc_all,
        yearSelectionVar=batting_season_sc_all,
    )

# ----------------------
st.markdown("##### *Batting stats at RISP since 2015*")

mid_col_r4, mid_col2_r4 = st.columns([2, 2])

# Chart for batting stats at RISP for Shohei Ohtani
with mid_col_r4:
    # stats_at_risp_sho_1822 = pd.read_csv("./data/batting/stats_at_risp_sho_1822.csv")
    # add database name and collection name from your MongoDB
    stats_at_risp_sho_1822 = db.create_df_from_mongo(db_name="", collection_name="")
    career_avg_ba_sho = round(stats_at_risp_sho_1822["BA"].mean(), 3)
    career_avg_slg_sho = round(stats_at_risp_sho_1822["SLG"].mean(), 3)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=":orange[Average BA]", value=career_avg_ba_sho)

    with col2:
        st.metric(label=":orange[Average SLG]", value=career_avg_slg_sho)

    cf.fig_stats_at_risp(df=stats_at_risp_sho_1822, playerSelectionVar="Shohei Ohtani")

with mid_col2_r4:
    col1, col2, col3 = st.columns(3)

    # stats_at_risp_all_1522 = pd.read_csv("./data/batting/stats_at_risp_all_1522.csv")
    # add database name and collection name from your MongoDB
    stats_at_risp_all_1522 = db.create_df_from_mongo(db_name="", collection_name="")

    # Filter 1
    default_idx = list(stats_at_risp_all_1522["player"].unique()).index("Trout, Mike")

    player_name_risp_all = col1.selectbox(
        "Select Player:", stats_at_risp_all_1522["player"].unique(), index=default_idx
    )

    df_selection_sc_all = stats_at_risp_all_1522.query(
        "player == @player_name_risp_all"
    )

    career_avg_ba_all = round(df_selection_sc_all["BA"].mean(), 3)
    career_avg_slg_all = round(df_selection_sc_all["SLG"].mean(), 3)

    with col2:
        st.metric(label=":orange[Average BA]", value=career_avg_ba_all)

    with col3:
        st.metric(label=":orange[Average SLG]", value=career_avg_slg_all)

    cf.fig_stats_at_risp(
        df=df_selection_sc_all, playerSelectionVar=player_name_risp_all
    )


st.markdown("---")

# --------------- Offence Analysis ------------------
st.markdown("### :blue[Offence Analysis]")
st.markdown("##### *Comparison among top players*")

# Row 4 for filters
left_column_r3, right_column_r3 = st.columns([2, 1])
with left_column_r3:
    col1, col2, col3 = st.columns([1, 1, 2])

    # master_batting_stats_all_1522 = pd.read_csv(
    #     "./data/batting/master_batting_stats_all_1522.csv"
    # )
    # add database name and collection name from your MongoDB
    master_batting_stats_all_1522 = db.create_df_from_mongo(
        db_name="", collection_name=""
    )

    # Filter 1
    batting_season = col1.selectbox(
        "Select Season(s):",
        master_batting_stats_all_1522["Year"].unique(),
        key="batting_season",
    )

    # Filter 2
    league = col2.multiselect(
        "Select League:",
        options=master_batting_stats_all_1522["League"].unique(),
        default="AL",
    )

    # Filter 3
    max_pa = int(master_batting_stats_all_1522["PA"].max())
    min_pa = int(master_batting_stats_all_1522["PA"].min())

    pa = col3.slider(
        "Select Plate Appearance range:",
        # options=[min_pa, max_pa]
        value=(300, max_pa),
        step=50,
    )

    df_selection_comparison = master_batting_stats_all_1522.query(
        "Year == @batting_season\
            & League == @league\
                & PA >= @pa[0] & PA <= @pa[1]"
    )

# row 2
left_column_r4, right_column_r4 = st.columns([2, 2])

# Chart 1: OPS+ ranking since 2015
with left_column_r4:
    cf.stat_ranking(
        df=df_selection_comparison,
        x="OPS+",
        y="Name",
        league=league,
        year=batting_season,
        sortValue="OPS+",
        topNumber=20,
        title="OPS+",
        orientation="h",
        color="OPS+",
        textAuto=".3s",
        colorScale=px.colors.diverging.BrBG,
        # colorTemplate='ggplot2'
    )

# Chart 2: Barrels % rank since 2015
with right_column_r4:
    cf.stat_ranking(
        df=df_selection_comparison,
        x="brl_pa_decimal",
        y="Name",
        league=league,
        year=batting_season,
        sortValue="brl_pa_decimal",
        topNumber=10,
        title="Barrel %",
        orientation="h",
        color="brl_pa_decimal",
        textAuto=".1%",
        colorTemplate="seaborn",
    )

left_column_r5, right_column_r5 = st.columns([2, 2])

# Chart 3: wRC+ ranking since 2015
with left_column_r5:
    cf.stat_ranking(
        df=df_selection_comparison,
        x="wRC+",
        y="Name",
        league=league,
        year=batting_season,
        sortValue="wRC+",
        topNumber=20,
        title="wRC+",
        orientation="h",
        color="wRC+",
        textAuto=".3s",
        colorScale=px.colors.sequential.Teal_r,
        # colorTemplate='ggplot2'
    )


# Chart 4: WAR vs. OPS comparison with MLB top players and relationship with wRC+
with right_column_r5:
    cf.fig_war_comparison(
        df=df_selection_comparison,
        x="bWAR_batter",
        y="OPS",
        sortValue="bWAR_batter",
        topNumber=20,
        league=league,
        color="bWAR_batter",
        size="wRC+",
        colorScale=px.colors.diverging.Tropic,
        season=batting_season,
        title="Batter",
    )


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
