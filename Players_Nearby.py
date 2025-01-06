import streamlit as st
# set streamlit to wide mode
st.set_page_config(layout="wide")

import pandas as pd

# Travel time in minutes from KT12 to each club, including league information
travel_time_data = [
    ("Hampton & Richmond Borough", 20, "NLS"),
    ("AFC Wimbledon", 30, "L2"),
    ("Woking FC", 30, "NL"),
    ("Sutton United", 35, "NL"),
    ("Dorking Wanderers", 35, "NLS"),
    ("Aldershot Town", 40, "NL"),
    ("Farnborough FC", 45, "NLS"),
    ("Slough Town", 50, "NLS"),
    ("Maidenhead United", 50, "NL"),
    ("Wealdstone FC", 50, "NL"),
    ("Boreham Wood FC", 55, "NLS"),
    ("Barnet FC", 60, "NL"),
    ("Hemel Hempstead Town", 60, "NLS"),
    ("St Albans City", 60, "NLS"),
    ("Bromley FC", 60, "L2"),
    ("Chesham United", 60, "NLS"),
    ("Welling United", 65, "NLS"),
    ("Ebbsfleet United", 65, "NL"),
    ("Tonbridge Angels", 70, "NLS"),
    ("Worthing FC", 70, "NLS"),
    ("Enfield Town", 70, "NLS"),
    ("Dagenham & Redbridge FC", 70, "NL"),
    ("Hornchurch FC", 75, "NLS"),
    ("Eastleigh FC", 75, "NL"),
    ("Aveley FC", 75, "NLS"),
    ("Oxford City", 75, "NLN"),
    ("Maidstone United", 75, "NLS"),
    ("Southend United", 80, "NL"),
    ("Chelmsford City", 80, "NLS"),
    ("FC Salisbury", 90, "NLS"),
    ("Braintree Town", 90, "NL"),
    ("Eastbourne Borough", 90, "NLS"),
]

# Shorten position descriptions
position_mapping = {
    "Goalkeeper": "GK",
    "Central Midfield": "CM",
    "Left-Back": "LB",
    "Centre-Back": "CB",
    "Right-Back": "RB",
    "Defensive Midfield": "DM",
    "Left Winger": "LW",
    "Centre-Forward": "CF",
    "Right Winger": "RW",
    "Left Midfield": "LM",
    "Attacking Midfield": "AM",
    "Right Midfield": "RM",
    "Second Striker": "SS",
    "Unknown": "Unknown"  # Keeping "Unknown" unchanged
}

# Function to update position descriptions
def update_positions(df):
    columns_to_update = ['main_pos', '2nd_pos', '3rd_pos']
    for col in columns_to_update:
        df[col] = df[col].map(position_mapping).fillna(df[col])  # Map positions and handle missing mappings
    return df

