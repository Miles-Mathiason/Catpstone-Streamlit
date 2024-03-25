import streamlit as st
from requests import post, get
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
conn = psycopg2.connect(**database_config)
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

f'{stored_artists}'
