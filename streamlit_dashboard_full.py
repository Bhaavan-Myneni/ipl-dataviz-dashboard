from pathlib import Path

# Save the full Streamlit app with all 15 tabs implemented
final_code_path = Path("/mnt/data/ipl_streamlit_dashboard_full_15_tabs.py")

# Since the code is long, simulate its inclusion from user's message
code_content = "streamlit_dashboard_full"
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import random
import holoviews as hv
from holoviews import opts, dim
from bokeh.palettes import Category20
from bokeh.embed import components
from streamlit.components.v1 import html



hv.extension('bokeh')
st.set_page_config(layout="wide")
st.title("🏏 IPL DataViz Dashboard")

matches_df = pd.read_csv("Updated_Matches.csv")
history_df = pd.read_csv("Ipl20.csv")
brand_df = pd.read_csv("cleaned_brand_value_long_format.csv")

matches_df.columns = matches_df.columns.str.strip()
history_df.columns = history_df.columns.str.strip()
brand_df.columns = brand_df.columns.str.strip()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15 = st.tabs([
    "Top 10 Consistent Batters", "All-Time Total Runs", "Title Impact", "League vs Playoff",
    "Brand Value vs Wins", "Team Success vs Growth", "Opponent Win % (Filtered)",
    "Opponent Win % (All Teams)", "Total Wins by Team", "Seasonal Win % by Team",
    "Team Retention Treemap", "Team vs Opponent Sunburst", "Playoff Win % Lollipop",
    "Wins by City (Geo)", "Rivalries Chord Diagram"
])

# === TAB 1: Top 10 Consistent Batters ===
with tab1:
    st.subheader("🎯 Top 10 Consistent Run-Scorers Across Seasons")
    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')
    merged_df = pd.merge(history_df, matches_df[['id', 'date']], left_on='match_id', right_on='id', how='left')
    merged_df['Year'] = merged_df['date'].dt.year
    runs_per_season = merged_df.groupby(['Year', 'batter'])['batsman_runs'].sum().reset_index()
    top_10_each_season = runs_per_season.sort_values(['Year', 'batsman_runs'], ascending=[True, False]).groupby('Year').head(10)
    consistency = top_10_each_season['batter'].value_counts().reset_index()
    consistency.columns = ['batter', 'seasons_in_top10']
    top_n = 10
    players = consistency.head(top_n)['batter'].tolist()
    values = consistency.head(top_n)['seasons_in_top10'].tolist()
    angles = np.linspace(0, 2 * np.pi, top_n, endpoint=False).tolist()
    bar_width = 2 * np.pi / top_n
    colors = plt.get_cmap('Set3').colors[:top_n]
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'polar': True})
    bars = ax.bar(angles, values, width=bar_width, color=colors, edgecolor='white')
    for angle, height in zip(angles, values):
        ax.text(angle, height / 2, str(height), ha='center', va='center', fontsize=12, fontweight='bold')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    fig.legend(bars, players, loc='center left', bbox_to_anchor=(1.05, 0.5), title="Player")
    ax.set_title("Top IPL Run-Scorers: Consistency in Top 10 Across Seasons", fontsize=16, pad=30)
    st.pyplot(fig)

# === TAB 2: All-Time Total Runs (Similar rose plot logic) ===
with tab2:
    st.subheader("🎯 Top IPL Run-Scorers: All-Time Total Runs")

    # Load data
    history_df = pd.read_csv("Ipl20.csv")
    matches_df = pd.read_csv("Updated_Matches.csv")

    # Clean and preprocess
    history_df.columns = history_df.columns.str.strip()
    matches_df.columns = matches_df.columns.str.strip()
    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')

    merged_df = pd.merge(history_df, matches_df[['id', 'date']], left_on='match_id', right_on='id', how='left')
    merged_df['Year'] = merged_df['date'].dt.year

    # Compute total runs per batter
    overall_runs = merged_df.groupby('batter')['batsman_runs'].sum().reset_index()
    top_scorers = overall_runs.sort_values(by='batsman_runs', ascending=False).head(10)

    top_n = 10
    players = top_scorers['batter'].tolist()
    values = top_scorers['batsman_runs'].tolist()
    angles = np.linspace(0, 2 * np.pi, top_n, endpoint=False).tolist()
    bar_width = 2 * np.pi / top_n
    colors = plt.get_cmap('Set3').colors[:top_n]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'polar': True})
    ax.set_facecolor('white')
    bars = ax.bar(angles, values, width=bar_width, color=colors, edgecolor='white', linewidth=1.5)

    for angle, height in zip(angles, values):
        ax.text(angle, height / 2, str(int(height)), ha='center', va='center', fontsize=12, fontweight='bold', color='black')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    fig.legend(bars, players, loc='center left', bbox_to_anchor=(1.05, 0.5), fontsize=11, title="Player")
    ax.set_title("Top IPL Run-Scorers: All-Time Total Runs", fontsize=16, fontweight='bold', pad=30)

    st.pyplot(fig)

