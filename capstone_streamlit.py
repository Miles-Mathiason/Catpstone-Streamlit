import streamlit as st

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM student.mm_artists;', ttl="10m")

# Making week:artist dict
ordered_weeks = tuple(set(df['week_']))

artist_dict = {}
for week in ordered_weeks:
  artists = []
  for i in range(0,len(df)):
    if df.loc[i]["week_"] == week:
      artists += [df.loc[i]["artist"]
  artist_dict[week] = artists

f'{artist_dict}'
      
    
  









st.title('UK Charts Artist Breakdown with Spotify Data')
st.dataframe(df)

