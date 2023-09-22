import pandas as pd
import baseball_metrics as sm
from pybaseball import *
import functions as f
import database as db

# ----------------- Pitching -----------------
# load pitching data for all MLB pitchers in 2022
# pitching_data_all_22 = pd.read_csv("./data/pitching/pitching_data_all_22_df.csv")

# add database name and collection name from your MongoDB
pitching_data_all_22 = db.create_df_from_mongo(db_name="", collection_name="")

# data for Shohei Ohtani 2022
pitching_data_sho_22 = pitching_data_all_22.loc[
    pitching_data_all_22["player_name"] == "Ohtani, Shohei"
]
# data for Shohei Ohtani all seasons
# pitching_data_sho_all = pd.read_csv("./data/pitching/pitching_data_sho_all.csv")

# add database name and collection name from your MongoDB
pitching_data_sho_all = db.create_df_from_mongo(db_name="", collection_name="")
pitching_data_sho_all = pitching_data_sho_all.loc[
    ~pitching_data_sho_all["pitch_name"].isnull()
]


# create a function to create each stat from all MLB players
def all_pitchers_stats():
    # create a data frame for pitching stats by pitch type for all pitchers
    pitch_type_list_all = list(pitching_data_all_22["pitch_name"].unique())

    df_all = []

    for j in pitch_type_list_all:
        # metrics
        avg_release_speed = pitching_data_all_22[
            pitching_data_all_22["pitch_name"] == j
        ]["release_speed"].agg("mean")
        pitch_counts = len(
            pitching_data_all_22[pitching_data_all_22["pitch_name"] == j]
        )
        pitch_pct = len(
            pitching_data_all_22.loc[pitching_data_all_22["pitch_name"] == j]
        ) / len(pitching_data_all_22)
        # RPM: revolutions per minute
        avg_release_spin_rate = pitching_data_all_22[
            pitching_data_all_22["pitch_name"] == j
        ]["release_spin_rate"].agg("mean")
        max_release_spin_rate = pitching_data_all_22[
            pitching_data_all_22["pitch_name"] == j
        ]["release_spin_rate"].max()
        min_release_spin_rate = pitching_data_all_22[
            pitching_data_all_22["pitch_name"] == j
        ]["release_spin_rate"].min()

        df_all.append(
            {
                "Pitch type": j,
                "WHIFF rate": sm.whiff(pitching_data_all_22, j),
                "Average release speed (mph)": round(avg_release_speed, 2),
                "Pitch counts": pitch_counts,
                "Pitch %": pitch_pct,
                "Average release spin rate (rpm)": round(avg_release_spin_rate),
                "Max release spin rate (rpm)": round(max_release_spin_rate),
                "Min release spin rate (rpm)": round(min_release_spin_rate),
                "Chase rate": sm.chase_rate(pitching_data_all_22, j)[0],
                "Total swings to balls": sm.chase_rate(pitching_data_all_22, j)[1],
            }
        )

    pitch_stats_df_all = pd.DataFrame(df_all)
    return pitch_stats_df_all


