import streamlit as st

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM student.mm_artists;', ttl="10m")


ordered_weeks = tuple(set(df['week_']))










st.title('UK Charts Artist Breakdown with Spotify Data')
st.dataframe(df)

f'{ordered_weeks}'
