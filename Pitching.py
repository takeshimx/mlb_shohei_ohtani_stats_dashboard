import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import altair as alt
import functions as f
import baseball_metrics as sm
import chart_functions as cf
from pybaseball import *
import streamlit_authenticator as stauth
import database as db

# set a dashboard page configuration
st.set_page_config(
    page_title="Shohei Ohtani Stats Dashboard v2.0",
    page_icon=":baseball:",  # small icon for the app https://www.webfx.com/tools/emoji-cheat-sheet/
    layout="wide",
    initial_sidebar_state="auto",
)


@st.cache_data(ttl=1800)
def load_file(file):
    df = pd.read_csv(file)
    return df


# add authenticator to the webapage (ref: https://www.youtube.com/watch?v=eCbH2nPL9sU)
# --------------------- USER AUTHENTICATION ---------------------
# fetch all users from MongoDB database, and create lists of those fields
users = db.fetch_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

# create a dictionary for credential info
credentials = {"usernames": {}}

for un, name, pw in zip(usernames, names, hashed_passwords):
    user_dict = {"name": name, "password": pw}
    credentials["usernames"].update({un: user_dict})

# create authenticator object, provide cookie name, random key
authenticator = stauth.Authenticate(
    credentials,
    cookie_name="baseball_dashboard",
    key="jiksjdnb",
    cookie_expiry_days=30,
)

name, authentication_status, username = authenticator.login(
    form_name="Login", location="main"
)

