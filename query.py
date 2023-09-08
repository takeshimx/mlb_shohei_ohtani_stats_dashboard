import streamlit as st
import psycopg2
import pandas as pd


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()


# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min (ttl: 600 seconds).
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        # retrieve column names
        col_names = [desc[0] for desc in cur.description]
        return cur.fetchall(), col_names


# create dataframe based on query
@st.cache_data(ttl=600)
def create_df(query):
    rows, col_names = run_query(query)
    # make it dataframe
    df = pd.DataFrame(rows, columns=col_names)
    return df
