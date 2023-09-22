# CONSTANT variales
# make a list for each event
SWINGING_STRIKES_EVENTS = ["swinging_strike", "swinging_strike_blocked"]
SWING_EVENTS = [
    "foul",
    "foul_bunt",
    "foul_tip",
    "hit_into_play",
    "missed_bunt",
] + SWINGING_STRIKES_EVENTS


# create a function WHIFF% by pitch type
def whiff(df, pitchType):
    """
    INPUTS:
        df: data frame
        pitchType: pitch type, e.g. Sweeper
    OUTPUT:
        WHIFF rate
    """
    # create a dtaframe pitch count for a specific pitch type
    df = (
        df.loc[df["pitch_name"] == pitchType]
        .groupby(["pitch_name", "description"])
        .size()
        .reset_index()
    )

    # counts *fyi, 0 is a column name for count
    swinging_strikes = df.loc[df["description"].isin(SWINGING_STRIKES_EVENTS)][0].sum()
    total_swings = df.loc[df["description"].isin(SWING_EVENTS)][0].sum()

    return round(swinging_strikes / total_swings, 3)


# create a function Chase rate by pitch type
def chase_rate(df, pitchType):
    """
    INPUTS:
        df: data frame
        pitchType: pitch type, e.g. Sweeper
    OUTPUT:
        Chase rate
        total swings to balls
    """
    # filter df to onclude only ball zone events
    ball_zone_list = [11, 12, 13, 14]
    df = df.loc[df["zone"].isin(ball_zone_list)]

    # create a dtaframe pitch count for a specific pitch type
    df = (
        df.loc[df["pitch_name"] == pitchType]
        .groupby(["pitch_name", "description"])
        .size()
        .reset_index()
    )

    # counts *fyi, 0 is a column name for count
    total_swings_to_balls = df.loc[df["description"].isin(SWING_EVENTS)][0].sum()
    total_ball_zones = df[0].sum()

    return round(total_swings_to_balls / total_ball_zones, 3), total_swings_to_balls
