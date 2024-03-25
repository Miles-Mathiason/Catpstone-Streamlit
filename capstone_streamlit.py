import streamlit as st

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM student.mm_artists;', ttl="10m")

artist_list = df['artist']










st.title('UK Charts Artist Breakdown with Spotify Data')
st.dataframe(df)


f'{set(artist_list)}'
