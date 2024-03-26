import streamlit as st
import base64
from requests import post, get
import json

## Database
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

# Making week:artist_count dict
artist_count_dict = {}
for week in artist_dict:
    artist_count_dict[week] = len(artist_dict[week])

## Spotify Web API
client_id = st.secrets.credentials["CLIENT_ID"] 
client_secret = st.secrets.credentials["CLIENT_SECRET"]

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    try:
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"?q={artist_name}&type=artist&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            print('No artist with this name found...')
            return None

        return json_result[0]
    except:
        return {}

def get_top_tracks_by_artist(token, artist, market):
    artist_search = search_for_artist(token,artist)
    try:
        artist_id = artist_search['id']
        url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country={market}'
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["tracks"]
        return json_result
    except:
        return {}

def get_related_artists(token, artist):
    artist_search = search_for_artist(token,artist)
    #artist_id = artist_search['id']
    try:
        #url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'
        #headers = get_auth_header(token)
        #result = get(url, headers=headers)
        #json_result = json.loads(result.content)["artists"]
        return artist_search
    except:
        return {}

def get_artist_data(token, artist):
    artist_search = search_for_artist(token,artist)
    try:
        artist_id = artist_search['id']
        url = f'https://api.spotify.com/v1/artists/{artist_id}'
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result
    except:
        return {}
token = get_token()
url = "https://api.spotify.com/v1/search"
headers = get_auth_header(token)
artist_name = 'central cee'
query = f"?q={artist_name}&type=artist&limit=1"

query_url = url + query
result = get(query_url, headers=headers)

st.write(result)
### Front-end
st.title('UK Charts Artist Breakdown with Spotify Data')
c1 = st.container()
c1.metric("Recent Chart Period", ordered_weeks[len(ordered_weeks)-1])

col1, col2 = c1.columns(2)
col1.metric("Number of Entering Artists", f'#{entering_artists_count}')
col2.metric("Number of Remaining Artists", f'#{defending_artists_count}')

#st.bar_chart(artist_count_dict, width=1)

## Artist breakdown
c2 = st.container(border=True)
artists_set = set(df['artist'])
artist = c2.selectbox('Pick an Artist',tuple(artists_set))

artists_data = get_artist_data(token, artist)
followers = artists_data['followers']['total']
genres = artists_data['genres']
popularity = artists_data['popularity']
image_url = artists_data['images'][0]['url']
weeks = list(df.loc[df['artist'] == f'{artist}']['week_'])


col1, col2 = c2.columns(2)

col1.image(image_url, caption=artists_data['name'])
col2.metric('Spotify Followers',followers)
col2.header('Weeks in the Charts')
for week in weeks:
    col2.markdown("- " + week)

col1, col2 = c2.columns(2)

col1.header('Top Tracks')
count = 0
for json in get_top_tracks_by_artist(token, artist, 'GB'):
    count += 1
    col1.write(f'{count}. ' + json['name'])

col2.header('Genres')
for genre in genres:
    col2.markdown("- " + genre)