with tab3:
    st.subheader("📊 IPL Title Impact: Bowlers vs Batters (Season-Wise Comparison)")

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Load and preprocess
    ipl_data = pd.read_csv("Ipl20.csv")
    matches_df = pd.read_csv("Updated_Matches.csv")

    ipl_data.columns = ipl_data.columns.str.strip()
    matches_df.columns = matches_df.columns.str.strip()

    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')
    matches_df['season_year'] = matches_df['date'].dt.year

    ipl_data = pd.merge(ipl_data, matches_df[['id', 'season_year']], left_on='match_id', right_on='id', how='left')

    # Filter valid wickets (exclude run outs)
    valid_wickets = ipl_data[
        (ipl_data['is_wicket'] == 1) &
        (~ipl_data['dismissal_kind'].str.lower().fillna('').str.contains('run out'))
    ]

    # Bowler data
    bowler_season_team = valid_wickets.groupby(['bowler', 'season_year', 'bowling_team'])['is_wicket']                                       .count().reset_index(name='wickets')

    # Batter data
    batter_season_team = ipl_data.groupby(['batter', 'season_year', 'batting_team'])['batsman_runs']                                  .sum().reset_index(name='runs')

    # Add season winners
    season_winners = matches_df.sort_values('date').groupby('season_year').tail(1)[['season_year', 'winner']]
    season_winners = season_winners.rename(columns={'winner': 'season_winner'})

    bowler_season_team = bowler_season_team.merge(season_winners, on='season_year', how='left')
    batter_season_team = batter_season_team.merge(season_winners, on='season_year', how='left')

    bowler_season_team['won_title'] = bowler_season_team['bowling_team'] == bowler_season_team['season_winner']
    batter_season_team['won_title'] = batter_season_team['batting_team'] == batter_season_team['season_winner']

    bowler_season_team = bowler_season_team.rename(columns={'season_year': 'season'})
    batter_season_team = batter_season_team.rename(columns={'season_year': 'season'})
    batter_season_team['runs'] = batter_season_team['runs'].clip(upper=700)

    bowler_season_team['season'] = bowler_season_team['season'].astype(str)
    batter_season_team['season'] = batter_season_team['season'].astype(str)

    winners_bowl = bowler_season_team[bowler_season_team['won_title']]
    others_bowl = bowler_season_team[~bowler_season_team['won_title']]
    winners_bat = batter_season_team[batter_season_team['won_title']]
    others_bat = batter_season_team[~batter_season_team['won_title']]

    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=("🎯 Wickets per Bowler (with Title Impact)", "💥 Runs per Batter (with Title Impact)")
    )

    for season in sorted(bowler_season_team['season'].unique()):
        sdata = bowler_season_team[bowler_season_team['season'] == season]
        fig.add_trace(go.Violin(
            x=sdata['season'], y=sdata['wickets'],
            box_visible=True, meanline_visible=True,
            line_color='rgba(0,0,0,0.3)', fillcolor='rgba(100,149,237,0.4)',
            opacity=0.7, scalemode='count', showlegend=False
        ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=winners_bowl['season'], y=winners_bowl['wickets'],
        mode='markers', name='Won Title',
        marker=dict(color='gold', size=5, line=dict(color='black', width=0.5)),
        text=[f"{r.bowler}<br>{r.bowling_team}<br>{r.wickets} wickets" for _, r in winners_bowl.iterrows()],
        hoverinfo='text'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=others_bowl['season'], y=others_bowl['wickets'],
        mode='markers', name='Did Not Win',
        marker=dict(color='gray', size=5, opacity=0.7),
        text=[f"{r.bowler}<br>{r.bowling_team}<br>{r.wickets} wickets" for _, r in others_bowl.iterrows()],
        hoverinfo='text'
    ), row=1, col=1)

    for season in sorted(batter_season_team['season'].unique()):
        sdata = batter_season_team[batter_season_team['season'] == season]
        fig.add_trace(go.Violin(
            x=sdata['season'], y=sdata['runs'],
            box_visible=True, meanline_visible=True,
            line_color='rgba(0,0,0,0.3)', fillcolor='rgba(72,201,176,0.4)',
            opacity=0.7, scalemode='width', showlegend=False
        ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=winners_bat['season'], y=winners_bat['runs'],
        mode='markers', name='Won Title',
        marker=dict(color='gold', size=5, line=dict(color='black', width=0.5)),
        text=[f"{r.batter}<br>{r.batting_team}<br>{r.runs} runs" for _, r in winners_bat.iterrows()],
        hoverinfo='text', showlegend=False
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=others_bat['season'], y=others_bat['runs'],
        mode='markers', name='Did Not Win',
        marker=dict(color='gray', size=5, opacity=0.7),
        text=[f"{r.batter}<br>{r.batting_team}<br>{r.runs} runs" for _, r in others_bat.iterrows()],
        hoverinfo='text', showlegend=False
    ), row=2, col=1)

    fig.update_layout(
        height=1000,
        width=1200,
        title="📊 IPL Title Impact: Bowlers vs Batters (Season-Wise Comparison)",
        font=dict(size=14),
        violinmode='overlay',
        template='plotly_white',
        legend=dict(
            title='Legend',
            orientation='h',
            x=0.35,
            y=0.52,
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='black',
            borderwidth=1
        )
    )
    fig.update_yaxes(title_text="Wickets", row=1, col=1)
    fig.update_yaxes(title_text="Runs (clipped at 700)", row=2, col=1)
    fig.update_xaxes(title_text="Season", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)
