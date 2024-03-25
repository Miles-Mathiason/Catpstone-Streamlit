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

      
    
  

### Front-end
st.title('UK Charts Artist Breakdown with Spotify Data')

col1, col2, col3 = st.columns(3)
col1.metric("Recent Chart Period", ordered_weeks[len(ordered_weeks)-1])
col2.metric("Number of Entering Artists", f'#{entering_artists_count}')
col3.metric("Number of Remaining Artists", f'#{defending_artists_count}')