if authentication_status == False:
    st.error("Username/password is incrrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

# if authentication is right, run below
if authentication_status:
    # data for Shohei Ohtani all seasons
    # pitching_data_sho_all_file = "./data/pitching/pitching_data_sho_all.csv"
    # pitching_data_sho_all = load_file(pitching_data_sho_all_file)

    # add database name and collection name from your MongoDB
    pitching_data_sho_all = db.create_df_from_mongo(db_name="", collection_name="")
    pitching_data_sho_all = pitching_data_sho_all.loc[
        ~pitching_data_sho_all["pitch_name"].isnull()
    ]
    # data for all eligible pitchers for regular season from 2015 to 2022
    # USE csv file due to file size limitation
    # pitching_data_all_1522_reg_file = (
    #     "./data/large_data/pitching_data_all_1522_df_reg.csv"
    # )
    # pitching_data_all_1522_reg = load_file(pitching_data_all_1522_reg_file)

    # add database name and collection name from your MongoDB
    pitching_data_all_1522_reg = db.create_df_from_mongo(db_name="", collection_name="")
    pitching_data_all_1522_reg["game_year"] = pitching_data_all_1522_reg[
        "game_year"
    ].astype(int)

    # --------------------- SIDEBAR for Pitch movement, position, & speed ---------------------
    # set up logout button
    authenticator.logout(button_name="Logout", location="sidebar")
    # display a username
    st.sidebar.title(f"Welcome {name}")

    st.sidebar.header("Filters:")
    st.sidebar.subheader("Pitch Movement, Position, & Speed")

    # Filter 1 for selecting pitcher
    default_idx = list(pitching_data_all_1522_reg["player_name"].unique()).index(
        "Ohtani, Shohei"
    )
    pitcher = st.sidebar.selectbox(
        "Select pithcer:",
        options=pitching_data_all_1522_reg["player_name"].unique(),
        index=default_idx,
    )

    # main data frame is filtered out with pitcher who is selected above
    pitching_data_all_1522_reg_player = pitching_data_all_1522_reg.loc[
        pitching_data_all_1522_reg["player_name"] == pitcher
    ]

    # Filter 2 for pithc type
    pitch_type = st.sidebar.multiselect(
        "Select pitch type:",
        options=pitching_data_all_1522_reg_player["pitch_name"].unique(),
        default=pitching_data_all_1522_reg_player["pitch_name"].unique(),
    )

    # first, select 'season level' or 'date level' stats
    level = st.sidebar.selectbox(
        "Select level:", options=["Season level", "Date level"]
    )

    if level == "Season level":
        season = st.sidebar.multiselect(
            "Select season:",
            options=pitching_data_all_1522_reg_player["game_year"].unique(),
            default=2022,
        )
        df_selection = pitching_data_all_1522_reg.query(
            "pitch_name == @pitch_type\
            & game_year == @season\
                & player_name == @pitcher"
        )

    if level == "Date level":
        game_date_latest = pitching_data_all_1522_reg_player.loc[
            pitching_data_all_1522_reg_player["game_year"]
            == pitching_data_all_1522_reg_player["game_year"].max()
        ]["game_date"].unique()

        game_date = st.sidebar.multiselect(
            "Select Game Date:",
            options=pitching_data_all_1522_reg_player["game_date"].unique(),
            default=game_date_latest,
        )
        df_selection = pitching_data_all_1522_reg.query(
            "pitch_name == @pitch_type\
                & game_date == @game_date\
                    & player_name == @pitcher"
        )

    # --------------------- MAINPAGE ---------------------
    st.title(":baseball: Pitching Stats in MLB Dashboard")

    # ----------- Key Pitching Stats -----------
    st.markdown("### :blue[Key Pitching Stats]")
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        col1, col2 = st.columns(2)
        with col1:
            # Filter for key stats
            # load all pitchers stats by season
            # season_pitcher_stats_all = pd.read_csv(
            #     "./data/pitching/season_pitchers_stats_all_br.csv"
            # )

            # add database name and collection name from your MongoDB
            season_pitcher_stats_all = db.create_df_from_mongo(
                db_name="", collection_name=""
            )

            # Filter 1: a pitcher
            default_idx = list(season_pitcher_stats_all["Name"].unique()).index(
                "Shohei Ohtani"
            )
            stats_pitcher = col1.selectbox(
                "Select Pitcher:",
                options=season_pitcher_stats_all["Name"].unique(),
                index=default_idx,
            )

            # main data frame is filtered out with pitcher who is selected above
            season_pitcher_stats_all_player = season_pitcher_stats_all.loc[
                season_pitcher_stats_all["Name"] == stats_pitcher
            ]

            # Filter 2: season(s)
            game_season_latest = (
                season_pitcher_stats_all_player["Season"].unique().max()
            )
            stats_season = col2.multiselect(
                "Select Season(s):",
                options=season_pitcher_stats_all_player["Season"].unique(),
                default=game_season_latest,
            )

            df_selection_stats = season_pitcher_stats_all.query(
                "Name == @stats_pitcher \
                & Season == @stats_season"
            )

    st.markdown("*Delta shows change from previous season.*")

    # pitching stats for Shohei Ohtani by season
    era_sho = df_selection_stats["ERA"].mean()
    eraplus_sho = df_selection_stats["ERA+"].mean()
    win_sho = df_selection_stats["W"].sum()
    fip_sho = df_selection_stats["FIP"].mean()
    ip_sho = df_selection_stats["IP"].sum()
    k9_sho = df_selection_stats["K/9"].mean()
    pitch_bwar_sho = df_selection_stats["bWAR_pitcher"].sum()
    whip_sho = df_selection_stats["WHIP"].mean()
    so_sho_b = df_selection_stats["SO"].sum()

    # delta from previous season
    era_delta_sho = df_selection_stats["ERA_diff"].mean()
    eraplus_delta_sho = df_selection_stats["ERA+_diff"].mean()
    win_delta_sho = df_selection_stats["W_diff"].sum()
    fip_delta_sho = df_selection_stats["FIP_diff"].mean()
    ip_delta_sho = df_selection_stats["IP_diff"].sum()
    k9_delta_sho = df_selection_stats["K/9_diff"].mean()
    pitch_bwar_delta_sho = df_selection_stats["bWAR_pitcher_diff"].sum()
    whip_delta_sho = df_selection_stats["WHIP_diff"].mean()
    so_delta_sho = df_selection_stats["SO_diff"].sum()

    # Create columns for KPIs
    # 1st row
    (
        left_column_1,
        left_column_2,
        middle_column_1,
        middle_column_2,
        right_column_1,
        right_column_2,
        extra_column_1,
        extra_column_2,
        extra_column_3,
    ) = st.columns(9)
    with left_column_1:
        st.metric(
            label=":orange[ERA]",
            value=round(era_sho, 2),
            delta=round(era_delta_sho, 2),
            help="Earned run average represents the number of earned runs a pitcher allows per nine innings\
                    -- with earned runs being any runs that scored without the aid of an error or a passed ball.",
        )
    with left_column_2:
        st.metric(
            label=":orange[ERA+]",
            value=int(eraplus_sho),
            delta=int(eraplus_delta_sho),
            help="ERA+ takes a player's ERA and normalizes it across the entire league.\
                    It accounts for external factors like ballparks and opponents. It then adjusts, so a score of 100 is league average,\
                        and 150 is 50 percent better than the league average.",
        )
    with middle_column_1:
        st.metric(
            label=":orange[WIN]",
            value=win_sho,
            delta=int(win_delta_sho),
            help="Number of wins",
        )
    with middle_column_2:
        st.metric(
            label=":orange[FIP]",
            value=round(fip_sho, 2),
            delta=round(fip_delta_sho, 2),
            help="FIP is similar to ERA, but it focuses solely on the events a pitcher has the most control over\
                    -- strikeouts, unintentional walks, hit-by-pitches and home runs.",
        )
    with right_column_1:
        st.metric(
            label=":orange[K/9]",
            value=round(k9_sho, 2),
            delta=round(k9_delta_sho, 2),
            help="K/9 rate measures how many strikeouts a pitcher averages for every nine innings pitched.\
                    It is determined by dividing his strikeout total by his innings pitched total and multiplying the result by nine.",
        )
    with right_column_2:
        st.metric(
            label=":orange[bWAR Pitcher]",
            value=pitch_bwar_sho,
            delta=round(pitch_bwar_delta_sho, 2),
            help="WAR measures a player's value in all facets of the game by deciphering how many more wins he's worth than a replacement-level player\
                    at his same position (e.g., a Minor League replacement or a readily available fill-in free agent).",
        )
    with extra_column_1:
        st.metric(
            label=":orange[WHIP]",
            value=round(whip_sho, 2),
            delta=round(whip_delta_sho, 2),
            help="Walks And Hits Per Inning Pitched",
        )
    with extra_column_2:
        st.metric(
            label=":orange[IP]",
            value=ip_sho,
            delta=round(ip_delta_sho, 1),
            help="Inning pitched",
        )
    with extra_column_3:
        st.metric(
            label=":orange[SO]",
            value=so_sho_b,
            delta=int(so_delta_sho),
            help="Number of Strike Out",
        )

    st.markdown("---")

    # ----------- Pitch Movement, Position, & Speed -----------
    st.markdown("### :blue[Pitch Movement, Position, & Speed]")
    # variable KPIs
    so_sho = len(df_selection.loc[df_selection["events"] == "strikeout"])
    whiff_pct_sho = sm.whiff(df_selection, df_selection["pitch_name"])
    # chase_rate_sho = sm.chase_rate(df_selection, df_selection['pitch_name'])[0]

    # row for granular level stats
    stats_left_col, stats_middle_col, stats_right_col = st.columns(3)
    with stats_left_col:
        st.metric(label=":orange[Total Strikeouts]", value=so_sho)
    with stats_middle_col:
        st.metric(
            label=":orange[WHIFF%]",
            value=round(whiff_pct_sho * 100, 2),
            help="Whiff% is the percentage of whiffs across all swings from the batter.",
        )
    # with stats_right_col:
    #     st.metric(label=':orange[Chase Rate]', value=chase_rate_sho)

    # ------- Charts -------
    pitch_dstribution_sho = df_selection[
        [
            "game_date",
            "release_speed",
            "release_pos_x",
            "release_pos_z",
            "pfx_x",
            "pfx_z",
            "plate_x",
            "plate_z",
            "pitch_name",
            "description",
            "events",
            "type",
            "zone",
        ]
    ]

    # Row 1
    left_column, right_column = st.columns(2)

    # Chart 1: pitch movements distribution
    # change volumes for breaking balls such as horizontal break, downward vertical break
    # ref: https://baseballsavant.mlb.com/pitchmix#656605_2023
    with left_column:
        cf.fig_pitch_stats(
            pitch_dstribution_sho, "pfx_x", "pfx_z", pitcher, season, "Pitch Movement"
        )

    # Chart 2: pitch position distribution
    with right_column:
        cf.fig_pitch_stats(
            pitch_dstribution_sho,
            "plate_x",
            "plate_z",
            pitcher,
            season,
            "Pitch Position",
        )

    # Row 2. Spaces are devided by ratio 3:1.
    # Chart 3: pitch type ditribution and speed by game
    left_column_r2, right_column_r2 = st.columns([3, 1])
    with left_column_r2:
        # plot with altair
        # define scale for pitch name and colors to each pitch type
        scale = alt.Scale(
            domain=list(pitching_data_all_1522_reg_player["pitch_name"].unique()),
            range=[
                "#e7ba52",
                "#274472",
                "#eabeb4",
                "#1f77b4",
                "#9467bd",
                "#4d8731",
                "#bf5958",
                "#7c501a",
            ],
        )
        color = alt.Color("pitch_name:N", scale=scale, title="Pitch type")

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
                x=alt.X("game_date:T", title=f"Game Date"),
                y=alt.Y(
                    "release_speed:Q",
                    title="Release Speed (mph)",
                    scale=alt.Scale(domain=[55, 105]),
                ),
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
                x=alt.X("count():Q", title="Pitch Counts"),
                y=alt.Y("pitch_name:N", title=""),
                # color='pitch_name:N',
                color=alt.condition(click, color, alt.value("lightgray")),
            )
            .transform_filter(brush)
            .properties(
                width=650,
            )
            .add_selection(click)
        )

        fig_3 = alt.vconcat(
            points,
            bars,
            data=df_selection,
            title=f"{pitcher} Pitch Speed by Game in {season}",
        )

        st.altair_chart(fig_3, use_container_width=True)

    st.markdown("---")

    # ----------- Pitch Usage -----------
    st.markdown("### :blue[Pitch Usage]")

    # Row 3
    left_column_r3, right_column_r3 = st.columns(2)

    # Chart 4: pitch usage
    with left_column_r3:
        # data only for Shohei Ohtani
        shohei_ohtani_mlbid = int(playerid_lookup("ohtani", "shohei")["key_mlbam"])
        current_year = datetime.today().year
        five_years_ago = datetime.today().year - 5
        individual_stats_all_sho = f.individual_pitcher_stats_v2(
            pitching_data_sho_all, shohei_ohtani_mlbid, five_years_ago, current_year
        )
        individual_stats_all_sho["Year"] = individual_stats_all_sho["Year"].astype(int)

        col1, col2, col3 = st.columns(3)
        # Filter 1
        default_idx = list(individual_stats_all_sho["Year"].unique()).index(2022)
        year = col1.selectbox(
            "Select Year:", individual_stats_all_sho["Year"].unique(), index=default_idx
        )

        df_selection = individual_stats_all_sho.query("Year == @year")

        # chart
        cf.pitch_usage(df_selection, year, "Shohei Ohtani")

    # Chart 5: Pitch usage for comparison by choosing other MLB pitchers including Shohei Ohtani
    with right_column_r3:
        # data for all pitchers from 2015 to 2022
        # pitchers_stats_1522_all = pd.read_csv(
        #     "./data/pitching/pitch_stats_all_players_1522_df.csv"
        # )

        # add database name and collection name from your MongoDB
        pitchers_stats_1522_all = db.create_df_from_mongo(
            db_name="", collection_name=""
        )

        col1, col2, col3 = st.columns(3)
        # Filter 2.1: Year
        default_idx = list(pitchers_stats_1522_all["Year"].unique()).index(2022)
        year_comparison = col1.selectbox(
            "Select Year:", pitchers_stats_1522_all["Year"].unique(), index=default_idx
        )

        # Filter 2.2: Pitcher name
        default_idx_2 = list(pitchers_stats_1522_all["Name"].unique()).index(
            "Cease, Dylan"
        )
        pitcher_comparison = col2.selectbox(
            "Select Pitcher:",
            pitchers_stats_1522_all["Name"].unique(),
            index=default_idx_2,
        )

        df_selection = pitchers_stats_1522_all.query(
            "Year == @year_comparison\
                & Name == @pitcher_comparison"
        )

        cf.pitch_usage(df_selection, year_comparison, pitcher_comparison)
        st.write(
            "*Caveats: Data contains only pitchers whose IPs >= 100 and ERA < 4.00 in a given season.*"
        )

    st.markdown("---")

    # ----------- Pitching Defense Analysis -----------
    st.markdown("### :blue[Pitching Defense Analysis]")
    # Row for additional chart: pitching stats against by inning
    extra_col_1, extra_col_2 = st.columns([2, 1])
    with extra_col_1:
        # load files
        # data for Shohei Ohtani 2022
        # pitching_stats_against_22_sho = pd.read_csv("pitching_stats_against_22_sho.csv")
        # data for Shohei Ohtani 2018 ~ 2022
        # pitching_stats_against_1822_sho = pd.read_csv(
        #     "./data/pitching/pitching_stats_against_1822_sho.csv"
        # )

        # add database name and collection name from your MongoDB
        pitching_stats_against_1822_sho = db.create_df_from_mongo(
            db_name="", collection_name=""
        )

        # data for all eligible pitchers 2015 ~ 2022
        # pitching_stats_against_1522_all = pd.read_csv(
        #     "./data/pitching/pitching_stats_against_1522_all.csv"
        # )

        # add database name and collection name from your MongoDB
        pitching_stats_against_1522_all = db.create_df_from_mongo(
            db_name="", collection_name=""
        )

        # data for MLB average pitchers 2022
        # baa_by_inning_mlb_mean_22 = pd.read_csv("baa_by_inning_mlb_mean_22.csv")
        # data for MLB average pitchers 2015 ~ 2022
        # baa_by_inning_mlb_mean_1522 = pd.read_csv(
        #     "./data/pitching/baa_by_inning_all_1522_reg.csv"
        # )

        # add database name and collection name from your MongoDB
        baa_by_inning_mlb_mean_1522 = db.create_df_from_mongo(
            db_name="", collection_name=""
        )

        col1, col2, col3, col4 = st.columns(4)

        # Filter 1 for Ohtani-san
        default_idx = list(pitching_stats_against_1822_sho["year"].unique()).index(2022)
        season_sho = col1.selectbox(
            "Select Season for Shohei Ohtani",
            pitching_stats_against_1822_sho["year"].unique(),
            index=default_idx,
        )

        # Filter 2 for other eligible pitchers
        default_idx_2 = list(pitching_stats_against_1522_all["year"].unique()).index(
            2022
        )
        season_all = col3.selectbox(
            "Select Season for other pitcher",
            pitching_stats_against_1522_all["year"].unique(),
            index=default_idx_2,
        )
        default_idx_3 = list(pitching_stats_against_1522_all["pitcher"].unique()).index(
            "Cease, Dylan"
        )
        pitcher_all = col4.selectbox(
            "Select pitcher",
            pitching_stats_against_1522_all["pitcher"].unique(),
            index=default_idx_3,
        )

        # # Filter 3 for MLB average
        # default_idx_4 = list(baa_by_inning_mlb_mean_1522['year'].unique()).index(2022)
        # season_mlb = col4.selectbox(
        #     'Select Season for MLB Average Pitchers',
        #     baa_by_inning_mlb_mean_1522['year'].unique(),
        #     index=default_idx_4
        # )

        # df for selection
        df_selection = pitching_stats_against_1822_sho.query("year == @season_sho")

        # df for selection 2
        df_selection_2 = pitching_stats_against_1522_all.query(
            "year == @season_all\
                & pitcher == @pitcher_all"
        )

        # # df for selection 3
        # df_selection_3 = baa_by_inning_mlb_mean_1522.query(
        #     'year == @season_mlb'
        # )

        # chart
        # line chart for BAA by inning
        fig_baa_by_inning = go.Figure(
            data=[
                # ++++++++++++++ data for Ohtani-san ++++++++++++++++++
                go.Scatter(
                    x=df_selection["inning"],
                    y=df_selection["baa"],
                    name=f"BAA (Shohei Ohtani) in {season_sho}",
                    # customdata=ba_at_strike_count_sho_22['year'],
                    marker=dict(color="Coral"),
                    mode="lines+markers+text",
                    text=list(df_selection["baa"]),
                    textposition="top center",
                    # fill='tozeroy',
                    hovertemplate="<br>".join(
                        [
                            "BAA: %{y:.3f}",
                            "Inning: %{x}",
                        ]
                    ),
                ),
                # bar chart for HRs allowed
                go.Bar(
                    x=df_selection["inning"],
                    y=df_selection["hr_allowed"],
                    yaxis="y2",
                    marker=dict(color="Crimson"),
                    # offsetgroup=0,
                    name=f"HRs allowed (Shohei Ohtani) in {season_sho}",
                    text=list(df_selection["hr_allowed"]),
                    textposition="outside",
                    opacity=1,
                    hovertemplate="<br>".join(
                        [
                            "HR allowed: %{y}",
                            "Inning: %{x}",
                        ]
                    ),
                    offsetgroup=0,
                ),
                # bar chart for hits allowed
                go.Bar(
                    x=df_selection["inning"],
                    y=df_selection["hits_allowed"],
                    yaxis="y2",
                    marker=dict(color="DarkKhaki"),
                    # offsetgroup=0,
                    name=f"Hits allowed (Shohei Ohtani) in {season_sho}",
                    text=list(df_selection["hits_allowed"]),
                    textposition="outside",
                    opacity=0.6,
                    hovertemplate="<br>".join(
                        [
                            "Hits allowed: %{y}",
                            "Inning: %{x}",
                        ]
                    ),
                    offsetgroup=0,
                ),
                # ++++++++++++++ data for other eligible pitchers ++++++++++++++++++
                go.Scatter(
                    x=df_selection_2["inning"],
                    y=df_selection_2["baa"],
                    name=f"BAA {pitcher_all} in {season_all}",
                    # customdata=ba_at_strike_count_sho_22['year'],
                    marker=dict(color="SteelBlue"),
                    mode="lines+markers+text",
                    text=list(df_selection_2["baa"]),
                    textposition="top center",
                    # fill='tozeroy',
                    hovertemplate="<br>".join(
                        [
                            "BAA: %{y:.3f}",
                            "Inning: %{x}",
                        ]
                    ),
                ),
                # bar chart for HRs allowed
                go.Bar(
                    x=df_selection_2["inning"],
                    y=df_selection_2["hr_allowed"],
                    yaxis="y2",
                    marker=dict(color="PaleTurquoise"),
                    name=f"HRs allowed {pitcher_all} in {season_all}",
                    text=list(df_selection_2["hr_allowed"]),
                    textposition="outside",
                    opacity=1,
                    hovertemplate="<br>".join(
                        [
                            "HR allowed: %{y}",
                            "Inning: %{x}",
                        ]
                    ),
                    offsetgroup=2,
                ),
                # bar chart for hits allowed
                go.Bar(
                    x=df_selection_2["inning"],
                    y=df_selection_2["hits_allowed"],
                    yaxis="y2",
                    marker=dict(color="MediumSeaGreen"),
                    name=f"Hits allowed {pitcher_all} in {season_all}",
                    text=list(df_selection_2["hits_allowed"]),
                    textposition="outside",
                    opacity=0.6,
                    hovertemplate="<br>".join(
                        [
                            "Hits allowed: %{y}",
                            "Inning: %{x}",
                        ]
                    ),
                    offsetgroup=2,
                ),
                # # ------------ data for MLB average -----------------
                # go.Scatter(
                #     x=df_selection_3['inning'],
                #     y=df_selection_3['baa'],
                #     name=f'BAA (MLB Average) in {season_mlb}',
                #     # customdata=ba_at_strike_count_sho_22['year'],
                #     marker=dict(color="SteelBlue"),
                #     mode='lines+markers+text',
                #     text=list(df_selection_3['baa']),
                #     textposition="top right",
                #     # fill='tozeroy',
                #     hovertemplate='<br>'.join([
                #         'BAA: %{y:.3f}',
                #         'Inning: %{x}',
                #     ]),
                # ),
                # # bar chart for HRs allowed
                # go.Bar(
                #     x=df_selection_3['inning'],
                #     y=df_selection_3['avg_hr_allowed'],
                #     yaxis='y2',
                #     marker=dict(color="PaleTurquoise"),
                #     name=f'HRs allowed (MLB Average) in {season_mlb}',
                #     text=list(df_selection_3['avg_hr_allowed']),
                #     textposition='outside',
                #     opacity=1,
                #     hovertemplate='<br>'.join([
                #         'HR allowed: %{y}',
                #         'Inning: %{x}',
                #     ]),
                #     offsetgroup=1
                # ),
                # # bar chart for hits allowed
                # go.Bar(
                #     x=df_selection_3['inning'],
                #     y=df_selection_3['avg_hits_allowed'],
                #     yaxis='y2',
                #     marker=dict(color="MediumSeaGreen"),
                #     name=f'Hits allowed (MLB Average) in {season_mlb}',
                #     text=list(df_selection_3['avg_hits_allowed']),
                #     textposition='outside',
                #     opacity=0.6,
                #     hovertemplate='<br>'.join([
                #         'Hits allowed: %{y}',
                #         'Inning: %{x}',
                #     ]),
                #     offsetgroup=1
                # ),
            ]
        )

        # update figure layout
        fig_baa_by_inning.update_layout(
            title="Shohei Ohtani Pitching Stats Against by Inning<br><sup>MLB average stats are calculated with starting pitchers whose pitch coutns >= 2,000</sup>",
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor="rgb(102, 102, 102)",
                tickfont_color="rgb(102, 102, 102)",
                showticklabels=True,
                dtick=1,
                ticks="outside",
            ),
            yaxis=dict(
                title=dict(text="BAA"),
                side="left",
                dtick=0.05,
                range=[0, 0.6],
            ),
            yaxis2=dict(
                title=dict(text="Hits Allowed"),
                side="right",
                range=[0, 40],
                overlaying="y",
                # tickmode="sync",
            ),
            barmode="group",
            # margin=dict(l=140, r=40, b=50, t=80),
            legend=dict(
                # orientation='h',
                font_size=12,
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=1,
                # bgcolor="LightSteelBlue",
            ),
            width=800,
            height=700,
        )

        fig_baa_by_inning.update_xaxes(title_text="Inning")
        st.plotly_chart(fig_baa_by_inning, use_container_width=True)

    # Row 4 for filters
    left_column_r4, right_column_r4 = st.columns(2)
    with left_column_r4:
        col1, col2 = st.columns([1, 3])

        # Filter 1
        pitching_season = col1.selectbox(
            "Select Season(s):",
            season_pitcher_stats_all["Season"].unique(),
            key="pitching_season",
        )

        # Filter 2
        # league = st.sidebar.multiselect(
        #     'Select League:',
        #     options = master_batting_stats_all_1522['League'].unique(),
        #     default = 'AL'
        # )

        # Filter 3
        max_ip = int(season_pitcher_stats_all["IP"].max())
        min_ip = int(season_pitcher_stats_all["IP"].min())

        ip = col2.slider(
            "Select Innings Pitched range:",
            # options=[min_pa, max_pa]
            value=(130, max_ip),
            step=10,
        )

        df_selection_comparison = season_pitcher_stats_all.query(
            "Season == @pitching_season\
                    & IP >= @ip[0] & IP <= @ip[1]"
        )

    # Row 5 for charts
    left_column_r5, right_column_r5 = st.columns(2)

    with left_column_r5:
        # Chart 6: ERA+ ranking
        cf.stat_ranking(
            df=df_selection_comparison,
            x="Name",
            y="ERA+",
            league="MLB",
            year=pitching_season,
            sortValue="ERA+",
            topNumber=20,
            title="ERA+",
            orientation="v",
            color="ERA+",
            textAuto=".3s",
            colorScale=px.colors.diverging.BrBG,
        )

        # tab1, tab2 = st.tabs(['Chart', 'Dataframe'])
        # with tab1:
        #     st.plotly_chart(fig_6, use_container_width=True)
        # with tab2:
        #     st.dataframe(df_selection_comparison)

    with right_column_r5:
        # Chart 7: ERA+ vs. WAR
        cf.fig_war_comparison(
            df=df_selection_comparison,
            x="bWAR_pitcher",
            y="ERA",
            sortValue="bWAR_pitcher",
            topNumber=20,
            league="MLB",
            color="bWAR_pitcher",
            size="bWAR_pitcher",
            colorScale=px.colors.diverging.Tealrose,
            season=pitching_season,
            title="Pitcher",
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