with tab4:
    st.subheader("🏏 Team Performance: League vs. Playoff (Box Plot)")

    import plotly.express as px

    # Load and clean
    matches_df = pd.read_csv("Updated_Matches.csv")
    history_df = pd.read_csv("Ipl20.csv")
    matches_df.columns = matches_df.columns.str.strip()
    history_df.columns = history_df.columns.str.strip()

    # Standardize team names
    team_name_mapping = {
        'Kings XI Punjab': 'Punjab Kings',
        'Delhi Daredevils': 'Delhi Capitals',
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Rising Pune Supergiant': 'Rising Pune Supergiants',
        'Rising Pune Supergiants': 'Rising Pune Supergiants'
    }
    history_df['batting_team'] = history_df['batting_team'].str.strip().replace(team_name_mapping)

    # Mark League vs Playoff stage
    matches_df['Stage'] = matches_df['match_type'].apply(
        lambda x: 'League' if str(x).strip().lower() == 'league' else 'Playoff'
    )

    # Sum runs per team per match
    team_runs = history_df.groupby(['match_id', 'batting_team'])['batsman_runs'].sum().reset_index()
    team_runs = team_runs.rename(columns={'batting_team': 'Team', 'batsman_runs': 'Runs'})

    # Merge stage info
    merged_df = pd.merge(team_runs, matches_df[['id', 'Stage']], left_on='match_id', right_on='id')

    # Plot box plot
    fig = px.box(
        merged_df,
        x="Team",
        y="Runs",
        color="Stage",
        title="🏏 Team Performance: League vs. Playoff (Box Plot)",
        labels={"Runs": "Total Runs per Match", "Team": "IPL Team"},
        template="plotly_white",
        height=600
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
with tab5:
    st.subheader("📈 Legacy IPL Teams: Brand Value vs Year (Dot Size = Wins)")

    import plotly.graph_objects as go

    # Load data
    matches_df = pd.read_csv("Updated_Matches.csv")
    brand_long_df = pd.read_csv("cleaned_brand_value_long_format.csv")

    # Clean columns and extract year
    matches_df.columns = matches_df.columns.str.strip()
    matches_df['winner'] = matches_df['winner'].str.strip()
    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')
    matches_df['Year'] = matches_df['date'].dt.year

    # Compute wins
    valid_matches = matches_df.dropna(subset=['winner'])
    wins = valid_matches.groupby(['winner', 'Year']).size().reset_index(name='Wins')
    wins = wins.rename(columns={'winner': 'Team'})

    # Merge with brand value
    merged = pd.merge(wins, brand_long_df, on=['Team', 'Year'])

    # Filter legacy teams (at least 5 years)
    legacy_teams = merged['Team'].value_counts()[merged['Team'].value_counts() >= 5].index
    legacy_teams = legacy_teams.difference(['Gujarat Titans'])  # Exclude GT
    legacy_df = merged[merged['Team'].isin(legacy_teams)].copy()

    # Create chart
    fig = go.Figure()
    for team in legacy_df['Team'].unique():
        team_data = legacy_df[legacy_df['Team'] == team].copy()
        win_sizes = team_data['Wins'] * 1.5  # Scale size

        fig.add_trace(go.Scatter(
            x=team_data['Year'],
            y=team_data['BrandValue'],
            mode='lines+markers',
            name=team,
            marker=dict(
                size=win_sizes.tolist(),
                sizemode='diameter',
                sizeref=2.5,
                line=dict(width=1, color='black')
            ),
            text=team_data['Team'],
            customdata=team_data['Wins'],
            hovertemplate="<b>%{text}</b><br>Year: %{x}<br>Brand Value: %{y}M<br>Wins: %{customdata}<br><i>(Team: %{text})</i>"
        ))

    fig.update_layout(
        title="📈 Legacy IPL Teams: Brand Value vs Year (Dot Size = Wins)",
        xaxis_title="Year",
        yaxis_title="Brand Value (in million USD)",
        template="plotly_white",
        width=1200,
        height=700,
        font=dict(family="Helvetica", size=14),
        xaxis=dict(tickmode='linear', dtick=1),
        legend=dict(bordercolor="gray", borderwidth=1)
    )

    st.plotly_chart(fig, use_container_width=True)
with tab6:
    st.subheader("📊 Bubble Chart: Team Success (Wins) vs Popularity Growth (Brand Value)")

    import plotly.express as px

    # Load data
    matches_df = pd.read_csv("Updated_Matches.csv")
    brand_long_df = pd.read_csv("cleaned_brand_value_long_format.csv")

    # Clean columns
    matches_df.columns = matches_df.columns.str.strip()
    matches_df['winner'] = matches_df['winner'].str.strip()

    # Total wins per team
    total_wins = matches_df['winner'].value_counts().reset_index()
    total_wins.columns = ['Team', 'TotalWins']

    # Prepare brand data
    brand_df = brand_long_df.copy().sort_values(by=['Team', 'Year'])

    # Compute brand value growth
    growth_df = brand_df.groupby('Team').agg(
        FirstYearValue=('BrandValue', 'first'),
        LastYearValue=('BrandValue', 'last')
    ).reset_index()
    growth_df['GrowthPercent'] = ((growth_df['LastYearValue'] - growth_df['FirstYearValue']) / growth_df['FirstYearValue']) * 100
    growth_df = growth_df[growth_df['FirstYearValue'] > 0]

    # Merge
    bubble_df = pd.merge(total_wins, growth_df, on='Team', how='inner')

    # Bubble chart
    fig = px.scatter(
        bubble_df,
        x="TotalWins",
        y="LastYearValue",
        size="GrowthPercent",
        color="Team",
        hover_data=["Team", "TotalWins", "GrowthPercent", "LastYearValue"],
        title="📊 Bubble Chart: Team Success (Wins) vs Popularity Growth (Brand Value)",
        size_max=40,
        template="plotly_white"
    )

    fig.update_layout(
        xaxis_title="Total Wins (2008–2024)",
        yaxis_title="Latest Brand Value (in million USD)",
        font=dict(family="Helvetica", size=14),
        legend=dict(bordercolor="gray", borderwidth=1),
        width=1100,
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)
with tab7:
    st.subheader("🔥 IPL Team vs Opponent Win % Heatmap")

    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np

    # Load data
    matches = pd.read_csv("Updated_Matches.csv")
    matches.columns = matches.columns.str.strip()

    # Standardize team names
    team_name_corrections = {
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Delhi Daredevils': 'Delhi Capitals',
        'Rising Pune Supergiants': 'Rising Pune Supergiant',
        'Rising Pune Supergiant': 'Rising Pune Supergiant'
    }
    for col in ['team1', 'team2', 'winner']:
        matches[col] = matches[col].replace(team_name_corrections)

    matches = matches[matches['winner'].notna()]

    # Create win/loss records
    data = []
    for idx, row in matches.iterrows():
        team1 = row['team1']
        team2 = row['team2']
        winner = row['winner']
        if team1 != team2:
            data.append({'team': team1, 'opponent': team2, 'won': int(winner == team1)})
            data.append({'team': team2, 'opponent': team1, 'won': int(winner == team2)})

    df = pd.DataFrame(data)

    # Group and calculate win %
    team_vs_opponent = df.groupby(['team', 'opponent']).agg(
        matches_played=('won', 'count'),
        matches_won=('won', 'sum')
    ).reset_index()
    team_vs_opponent['win_percentage'] = (team_vs_opponent['matches_won'] / team_vs_opponent['matches_played']) * 100

    heatmap_data = team_vs_opponent.pivot(index='team', columns='opponent', values='win_percentage')

    # Mask diagonal and defunct teams
    mask = heatmap_data.copy()
    for team in heatmap_data.index:
        if team in heatmap_data.columns:
            mask.loc[team, team] = np.nan
    defunct_teams = ['Deccan Chargers', 'Kochi Tuskers Kerala', 'Pune Warriors', 'Rising Pune Supergiant', 'Gujarat Lions']
    mask = mask.drop(index=defunct_teams, errors='ignore')
    mask = mask.drop(columns=defunct_teams, errors='ignore')

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        mask, 
        annot=True, 
        fmt=".1f", 
        cmap='coolwarm', 
        linewidths=1.0,
        linecolor='black',
        cbar_kws={'label': 'Win %'}, 
        mask=mask.isnull(),
        ax=ax
    )
    ax.set_title('IPL Team vs Opponent Win % Heatmap (Cleaned with Borders)', fontsize=20, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    st.pyplot(fig)
with tab8:
    st.subheader("📊 IPL Team vs Opponent Win % (All Teams, Standardized)")

    import seaborn as sns
    import matplotlib.pyplot as plt

    # Load data
    matches = pd.read_csv("Updated_Matches.csv")
    matches.columns = matches.columns.str.strip()

    # Standardize team names
    team_name_corrections = {
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Delhi Daredevils': 'Delhi Capitals',
        'Rising Pune Supergiants': 'Rising Pune Supergiant',
        'Rising Pune Supergiant': 'Rising Pune Supergiant'
    }
    for col in ['team1', 'team2', 'winner']:
        matches[col] = matches[col].replace(team_name_corrections)

    matches = matches[matches['winner'].notna()]

    # Generate match records
    data = []
    for idx, row in matches.iterrows():
        t1, t2, w = row['team1'], row['team2'], row['winner']
        if t1 != t2:
            data.append({'team': t1, 'opponent': t2, 'won': int(w == t1)})
            data.append({'team': t2, 'opponent': t1, 'won': int(w == t2)})

    df = pd.DataFrame(data)

    # Aggregate win % per opponent
    team_vs_opponent = df.groupby(['team', 'opponent']).agg(
        matches_played=('won', 'count'),
        matches_won=('won', 'sum')
    ).reset_index()
    team_vs_opponent['win_percentage'] = (team_vs_opponent['matches_won'] / team_vs_opponent['matches_played']) * 100
    heatmap_data = team_vs_opponent.pivot(index='team', columns='opponent', values='win_percentage')

    # Plot heatmap with borders
    fig, ax = plt.subplots(figsize=(16, 12))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".1f",
        cmap='coolwarm',
        linewidths=1.0,
        linecolor='black',
        cbar_kws={'label': 'Win %'},
        ax=ax
    )
    ax.set_title('IPL Team vs Opponent Win Percentage Heatmap (All Names Standardized with Borders)', fontsize=20, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    st.pyplot(fig)
with tab9:
    st.subheader("🏏 Total Wins by IPL Teams (2008–2024)")

    import plotly.express as px

    # Load match data
    matches = pd.read_csv("Updated_Matches.csv")
    matches.columns = matches.columns.str.strip()

    # Standardize names
    team_name_corrections = {
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Delhi Daredevils': 'Delhi Capitals',
        'Rising Pune Supergiants': 'Rising Pune Supergiant',
        'Rising Pune Supergiant': 'Rising Pune Supergiant'
    }
    for col in ['team1', 'team2', 'winner']:
        matches[col] = matches[col].replace(team_name_corrections)

    # Wins
    wins = matches['winner'].value_counts().reset_index()
    wins.columns = ['team', 'wins']

    # Matches played
    team1_counts = matches['team1'].value_counts()
    team2_counts = matches['team2'].value_counts()
    matches_played = (team1_counts + team2_counts).reset_index()
    matches_played.columns = ['team', 'matches_played']

    # Merge and calculate
    performance = pd.merge(wins, matches_played, on='team', how='outer').fillna(0)
    performance['win_percentage'] = (performance['wins'] / performance['matches_played']) * 100
    performance = performance.sort_values(by="wins", ascending=True)

    # Highlight top team
    highlight_team = performance.iloc[-1]['team']
    performance['color'] = performance['team'].apply(
        lambda x: '#d94f45' if x == highlight_team else 'lightgray'
    )

    # Plot
    fig = px.bar(
        performance,
        x='wins',
        y='team',
        orientation='h',
        title='🏏 Total Wins by IPL Teams (2008–2024)',
    )
    fig.update_traces(marker_color=performance['color'])
    fig.update_layout(
        height=700, width=900,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=14),
        title_font=dict(size=22),
        xaxis=dict(title='Wins', showgrid=False),
        yaxis=dict(title='', showgrid=False),
        margin=dict(l=150, r=40, t=60, b=40),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
with tab10:
    st.subheader("📊 IPL Win % by Season (Teams with >10 Seasons)")

    import seaborn as sns
    import matplotlib.pyplot as plt

    # Load data
    matches_df = pd.read_csv("Updated_Matches.csv")
    matches_df.columns = matches_df.columns.str.strip()

    # Long format for matches
    long_df = pd.melt(
        matches_df,
        id_vars=["season", "winner"],
        value_vars=["team1", "team2"],
        var_name="role",
        value_name="team"
    )

    matches_played = long_df.groupby(['season', 'team']).size().reset_index(name='Matches_Played')
    wins = matches_df.groupby(['season', 'winner']).size().reset_index(name='Wins')
    wins = wins.rename(columns={'winner': 'team'})

    # Merge win data
    team_stats = pd.merge(matches_played, wins, on=['season', 'team'], how='left').fillna(0)
    team_stats['Win_Percent'] = (team_stats['Wins'] / team_stats['Matches_Played']) * 100
    team_stats['season'] = team_stats['season'].astype(str).str.strip()

    # Filter for teams with >10 seasons
    season_counts = team_stats.groupby('team')['season'].nunique().reset_index(name='Season_Count')
    long_term_teams = season_counts[season_counts['Season_Count'] > 10]['team'].tolist()
    filtered_stats = team_stats[team_stats['team'].isin(long_term_teams)]

    # Facet grid plot
    sns.set(style="whitegrid", palette="muted", font_scale=1.2)
    g = sns.FacetGrid(filtered_stats, col="team", col_wrap=3, height=5, sharey=False)
    g.map_dataframe(sns.barplot, x="season", y="Win_Percent", palette="Blues", order=sorted(filtered_stats['season'].unique()))
    g.set_titles("{col_name}", size=14)
    g.set_axis_labels("Season", "Win %", size=12)
    g.set_xticklabels(rotation=45, size=10)
    g.set_yticklabels(size=10)

    for ax in g.axes.flatten():
        ax.grid(True, linestyle='--', alpha=0.5)

    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("📊 IPL Win % by Season (Teams with >10 Seasons)", fontsize=18, weight='bold')
    plt.tight_layout()

    st.pyplot(g.fig)
with tab11:
    st.subheader("📦 Treemap: Teams and Players Retained 5+ Seasons (Sorted by Team Strength)")

    import plotly.express as px

    # Load data
    matches_df = pd.read_csv("Updated_Matches.csv")
    history_df = pd.read_csv("Ipl20.csv")
    matches_df.columns = matches_df.columns.str.strip()
    history_df.columns = history_df.columns.str.strip()

    # Standardize team names
    team_name_mapping = {
        'Kings XI Punjab': 'Punjab Kings',
        'Delhi Daredevils': 'Delhi Capitals',
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Rising Pune Supergiant': 'Rising Pune Supergiants',
        'Rising Pune Supergiants': 'Rising Pune Supergiants'
    }
    history_df['batting_team'] = history_df['batting_team'].str.strip().replace(team_name_mapping)

    # Merge season info
    history_with_season = pd.merge(
        history_df,
        matches_df[['id', 'season']],
        left_on='match_id',
        right_on='id',
        how='left'
    )
    history_with_season = history_with_season[['season', 'batting_team', 'batter']].dropna()
    history_with_season['season'] = history_with_season['season'].astype(str).str.strip()

    # Group players by team and seasons played
    player_season_map = history_with_season.drop_duplicates().groupby(['batting_team', 'batter'])['season']                                            .apply(set).reset_index()
    player_season_map['num_seasons'] = player_season_map['season'].apply(len)

    # Filter for 5+ season players
    retained_5yr_plus = player_season_map[player_season_map['num_seasons'] >= 5]
    team_retention_count = retained_5yr_plus.groupby('batting_team').size().reset_index(name='Players_5yr+')

    treemap_data = retained_5yr_plus.merge(team_retention_count, on='batting_team')
    treemap_data.columns = ['Team', 'Player', 'Seasons', 'Num_Seasons', 'Team_Player_Count']
    treemap_data['Player_Label'] = treemap_data['Player'] + ' (' + treemap_data['Num_Seasons'].astype(str) + ' yrs)'
    treemap_data = treemap_data.sort_values(by=['Team_Player_Count', 'Num_Seasons'], ascending=[False, False])

    # Create treemap
    fig = px.treemap(
        treemap_data,
        path=['Team', 'Player_Label'],
        values='Num_Seasons',
        color='Team_Player_Count',
        color_continuous_scale='Tealgrn',
        title='📦 Treemap: Teams and Players Retained 5+ Seasons (Sorted by Team Strength)',
        template='plotly_white'
    )
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig, use_container_width=True)
with tab12:
    st.subheader("🏏 IPL: Team vs Opponent Wins (Sunburst Chart)")

    import plotly.express as px

    # Load and clean match data
    matches = pd.read_csv("Updated_Matches.csv")
    matches_cleaned = matches.dropna(subset=['winner'])

    def get_opponent(row):
        if row['team1'] == row['winner']:
            return row['team2']
        elif row['team2'] == row['winner']:
            return row['team1']
        else:
            return None

    matches_cleaned['opponent'] = matches_cleaned.apply(get_opponent, axis=1)

    # Group wins by team and opponent
    team_vs_opponent = matches_cleaned.groupby(['winner', 'opponent']).size().reset_index(name='wins')

    # Create sunburst
    fig = px.sunburst(
        team_vs_opponent,
        path=['winner', 'opponent'],
        values='wins',
        color='winner',
        title='🏏 IPL: Team vs Opponent Wins (Sunburst Chart)',
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)
with tab13:
    st.subheader("🎯 IPL Playoffs: Win Percentage by Team (Lollipop Chart)")

    import matplotlib.pyplot as plt

    # Load data
    matches_df = pd.read_csv("Updated_Matches.csv")
    matches_df['Stage'] = matches_df['match_type'].apply(
        lambda x: 'League' if str(x).strip().lower() == 'league' else 'Playoff'
    )

    playoff_matches = matches_df[matches_df['Stage'] == 'Playoff']

    # Wins
    wins_df = playoff_matches['winner'].value_counts().reset_index()
    wins_df.columns = ['Team', 'Wins']

    # Appearances
    appearances_df = pd.concat([
        playoff_matches[['team1']].rename(columns={'team1': 'Team'}),
        playoff_matches[['team2']].rename(columns={'team2': 'Team'})
    ])
    appearances_df = appearances_df['Team'].value_counts().reset_index()
    appearances_df.columns = ['Team', 'Appearances']

    # Win %
    playoff_stats = pd.merge(appearances_df, wins_df, on='Team', how='left').fillna(0)
    playoff_stats['Win_Percent'] = (playoff_stats['Wins'] / playoff_stats['Appearances']) * 100
    playoff_stats = playoff_stats[playoff_stats['Appearances'] >= 3]
    playoff_stats_sorted = playoff_stats.sort_values(by='Win_Percent', ascending=True)

    # Lollipop plot
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.hlines(y=playoff_stats_sorted['Team'], xmin=0, xmax=playoff_stats_sorted['Win_Percent'], color='skyblue')
    ax.plot(playoff_stats_sorted['Win_Percent'], playoff_stats_sorted['Team'], "o", markersize=8, color='blue')

    ax.set_title("IPL Playoffs: Win Percentage by Team (Lollipop Chart)", fontsize=16)
    ax.set_xlabel("Win Percentage", fontsize=12)
    ax.set_xlim(0, 100)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig)
