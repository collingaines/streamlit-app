import streamlit as st
import pandas as pd
import numpy as np

#======================================================
#Setting the tab page title here: 
st.set_page_config(
    page_title="Pyramid Construction Analytics",
    page_icon="static/Main_Logo.jpg",
)

#======================================================
#Setting up our sidebar here:

# Add the custom logo to the sidebar
st.sidebar.image("static/Main_Logo.jpg", width=100)

# Add a title to the sidebar
st.sidebar.title("Pyramid Construction Technologies, LLC")

#======================================================
#Title code for this page goes here: 
st.title('Uber pickups in NYC')

#======================================================
#Here we will write our function to pull data from a preset database: 
DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


@st.cache_data #Let's go ahead and cache this data so that we don't have to wait for it to load every time that we interact with a component!
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


#======================================================
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache_data)")


#======================================================
#Adding a table that shows the raw data we pulled from our data source:
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)
