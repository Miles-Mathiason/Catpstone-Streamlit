import streamlit as st

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM student.mm_artists;', ttl="10m")












st.title('UK Charts Artist Breakdown with Spotify Data')
st.dataframe(df)


print([1,2,3])