with tab14:
    st.subheader("🗺️ IPL Team Wins Across Indian Cities (Clustered Map)")

    import folium
    from folium.plugins import MarkerCluster
    from streamlit_folium import st_folium
    import random

    # Reload IPL data
    matches = pd.read_csv("Updated_Matches.csv")

    city_coords = {
        'Mumbai': (19.0760, 72.8777),
        'Chennai': (13.0827, 80.2707),
        'Delhi': (28.6139, 77.2090),
        'Kolkata': (22.5726, 88.3639),
        'Bangalore': (12.9716, 77.5946),
        'Hyderabad': (17.3850, 78.4867),
        'Ahmedabad': (23.0225, 72.5714),
        'Jaipur': (26.9124, 75.7873),
        'Mohali': (30.7046, 76.7179),
        'Pune': (18.5204, 73.8567),
        'Raipur': (21.2514, 81.6296),
        'Ranchi': (23.3441, 85.3096),
        'Dharamsala': (32.2190, 76.3234),
        'Visakhapatnam': (17.6868, 83.2185),
        'Cuttack': (20.4625, 85.8828),
        'Indore': (22.7196, 75.8577),
        'Nagpur': (21.1458, 79.0882),
    }

    matches = matches[matches['city'].isin(city_coords.keys())]
    team_city_wins = matches.dropna(subset=['winner']).groupby(['city', 'winner']).size().reset_index(name='wins')
    team_city_wins['lat'] = team_city_wins['city'].map(lambda x: city_coords[x][0])
    team_city_wins['lon'] = team_city_wins['city'].map(lambda x: city_coords[x][1])

    teams = team_city_wins['winner'].unique()
    team_colors = {team: f"#{random.randint(0, 0xFFFFFF):06x}" for team in teams}

    india_map = folium.Map(location=[22.9734, 78.6569], zoom_start=5.1, tiles='CartoDB positron')
    marker_cluster = MarkerCluster().add_to(india_map)

    for _, row in team_city_wins.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=max(3, row['wins'] / 2),
            color=team_colors.get(row['winner'], 'blue'),
            fill=True,
            fill_opacity=0.6,
            popup=f"{row['winner']} - {row['city']}: {row['wins']} wins"
        ).add_to(marker_cluster)

    # Render map in Streamlit
    st_folium(india_map, width=1000, height=600)
