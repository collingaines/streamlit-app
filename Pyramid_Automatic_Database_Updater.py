#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #0 | IMPORTING OUR PYTHON LIBRARIES: 
#region CLICK HERE TO EXPAND SECTION

import streamlit as st
import pandas as pd
import numpy as np
from streamlit_cookies_manager import EncryptedCookieManager
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


#===============================================================================================================================================================
#Importing our libraries for our AgGrid table:
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

from openpyxl import Workbook
import io


#===============================================================================================================================================================
#Setting up our Supabase cloud database connection and logging in:

#=========================================================================
#Connecting to our Supabase cloud database:
from supabase import create_client, Client

def connect_to_supabase(url: str, key: str) -> Client:
    """
    Connects to the Supabase database.

    Parameters:
    - url: The Supabase project URL.
    - key: The Supabase API key.

    Returns:
    - A Supabase client instance.
    """
    supabase: Client = create_client(url, key)
    return supabase

# Example usage:
supabase_url = 'https://tfaydxxaqmroiroazueg.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRmYXlkeHhhcW1yb2lyb2F6dWVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3MDU4ODMsImV4cCI6MjA1NDI4MTg4M30.kBiVOV2loWuI_wnB3kmL0CE3jZOd6oOq02-bM3R8N-Y'
supabase_client = connect_to_supabase(supabase_url, supabase_key)

#=========================================================================
#Logging in to our Supabase cloud database:

#Function to log in a user
def login_user(email: str, password: str):
    response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
    return response

#Logging in to our Supabase databsae:
if __name__ == "__main__":
    # Log in as an authenticated user
    email = 'collingaines92@gmail.com'  # Replace with the user's email
    password = 'Cgained41$'   # Replace with the user's password
    login_response = login_user(email, password)


#=========================================================================
#Writing some functions to use to access/edit our database later in this script:

#Function for reading data from a specified database table. This will return a next list, similar to how you are used to dealing with Sqlite3:
def fetch_data_from_table(table_name: str):
    try:
        # Create a Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        all_data = []
        limit = 1000  # Set the limit for each request
        offset = 0    # Start with an offset of 0

        while True:
            # Fetch data from the specified table with pagination
            response = supabase.table(table_name).select("*").range(offset, offset + limit - 1).execute()

            # Print the raw response for debugging
            print("Raw response:", response)

            # Check if there was an error in the response
            # if response.error:
            #     print("Error fetching data:", response.error)
            #     return None

            # If no more data is returned, break the loop
            if not response.data:
                break

            # Append the fetched data to the all_data list
            all_data.extend(response.data)

            # Update the offset for the next request
            offset += limit

        # Convert the list of dictionaries to a nested list
        nested_list = [[value for value in row.values()] for row in all_data]

        return nested_list

    except Exception as e:
        print("An exception occurred:", str(e))
        return None


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #1 | UPDATING OUR DATABASE: 


import time

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes} minutes and {seconds:.2f} seconds"

startTime = format_time(time.time())




#========================================
#Inserting data into our "test" table:
def insert_data(data: dict):
    response = supabase_client.table('test').insert(data).execute()
    return response

data_to_insert = {
    'id':3,
    'test':str(startTime)
}

insert_response = insert_data(data_to_insert)