# 1) create a function to create an indivdual data frame of pitch stats
def individual_pitcher_stats(playerId):
    # filter out to a specific player
    player_df = pitching_data_all_22.loc[pitching_data_all_22["pitcher"] == playerId]
    # create a data frame for pitching stats by pitch type for an individual player
    pitch_type_list_all = list(player_df["pitch_name"].unique())

    individual_player_stats = []

    for i in pitch_type_list_all:
        # metrics
        avg_release_speed = player_df[player_df["pitch_name"] == i][
            "release_speed"
        ].agg("mean")
        pitch_counts = len(player_df[player_df["pitch_name"] == i])
        pitch_pct = len(player_df.loc[player_df["pitch_name"] == i]) / len(player_df)
        # RPM: revolutions per minute
        avg_release_spin_rate = player_df[player_df["pitch_name"] == i][
            "release_spin_rate"
        ].agg("mean")
        max_release_spin_rate = player_df[player_df["pitch_name"] == i][
            "release_spin_rate"
        ].max()
        min_release_spin_rate = player_df[player_df["pitch_name"] == i][
            "release_spin_rate"
        ].min()

        individual_player_stats.append(
            {
                "Pitch type": i,
                "WHIFF rate": sm.whiff(player_df, i),
                "Average release speed (mph)": round(avg_release_speed, 2),
                "Pitch counts": pitch_counts,
                "Pitch %": pitch_pct,
                "Average release spin rate (rpm)": round(avg_release_spin_rate),
                "Max release spin rate (rpm)": round(max_release_spin_rate),
                "Min release spin rate (rpm)": round(min_release_spin_rate),
                "Chase rate": sm.chase_rate(player_df, i)[0],
                "Total swings to balls": sm.chase_rate(player_df, i)[1],
            }
        )

    pitch_stats_df_player = pd.DataFrame(individual_player_stats)
    pitch_stats_df_player["MLB ID"] = playerId
    pitch_stats_df_player["Name"] = list(
        pitching_data_all_22.loc[pitching_data_all_22["pitcher"] == playerId][
            "player_name"
        ]
    )[0]

    return pitch_stats_df_player


# 2) create a function to to concat all individual players stats data frames, and adding more stats (caveat: this is not stats for all pitchers stats mixed)
def individual_pitchers_all_stats():
    # for loop all pitchers IDs and concat them by using individual_pitcher_stats function
    pitchers_all = [
        individual_pitcher_stats(player)
        for player in list(pitching_data_all_22["pitcher"].unique())
    ]
    pitchers_all_df = pd.concat(pitchers_all)

    return pitchers_all_df


# function for updating pitch_stats_df_all data frame
def all_pitchers_stats_b():
    # new stat: calculate avg Total swings to balls per pitch type
    # formula = (total swings to balls for all pitchers per pitch type) / (number of pitchers per pitch type)

    pitchers_all_df = individual_pitchers_all_stats()
    # total swings to balls for all pitchers per pitch type
    total_swings_to_balls = (
        pitchers_all_df.groupby("Pitch type")
        .sum()["Total swings to balls"]
        .reset_index()
    )
    # number of pitchers per pitch type
    num_of_pitchers_tstb = (
        pitchers_all_df.groupby("Pitch type").count()["Name"].reset_index()
    )
    tstb_merged = total_swings_to_balls.merge(
        num_of_pitchers_tstb, on="Pitch type", how="left"
    ).rename(columns={"Name": "Num of pitchers"})
    # new column for the new stat
    tstb_merged["Average total swings to balls"] = round(
        tstb_merged["Total swings to balls"] / tstb_merged["Num of pitchers"], 1
    )

    # merge it with pitch_stats_df_all
    pitch_stats_df_all = all_pitchers_stats()
    pitch_stats_df_all_b = pitch_stats_df_all.merge(
        tstb_merged[["Pitch type", "Num of pitchers", "Average total swings to balls"]],
        on="Pitch type",
        how="left",
    )

    return pitch_stats_df_all_b


