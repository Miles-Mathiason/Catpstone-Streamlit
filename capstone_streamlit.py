import streamlit as st
from requests import post, get
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv
import os
import base64
import pandas as pd
import json

load_dotenv()

database_config = {
        "database": os.environ.get('DATABASE'),
        "user": os.environ.get('USERNAME'),
        "password": os.environ.get('SQL_PASSWORD'),
        "host": os.environ.get('HOST'),
        "port": "5432"
    }
# conn = psycopg2.connect(**database_config)

def get_artists():
    '''Output is list of artists with a song in top 100 UK official charts'''
    
    url = 'https://www.officialcharts.com/charts/singles-chart/'
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    artists_list = [x.span.text for x in soup.findAll('a', class_="chart-artist text-lg inline-block")]
    artists_set = {}
    
    def flatten(xss):
        return [x for xs in xss for x in xs]
    
    artists_s0 = [x.replace("'","") for x in artists_list]
    artists_s1 = [x.split('/') for x in artists_s0] #List of Lists
    artists_s1_flat = flatten(artists_s1)
    artists_s2 = [x.split(' FT ') for x in artists_s1_flat] #List of Lists
    artists_s2_flat = flatten(artists_s2)
    artists_s3 = [x.split(' & ')+[x] for x in artists_s2_flat] #List of Lists
    artists_s3_flat = flatten(artists_s3)
    artists_set = set(artists_s3_flat)

    week = str(soup.find('p',class_="text-brand-cobalt text-sm sm:text-lg lg:text-xl basis-full font-bold !my-4").text)
    artists_with_week = [(artist,week) for artist in artists_set]
    return artists_with_week


def get_stored_artists():
    try:
        with psycopg2.connect(**database_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT *
                    FROM student.mm_artists
                """)

                result = cur.fetchall()
                return result
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
            return None


stored_artists = get_stored_artists()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

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
    artist_id = artist_search['id']
    try:
        url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country={market}'
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["tracks"]
        return json_result
    except:
        return {}

def get_related_artists(token, artist):
    artist_search = search_for_artist(token,artist)
    artist_id = artist_search['id']
    try:
        url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["artists"]
        return json_result
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


### Making artist+week lists
artists_set = {pair[0] for pair in stored_artists}
weeks_set = {pair[1] for pair in stored_artists}

artists = list(artists_set)
weeks = list(weeks_set)

ordered_weeks = tuple(pair[1] for pair in stored_artists)

### Making artist_data dataframe
#artist_data_df = pd.DataFrame()


#for artist in artists:
#    artist_json = get_artist_data(token,artist)
#    artist_df = pd.DataFrame(artist_json)
#    
#    artist_data_df = pd.concat([artist_data_df,artist_df])
#    artist_data_df = artist_data_df.reset_index(drop=True)
    
# Making week:artists dict
artist_dict = {}

for week in ordered_weeks:
    artists = []
    for pair in stored_artists:
        if pair[1] == week:
            artists += [pair[0]]
    artist_dict[week] = artists

    
##############################################################################
    
st.title('UK Charts Artist Breakdown with Spotify Data')

### Entering artist count

entering_artists = set(artist_dict[ordered_weeks[len(ordered_weeks)-1]])-set(artist_dict[ordered_weeks[len(ordered_weeks)-2]])
entering_artists_count = len(entering_artists)


### Defending artists count

defending_artists = set(artist_dict[ordered_weeks[len(ordered_weeks)-1]]) - entering_artists
defending_artists_count = len(defending_artists)


### Most common genre this week

genre_week_dict = {}

'''for week in ordered_weeks:
    genres = []
    for pair in stored_artists:
        if pair[1] == week:
            print(get_artist_data(token,pair[0]))
            genres += get_artist_data(token,pair[0])['genres']
            
    genre_counter = {key: genres.count(key) for key in set(genres)}
    genre_week_dict[week] = genres_counter'''

# max_genre_current = max(genre_week_dict[ordered_weeks[len(ordered_weeks)-1]])

### Most common genre last week

#max_genre_last = max(genre_week_dict[ordered_weeks[len(ordered_weeks)-2]])

### Preview display

col1, col2, col3, col4 = st.columns(4)
col1.metric("Number of Entering Artists", entering_artists_count, "0")
col2.metric("Number of Returning Artists", defending_artists_count, "0")
col3.metric("This Weeks Most Popular Genre", 'max_genre_current')
col4.metric("Last Weeks Most Popular Genre", 'max_genre_last')










### Genre chart
#genres = [genre_list for genre_list in artist_data_df['genres']]

#genre = st.selectbox(
#    'Pick a genre',
#    tuple(set(genres)))

#genre_week_data = []

#for week in weeks:
#    count = 0
    
    
#    genre_week_data+=[(week,count)]
    
