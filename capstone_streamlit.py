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
            artists += [df.loc[i]["artist"]]
    artist_dict[week] = artists

# Entering artist count
entering_artists = set(artist_dict[ordered_weeks[len(ordered_weeks)-1]])-set(artist_dict[ordered_weeks[len(ordered_weeks)-2]])
entering_artists_count = len(entering_artists)

#Defending artist count
defending_artists = set(artist_dict[ordered_weeks[len(ordered_weeks)-1]]) - entering_artists
defending_artists_count = len(defending_artists)

#Making week:artist_count dict
artist_count_dict = {}
for week in artist_dict:
    artist_count_dict[week] = len(artist_dict[week])
    
  

### Front-end
st.title('UK Charts Artist Breakdown with Spotify Data')

st.metric("Recent Chart Period", ordered_weeks[len(ordered_weeks)-1])

col1, col2 = st.columns(2)
col1.metric("Number of Entering Artists", f'#{entering_artists_count}')
col2.metric("Number of Remaining Artists", f'#{defending_artists_count}')

st.bar_chart(artist_count_dict)


