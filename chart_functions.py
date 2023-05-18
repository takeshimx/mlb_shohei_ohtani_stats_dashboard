import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Pitching
# --------------- plot for Pitch Movement, Position, & Speed ---------------------

def fig_pitch_stats(df, x, y, pitcherName, year, titleVar=None):
    fig = px.scatter(df,
                    x=x,
                    y=y,
                    color='pitch_name',
                    hover_name='pitch_name')

    # fig_pitch_distribution_sho.add_selection(x0=-1.41667, y0=1.5748, x1=1.41667, y1=3.41207)

    # add annotation that shows each pitch type summary

    fig.update_layout(
        title=f'{pitcherName} {titleVar} in {year}',
        legend=dict(
            title='Pitch Name'
        ),
        xaxis=dict(
            title=f'Horizontal {titleVar} (ft)',
            dtick=0.5
        ),
        yaxis=dict(
            title=f'Vertical {titleVar} (ft)',
            dtick=0.5
        ),
        width=800,
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------- plot for Pitch Usage ---------------------

# TODO: Create color scale dictionary by pitch type
def SetColor(y):
        if (y == '4-Seam Fastball'):
            return 'seagreen'
        elif (y == 'Sweeper'):
            return 'goldenrod'
        elif (y == 'Curveball'):
            return 'steelblue'
        elif (y == 'Sinker'):
            return 'lightpink'
        elif (y == 'Slider'):
            return 'plum'
        elif (y == 'Split-Finger'):
            return 'lightcoral'
        elif (y == 'Cutter'):
            return 'dodgerblue'
        elif (y == 'Slow Curve'):
            return 'rosybrown'
        elif (y == 'Knuckle Curve'):
            return 'sandybrown'
        elif (y == 'Changeup'):
            return 'tan'
        elif (y == 'Slurve'):
            return 'mistyrose'
        elif (y == 'Knuckleball'):
            return 'silver'
        elif (y == 'Screwball'):
            return 'beige'
        elif (y == 'Eephus'):
            return 'peachpuff'
        else:
            return 'blanchedalmond'

def pitch_usage(df, year, pitcher=None):
    
    fig = go.Figure(
        go.Bar(
            x=df['Pitch type'],
            y=df['Pitch %'],
            orientation='v',
            marker=dict(
                color=list(map(SetColor, df['Pitch type']))
            ),
            # text=df['Pitch %'],
        )
    )
    
    fig.update_layout(
            title=f'{pitcher} Pitch Usage in {year}<br><sup></sup>',
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
    
    st.plotly_chart(fig, use_container_width=True)

# def pitch_usage(df, year, pitcher=None):
#     fig = px.bar(df,
#                 x=df['Pitch type'],
#                 y=df['Pitch %'],
#                 orientation='v',
#                 # color_discrete_map=pitch_type_color_dict,
#                 color='Pitch type',
#                 text_auto='.1%',
#                 template='seaborn')

#     fig.update_layout(
#             title=f'{pitcher} Pitch Usage in {year}<br><sup></sup>',
#             xaxis=dict(
#                 title='Pitch type',
#                 gridcolor='white',
#                 gridwidth=2,
#                 showgrid=False
#             ),
#             yaxis=dict(
#                 title='Pitch Usage',
#                 gridcolor='white',
#                 gridwidth=2,
#                 tickformat='.1%'
#             )
#         )
    
#     st.plotly_chart(fig, use_container_width=True)

# Batting
# --------------- relationship bwtween Batting Speed and Angle ---------------
def fig_batting_speed_angle(df, year, sizeMetric, colorField, title=None, legendTitle=None):

    fig = px.scatter(df,
                        x='launch_speed',
                        y='launch_angle',
                        color=colorField, 
                        hover_name='events',
                        size=sizeMetric,
                        size_max=10,
                        template='plotly_dark')

    fig.update_layout(
        title=f'{title} in {year}<br><sup></sup>',
        legend=dict(
            title=legendTitle
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
    
    st.plotly_chart(fig, use_container_width=True)

# --------------- histogram for Batting Speed and Angle ---------------
def fig_hist_speed_angle(df, year, x, xTitle):

    fig = px.histogram(
        df,
        x=x,
        nbins=60,
        color='events',
        barmode='overlay',
        marginal='box',
        hover_name='events',
        # hover_data=batter_events_sho.columns,
        template='seaborn'
    )

    fig.update_layout(
        title=f'{xTitle} in {year}<br><sup></sup>',
        legend=dict(
            title='Batting event'
        ),
        xaxis=dict(
            title=xTitle,
            dtick=20
        ),
        yaxis=dict(
            title='Count',
            dtick=20
        ),
        width=800,
        height=700,
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------- plot for BA and HR at each strike count ---------------

def fig_ba_hr(df, playerSelectionVar=None, yearSelectionVar=None):
    """
    INPUTS:
        df: dataframe for batting stats at each strike count
        playerSelectionVar: variable for player name selection
        yearSelectionVar: variable for year selection
    
    OUTPUT: a chart
    """

    # line chart for ba at strike count
    fig = go.Figure(
        data=go.Scatter(
            x=df['strike_count'],
            y=df['ba'],
            name='Batting Average',
            customdata=df['year'],
            marker=dict(color="DarkGoldenrod"),
            mode='lines+markers+text',
            text=list(df['ba']),
            textposition="top left",
            hovertemplate='<br>'.join([
                'Batting Average: %{y:.3f}',
                'Strike Count: %{x}',
                'Season: %{customdata}',
            ]),
            )
            )

    # bar chart for HR at strike count
    fig.add_trace(go.Bar(
        x=df['strike_count'],
        y=df['hr'],
        yaxis='y2',
        name='HR',
        customdata=df['year'],
        marker=dict(color="DarkSeaGreen"),
        width=0.6,
        opacity=0.8,
        hovertemplate='<br>'.join([
            'HR: %{y}',
            'Strike Count: %{x}',
            'Season: %{customdata}',
        ]),
        text=df['hr'],
        textposition='outside'
        )
        )

    # update figure layout
    fig.update_layout(
        title=f'{playerSelectionVar} BA and HR at strike count in {yearSelectionVar}',
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='rgb(102, 102, 102)',
            tickfont_color='rgb(102, 102, 102)',
            showticklabels=True,
            dtick=1,
            ticks='outside',
        ),
        yaxis=dict(
            title=dict(text="Batting Average"),
            side="left",
            dtick=0.05,
            range=[0, 0.8],
        ),
        yaxis2=dict(
            title=dict(text="HR"),
            side="right",
            range=[0, 30],
            overlaying="y",
            # tickmode="sync",
        ),
        margin=dict(l=140, r=40, b=50, t=80),
        legend=dict(
            orientation='h',
            font_size=10,
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ),
        width=800,
        height=600,
        # plot_bgcolor='Linen',
    )

    fig.update_xaxes(title_text="Strike Count")

    st.plotly_chart(fig, use_container_width=True)


# ------------------ Chart for batting stats at RISP --------------------

# plot
# line chart for stats at RISP

def fig_stats_at_risp(df, playerSelectionVar=None):

    fig = go.Figure(
    data=[
        go.Scatter(
            x=df['Season'].sort_values(ascending=True),
            y=df['BA'],
            name='Batting Average',
            # customdata=ba_at_strike_count_sho_22['year'],
            marker=dict(color="DarkOrange"),
            mode='lines+markers+text',
            text=list(df['BA']),
            textposition="top right",
            hovertemplate='<br>'.join([
                'Batting Average: %{y:.3f}',
                'Season: %{x}',
            ]),
        ),
        # bar chart for SLG at RISP
        go.Scatter(
            x=df['Season'].sort_values(ascending=True),
            y=df['SLG'],
            # yaxis='y2',
            name='SLG',
            # customdata=ba_at_strike_count_sho_22['year'],
            marker=dict(color="Olive"),
            mode='lines+markers+text',
            # width=0.6,
            hovertemplate='<br>'.join([
                'SLG: %{y:.3f}',
                'Season: %{x}',
            ]),
            text=df['SLG'],
            textposition='top right'
        ),
        # bar chart for extra bases hits
        go.Bar(
            x=df['Season'],
            y=df['HR'],
            yaxis='y2',
            marker=dict(color="Goldenrod"),
            # offsetgroup=0,
            name='Home Run',
            text=df['HR'],
            textposition='inside',
            opacity=0.8,
            hovertemplate='<br>'.join([
                'HR: %{y}',
                'Season: %{x}',
            ]),
        ),
        go.Bar(
            x=df['Season'],
            y=df['Triple'],
            yaxis='y2',
            marker=dict(color="MediumAquamarine"),
            # offsetgroup=0,
            name='Triple',
            text=df['Triple'],
            textposition='inside',
            opacity=0.8,
            hovertemplate='<br>'.join([
                'Triple: %{y}',
                'Season: %{x}',
            ]),
        ),
        go.Bar(
            x=df['Season'],
            y=df['Double'],
            yaxis='y2',
            marker=dict(color="DarkSalmon"),
            # offsetgroup=0,
            name='Double',
            text=df['Double'],
            textposition='inside',
            opacity=0.8,
            hovertemplate='<br>'.join([
                'Double: %{y}',
                'Season: %{x}',
            ]),
        ),
            ]
        )

    # update figure layout
    fig.update_layout(
        title=f'{playerSelectionVar} Batting Stats at RISP',
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='rgb(102, 102, 102)',
            tickfont_color='rgb(102, 102, 102)',
            showticklabels=True,
            dtick=1,
            ticks='outside',
        ),
        yaxis=dict(
            title=dict(text="Batting Average & Slugging"),
            side="left",
            dtick=0.05,
            range=[0, 1],
        ),
        yaxis2=dict(
            title=dict(text="XBH"),
            side="right",
            range=[0, 40],
            overlaying="y",
            # tickmode="sync",
        ),
        barmode='stack',
        # margin=dict(l=140, r=40, b=50, t=80),
        legend=dict(
            orientation='h',
            font_size=10,
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ),
        width=800,
        height=600,
        # paper_bgcolor='white',
        # plot_bgcolor='AliceBlue'
    )

    fig.update_xaxes(title_text="Season")

    st.plotly_chart(fig, use_container_width=True)

# Common
# ------------------ Stats ranking ------------------
def stat_ranking(df, x, y, year, topNumber, sortValue, title, orientation, color, textAuto, league=None, colorTemplate=None, colorScale=None):
    fig = px.bar(df.sort_values(sortValue, ascending=False)[:topNumber],
                                x=x,
                                y=y,
                                orientation=orientation,
                                color=color,
                                hover_name=y,
                                text_auto=textAuto,
                                color_continuous_scale=colorScale,
                                template=colorTemplate)

    fig.update_traces(textfont_size=12,
                                textangle=0,
                                textposition="outside",
                                cliponaxis=False
                                )

    fig.update_layout(
        title=f'{title} {league} Top {topNumber} Players in {year}<br><sup>Average player {title} = 100</sup>',
        legend=dict(
            title=title
        ),
        barmode='stack',
        xaxis=dict(
            title=title,
            # dtick=10
        ),
        yaxis={'categoryorder':'total ascending'},
        width=800,
        height=700,
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------ Chart for WAR vs. ERA or OPS --------------------

def fig_war_comparison(df, x, y, sortValue, topNumber, league, color, size, colorScale, season, title):
    """
    INPUTS:
        df: specifically formatted dataframe
        positionType: (String) 'pitcher' or 'batter'
        season: baseball annual season
        metric: (String) 'ERA' or 'OPS'
    OUTPUT: chart for the cmparison with WAR
    """
    fig = px.scatter(df.sort_values(sortValue, ascending=False)[:topNumber],
                                x=x,
                                y=y,
                                color=color,
                                hover_name='Name',
                                size=size,
                                size_max=12,
                                text='Name',
                                color_continuous_scale=colorScale,
                                template='plotly_dark')

    fig.update_traces(textposition='top center')

    fig.update_layout(
        title=f'{title} WAR vs. {y} for Top {topNumber} {league} Players in {season}<br><sup></sup>',
        legend=dict(
            title=x
        ),
        xaxis=dict(
            title=x
        ),
        yaxis=dict(
            title=y,
            dtick=0.05
        ),
        width=800,
        height=700,
    )

    st.plotly_chart(fig, use_container_width=True)