# 1)-v2: create a function to create an indivdual data frame of pitch stats
def individual_pitcher_stats_v2(df, playerId, startSeason, endSeason):
    years = list(range(startSeason, endSeason + 1))

    individual_player_all_season = []

    for year in years:
        # filter out to a specific player and season
        player_df = df.loc[(df["pitcher"] == playerId) & (df["game_year"] == year)]
        # drop rows where 'pitch_name' is null
        player_df = player_df.loc[~player_df["pitch_name"].isnull()]
        # create a data frame for pitching stats by pitch type for an individual player
        pitch_type_list_all = list(player_df["pitch_name"].unique())

        individual_player = []

        for i in pitch_type_list_all:
            # metrics
            avg_release_speed = player_df[player_df["pitch_name"] == i][
                "release_speed"
            ].agg("mean")
            pitch_counts = len(player_df[player_df["pitch_name"] == i])
            pitch_pct = len(player_df.loc[player_df["pitch_name"] == i]) / len(
                player_df
            )
            # RPM: revolutions per minute
            avg_release_spin_rate = player_df[player_df["pitch_name"] == i][
                "release_spin_rate"
            ].agg("mean")
            max_release_spin_rate = player_df[player_df["pitch_name"] == i][
                "release_spin_rate"
            ].max()
            min_release_spin_rate = player_df[player_df["pitch_name"] == i][
                "release_spin_rate"
            ].min()
            season = int(player_df[player_df["pitch_name"] == i]["game_year"].values[0])

            individual_player.append(
                {
                    "Pitch type": i,
                    "WHIFF rate": sm.whiff(player_df, i),
                    "Average release speed (mph)": round(avg_release_speed, 2),
                    "Pitch counts": pitch_counts,
                    "Pitch %": pitch_pct,
                    "Average release spin rate (rpm)": round(avg_release_spin_rate),
                    "Max release spin rate (rpm)": round(max_release_spin_rate),
                    "Min release spin rate (rpm)": round(min_release_spin_rate),
                    "Chase rate": sm.chase_rate(player_df, i)[0],
                    "Total swings to balls": sm.chase_rate(player_df, i)[1],
                    "Year": season,
                }
            )

        pitch_stats_df_player = pd.DataFrame(individual_player)
        pitch_stats_df_player["MLB ID"] = playerId
        pitch_stats_df_player["Name"] = list(
            df.loc[df["pitcher"] == playerId]["player_name"]
        )[0]
        # pitch_stats_df_player['Year'] = year

        individual_player_all_season.append(pitch_stats_df_player)

    pitch_stats_df_player = pd.concat(individual_player_all_season)
    return pitch_stats_df_player


# create a function for pitcher stats ranking
def stats_rank_pitcher(pitcher_df, metric, year):
    pitcher_df = pitcher_df.loc[
        (pitcher_df["Season"] == year) & (pitcher_df["IP"] >= 100)
    ].sort_values(metric, ascending=True)
    pitcher_df["Rank"] = list(range(1, pitcher_df.shape[0] + 1))

    return pitcher_df


# create a function for stat delta from previous season
def stats_delta_pitcher(pitcher_df, player, metric, year):
    pitcher_df = pitcher_df.loc[
        (pitcher_df["Name"] == player) & (pitcher_df["IP"] >= 100)
    ].sort_values("Season", ascending=True)

    # if stat for a give season exists
    if year in list(pitcher_df["Season"].unique()):
        current_year_stat = pitcher_df.loc[pitcher_df["Season"] == year][metric].values[
            0
        ]
    else:
        return "No data found"

    if year - 1 in list(pitcher_df["Season"].unique()):
        prev_year_stat = pitcher_df.loc[pitcher_df["Season"] == year - 1][
            metric
        ].values[0]
    else:
        return "No data found"

    delta = current_year_stat - prev_year_stat

    return delta


# ----------------- Batting -----------------
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
    player_mlbid = int(
        playerid_lookup(lastName.lower(), firstName.lower())["key_mlbam"]
    )
    # create a data frame with the given ID
    batter_player_data = statcast_batter(startDate, endDate, player_mlbid)
    # add a new column
    batter_player_data["launch_speed_angle_definition"] = batter_player_data.apply(
        f.launch_speed_angle_zone, axis=1
    )

    return batter_player_data


def launch_speed_angle_zone(row):
    if row["launch_speed_angle"] == 6:
        return "Barrel"
    elif row["launch_speed_angle"] == 5:
        return "Solid Contact"
    elif row["launch_speed_angle"] == 4:
        return "Flare/Burner"
    elif row["launch_speed_angle"] == 3:
        return "Under"
    elif row["launch_speed_angle"] == 2:
        return "Topped"
    else:
        return "Weak"