with tab15:
    st.subheader("🕸️ IPL Matchups: Rivalries Highlighted by Team Color (Chord Diagram)")

    import pandas as pd
    import holoviews as hv
    from holoviews import opts, dim
    from bokeh.palettes import Category20
    from bokeh.plotting import show
    from streamlit_bokeh_events import streamlit_bokeh_events

    hv.extension('bokeh')

    matches = pd.read_csv("Updated_Matches.csv")
    matches.columns = matches.columns.str.strip()
    matches = matches[matches['winner'].notna()]
    matches['date'] = pd.to_datetime(matches['date'], errors='coerce')
    matches['Year'] = matches['date'].dt.year

    team_name_corrections = {
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Delhi Daredevils': 'Delhi Capitals',
        'Rising Pune Supergiants': 'Rising Pune Supergiant',
    }
    abbrev_map = {
        'Mumbai Indians': 'MI', 'Chennai Super Kings': 'CSK',
        'Kolkata Knight Riders': 'KKR', 'Royal Challengers Bangalore': 'RCB',
        'Delhi Capitals': 'DC', 'Sunrisers Hyderabad': 'SRH',
        'Punjab Kings': 'PBKS', 'Rajasthan Royals': 'RR',
        'Deccan Chargers': 'DCG'
    }
    for col in ['team1', 'team2', 'winner']:
        matches[col] = matches[col].replace(team_name_corrections).replace(abbrev_map)

    team_years = pd.concat([
        matches[['team1', 'Year']].rename(columns={'team1': 'Team'}),
        matches[['team2', 'Year']].rename(columns={'team2': 'Team'})
    ])
    long_term_teams = team_years.drop_duplicates().groupby('Team').size()
    long_term_teams = long_term_teams[long_term_teams >= 10].index.tolist()

    filtered_matches = matches[
        matches['team1'].isin(long_term_teams) & matches['team2'].isin(long_term_teams)
    ]

    all_rivalries = []
    for _, row in filtered_matches.iterrows():
        t1, t2 = sorted([row['team1'], row['team2']])
        winner = row['winner']
        all_rivalries.append((t1, t2, winner))

    rivalry_df = pd.DataFrame(all_rivalries, columns=['teamA', 'teamB', 'winner'])
    match_counts = rivalry_df.groupby(['teamA', 'teamB']).size().reset_index(name='total_matches')
    wins_A = rivalry_df[rivalry_df['winner'] == rivalry_df['teamA']].groupby(['teamA', 'teamB']).size().reset_index(name='winsA')
    wins_B = rivalry_df[rivalry_df['winner'] == rivalry_df['teamB']].groupby(['teamA', 'teamB']).size().reset_index(name='winsB')
    merged = match_counts.merge(wins_A, on=['teamA', 'teamB'], how='left')                          .merge(wins_B, on=['teamA', 'teamB'], how='left')
    merged['winsA'] = merged['winsA'].fillna(0).astype(int)
    merged['winsB'] = merged['winsB'].fillna(0).astype(int)

    def get_direction(row):
        if row['winsA'] >= row['winsB']:
            return pd.Series([row['teamA'], row['teamB'], row['winsA'], row['winsB']], index=['source', 'target', 'value', 'opp_value'])
        else:
            return pd.Series([row['teamB'], row['teamA'], row['winsB'], row['winsA']], index=['source', 'target', 'value', 'opp_value'])

    final_df = merged.copy()
    final_df[['source', 'target', 'value', 'opp_value']] = final_df.apply(get_direction, axis=1)
    final_df['win_diff'] = final_df['value'] - final_df['opp_value']

    teams = sorted(set(final_df['source']).union(set(final_df['target'])))
    nodes = pd.DataFrame({'name': teams})
    available_colors = [c for c in Category20[20] if 'green' not in c.lower()]
    while len(available_colors) < len(nodes):
        available_colors *= 2
    nodes['color'] = available_colors[:len(nodes)]
    team_color_map = nodes.set_index('name')['color'].to_dict()

    final_df['is_rivalry'] = ((final_df['value'] >= 15) & (final_df['win_diff'] >= 5)) | (final_df['total_matches'] > 35)
    final_df['edge_color'] = final_df.apply(lambda row: team_color_map.get(row['source'], 'gray') if row['is_rivalry'] else 'green', axis=1)
    final_df['label'] = final_df.apply(lambda row: f"{row['source']} → {row['target']}: {row['value']} wins", axis=1)

    chord = hv.Chord((final_df.drop(columns=['is_rivalry']), hv.Dataset(nodes, 'name'))).opts(
        opts.Chord(
            width=850, height=850,
            labels='name',
            node_color='name',
            cmap=team_color_map,
            edge_color=dim('edge_color'),
            edge_line_width=dim('value') * 0.2,
            node_size=30,
            node_line_width=2,
            node_line_color='black',
            label_text_font_size='11pt',
            label_text_color='black',
            title="🏏 IPL Matchups: All Shown, Rivalries Highlighted by Team Color",
            tools=['hover'],
            inspection_policy='edges'
        )
    )

    # Render it in Streamlit
    from bokeh.embed import components
    from streamlit.components.v1 import html

  # Properly indented inside tab15
st.bokeh_chart(hv.render(chord, backend='bokeh'), use_container_width=True)




# Save the file
file_path_full = Path("/mnt/data/streamlit_dashboard_full.py")
file_path_full.write_text(streamlit_dashboard_full)

file_path_full.name