# Function to map transfermarkt positions
def add_position_coverage(df):
    # Initialize all cover columns to 0
    cover_columns = [
        'gk_cover', 'lb_cover', 'rb_cover', 'cb_cover', 
        '6_cover', '8_cover', 'lw_cover', 'rw_cover', '9_cover'
    ]
    for col in cover_columns:
        df[col] = 0
    
    # Apply rules for each cover column
    df['gk_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['GK']).any(axis=1).astype(int)
    df['lb_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['LB']).any(axis=1).astype(int)
    df['rb_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['RB']).any(axis=1).astype(int)
    df['cb_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['CB']).any(axis=1).astype(int)
    df['6_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['DM', 'CM']).any(axis=1).astype(int)
    df['8_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['AM', 'CM']).any(axis=1).astype(int)
    df['lw_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['LM', 'LW']).any(axis=1).astype(int)
    df['rw_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['RM', 'RW']).any(axis=1).astype(int)
    df['9_cover'] = df[['main_pos', '2nd_pos', '3rd_pos']].isin(['CF', 'SS']).any(axis=1).astype(int)
    
    return df

# Import CSV file of player data
df = pd.read_csv("https://raw.githubusercontent.com/fofota/player_minutes/main/players_minutes.csv")
df = df[df['club'] != "Dover Athletic"]

# Convert travel_time_data into a DataFrame for easy mapping
travel_df = pd.DataFrame(travel_time_data, columns=["club", "travel_time", "league"])
travel_df.index += 1

# Merge league and travel time data into the main DataFrame
df = df.merge(travel_df, on="club", how="left")

# Pre-processing of dataframe df
df.rename(columns={'transfer': 'recent_moves'}, inplace=True)
df = df[['name', 'club', 'minutes', 'position', 'age', 'height', 'foot', 'main_pos', '2nd_pos', '3rd_pos', 'travel_time', 'league', 'player_url', 'recent_moves']]
df = update_positions(df)
df = add_position_coverage(df)

# Remove visible index from dataframe df
df.set_index('name', inplace=True)

# Sort dataframe df by minutes
df.sort_values(by='minutes', ascending=False, inplace=True)

# Streamlit app
st.header("Players Nearby")
st.write("This table sets out all senior players in Step 2, Step 1 and League Two playing at clubs within 120 minutes drive of KT12")
with st.expander("Click here for more information on how this works"):
    st.write("There are 32 clubs within a 120 minute drive of KT12 that play at either the League 2, National League or National League South level. This includes Oxford City, who play in the National League North.")
    st.write("The table below includes all the players that transfermarkt records as being registered to those clubs as at 26 November 2024.")
    st.write("The table can be filtered using the controls in the sidebar. Here's an example: 'All players that have played between 1 and 500 minutes so far in the 2024/25 season, for clubs less than 30 minutes away, who can play at left back'.")
    st.write("Reload the page to restore the default filters.")
    st.write("This is the list of clubs that have been included in the analysis, sorted nearest to furthest. The travel time estimates are driving time, in minutes.")
    st.dataframe(travel_df)  # Display included clubs and leagues

# Sidebar filters
st.sidebar.header("Filters")

# Minutes played slider
minutes = st.sidebar.slider(
    "Minutes played so far this season", 
    min_value=0, 
    max_value=4000, 
    value=(1, 300)  # Default range
)

# Travel time slider
travel_time = st.sidebar.slider(
    "Drive time to current club (minutes)", 
    min_value=0, 
    max_value=120, 
    value=60  # Default value
)

# Add segmented control for position coverage with multiple selection
position_filter = st.sidebar.segmented_control(
    "Can play position:",
    options=[
        "GK", "LB", "RB", "CB", 
        "6", "8", "LW", "RW", "9"
    ],  # Options match the keys in position_mapping
    selection_mode="multi",
    default=None  # Default state with nothing selected
)

# Toggle for left-footed players
known_left_footed = st.sidebar.toggle("Known left-footed", value=False)

# Apply filters
df_filtered = df[(df['minutes'] >= minutes[0]) & (df['minutes'] <= minutes[1])]
df_filtered = df_filtered[df_filtered['travel_time'] <= travel_time]

# Apply position coverage filter
position_mapping = {
    "GK": "gk_cover",
    "LB": "lb_cover",
    "RB": "rb_cover",
    "CB": "cb_cover",
    "6": "6_cover",
    "8": "8_cover",
    "LW": "lw_cover",
    "RW": "rw_cover",
    "9": "9_cover",
}
# Handle multi-selection or no selection
if position_filter:
    selected_columns = [position_mapping[pos] for pos in position_filter if pos in position_mapping]
    if selected_columns:
        # Combine filters for multiple columns using logical OR
        df_filtered = df_filtered[df_filtered[selected_columns].any(axis=1)]

# Apply left-footed filter if toggle is active
if known_left_footed:
    df_filtered = df_filtered[df_filtered['foot'] == "left"]  # Ensure lowercase 'left'

# tidy df_filtered for display
df_filtered = df_filtered[['club', 'minutes', 'position', 'age', 'height', 'foot', 'main_pos', '2nd_pos', '3rd_pos', 'player_url', 'recent_moves', 'travel_time']]

st.sidebar.write("Height: 6ft0 = 1.83m, 6ft3 = 1.91m")
st.sidebar.write("Reload page to restore default filters (Cmd+R mac, Ctrl+R windows)")
# Update the table display to use the filtered dataframe
st.write(f"Number of players in table after filter: {df_filtered.shape[0]}")
# Display the filtered dataframe with clickable links for the "player_url" column
st.dataframe(
    df_filtered,
    column_config={
        "player_url": st.column_config.LinkColumn(
            label="Player Profile",  # Set the label for the column
            help="Click to view player profile",  # Tooltip for the column header
            display_text="transfermarkt"  # Text displayed for the link
        )
    },
)