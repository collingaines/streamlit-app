#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #0 | IMPORTING OUR PYTHON LIBRARIES: 
#region CLICK HERE TO EXPAND SECTION


#===============================================================================================================================================================
#Importing misc libraries
#region

print('IMPORTING PYTHON LIBRARIES...')

#Pandas and numpy will allow us to work with dataframes:
import pandas as pd
import numpy as np

#Datetime will allow us to pull current dates and work with dates/times
import datetime

#The time module will alow us to pause the script for set periods of time. This can be useful when some information takes a couple of seconds to update properly on the webpage
import time

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

#importing openpyxl for excel interaction, including modules that allow us to incorporate conditional formatting:
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Color, PatternFill, Font, Border
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule


import io

print('SUCCESS')

#endregion

#===============================================================================================================================================================
#Defining some misc functions for use later in script:
#region

print('DEFINING MISC FUNCTIONS FOR USE THROUGHOUT SCRIPT...')

#================================================================
#Defining our function to pull an address from GPS coordinates:
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_address_from_coordinates(latitude, longitude):
    """
    Takes GPS coordinates (latitude, longitude) and returns the corresponding address.
    """
    geolocator = Nominatim(user_agent="geo_lookup")
            
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        return location.address if location else "Address not found"
    except GeocoderTimedOut:
        return "Geocoder service timed out. Try again."

#================================================================
#Writing a function that will format our code block run time print outs in the console to be easier to read: 
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes} minutes and {seconds:.2f} seconds"

#Starting our time for our full script runtime console printout
fullScritStart_Time = time.time()


#================================================================
#Writing our function for pulling the lat/long range for each project
import math

def get_lat_lng_bounds(lat, lng, radius_miles=3):
    """Calculate the bounding box for a given latitude, longitude, and radius in miles."""
    miles_per_degree_lat = 69.0  # Approximate miles per degree of latitude
    delta_lat = radius_miles / miles_per_degree_lat

    miles_per_degree_lng = 69.0 * math.cos(math.radians(lat))  # Adjust for latitude
    delta_lng = radius_miles / miles_per_degree_lng

    return {
        "min_lat": lat - delta_lat,
        "max_lat": lat + delta_lat,
        "min_lng": lng - delta_lng,
        "max_lng": lng + delta_lng,
    }


#================================================================
#Writing a function that will return the most frequently occuring item an a list: 
from collections import Counter

def most_frequent(lst):
    """
    Returns the most frequently occurring value in the list.
    If there are multiple values with the same highest frequency, returns one of them.
    """
    if not lst:
        return None  # Return None for empty lists
        
    counter = Counter(lst)
    return counter.most_common(1)[0][0]  # Get the most common value
    

print('SUCCESS')

#endregion

#===============================================================================================================================================================
#Setting up our Supabase cloud database connection, logging in, AND creating some functions to use to access the data:
#region

print('CONNECTING TO OUR SUPABASE DATABASE, LOGGING IN, AND CREATING FUNCTIONS FOR PULLING/MODIFYING DATA...')

#=========================================================================
#Connecting to our Supabase cloud database:
#region

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

# Supabase credentials
supabase = create_client(supabase_url, supabase_key)


#endregion

#=========================================================================
#Logging in to our Supabase cloud database:
#region

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

#endregion

#=========================================================================
#Writing some functions to use to access/edit our database later in this script:
#region

#================================
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
            #print("Raw response:", response)

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

#================================
#Function for pulling data from our database WITH FILTERS
def fetch_filtered_data(supabase_url: str, supabase_key: str, table: str, filters: dict):
    """
    Fetch all data from a Supabase table where specified columns contain specified values.
    Returns data as a nested list (list of lists).

    :param supabase_url: Supabase project URL.
    :param supabase_key: Supabase API key.
    :param table: Name of the table to query.
    :param filters: Dictionary of column names and their required values.
    :return: Nested list of matching rows.
    """
    # Initialize Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Start building the query
    query = supabase.table(table).select("*")

    # Apply filters
    for column, value in filters.items():
        query = query.eq(column, value)

    # Execute query
    response = query.execute()

    # Extract data properly
    if hasattr(response, 'data'):
        data = response.data  # Use .data attribute instead of .get()
    else:
        raise Exception(f"Unexpected Supabase response format: {response}")

    # Convert the list of dictionaries to a nested list
    nested_list = [list(row.values()) for row in data]

    return nested_list


# filters = {"column1": "value1", "column2": "value2"}
# results = fetch_filtered_data_nested(supabase_url, supabase_key, table_name, filters)
# print(results)

#================================
#Function for deleting rows from a database that have a specified value in a specified column: 
def delete_rows_by_value(supabase_url: str, supabase_key: str, table: str, column: str, value):
    """
    Deletes all rows from a specified Supabase table where a given column contains a specified value.

    Args:
        supabase_url (str): Your Supabase project URL.
        supabase_key (str): Your Supabase service role key.
        table (str): The name of the table from which to delete rows.
        column (str): The column to filter by.
        value: The value to match for deletion (type depends on the column).
    
    Returns:
        dict: The response from Supabase containing the status of the deletion.
    """
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Perform deletion
        response = supabase.table(table).delete().eq(column, value).execute()
        
        return response
    except Exception as e:
        return {"error": str(e)}

# Example Usage

# TABLE_NAME = "your_table_name"
# COLUMN_NAME = "your_column_name"
# VALUE_TO_DELETE = "your_value"

# result = delete_rows_with_value(supabase_url, supabase_key, "Master_Equipment_GPS_Data", "date", "2025-02-07")
# print(result)






#endregion


print('SUCCESS')
#endregion

#===============================================================================================================================================================
#Generating our access token for the HCSS API:
#region

print('CONNECTING TO OUR HCSS API...')

import requests

url = "https://api.hcssapps.com/identity/connect/token"

payload = {
    "client_id": "3i1ruzh3fhvfrrag38dkiqhnh4zp9wze",
    "client_secret": "NoK38HmOjmAj44blOXgsn2nxmPH0YCHiW02XIgbQ",
    "grant_type": "client_credentials",
    "scope": "e360:read e360:write heavyjob:read heavyjob:write timecards:read timecards:write heavyjob:users:read heavyjob:users:write dis:read dis:write skills:read skills:write telematics:read users:read users:write",
    "code": "string",
    "redirect_uri": "string"
}

headers = {"Content-Type": "application/x-www-form-urlencoded"}

response = requests.post(url, data=payload, headers=headers)

data = response.json()

token = data.get('access_token')

#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

print('SUCCESS')

#endregion

#===============================================================================================================================================================
#Connecting to the Smartsheet API and writing some functions for interacting with it:
#region

print('CONNECTING TO OUR SMARTSHEET API...')

#=======================================================================
#Importing the Smartsheet library so that I can interact with it's API:
#SMARTSHEET API TOKEN (Collin's Application) ==> gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1
import smartsheet
import logging

#Initialize client. Uses the API token in the environment variable "SMARTSHEET_ACCESS_TOKEN"
smart = smartsheet.Smartsheet('gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1')

#Make sure we don't miss any errors:
smart.errors_as_exceptions(True)


#=======================================================================
#Writing a function that will allow us to delete all entries in a smartsheet
def delete_all_rows(sheet_id):
    """Deletes all rows from the given Smartsheet."""
    
    # Get the current rows in the sheet
    sheet = smart.Sheets.get_sheet(sheet_id)
    
    # Extract row IDs
    row_ids = [row.id for row in sheet.rows]

    if not row_ids:
        print("No rows to delete.")
        return

    print(f"Deleting {len(row_ids)} rows...")

    # Delete rows in batches (Smartsheet API allows up to 500 rows per request)
    batch_size = 500
    for i in range(0, len(row_ids), batch_size):
        batch = row_ids[i:i+batch_size]
        response = smart.Sheets.delete_rows(sheet_id, batch)
        print(f"Deleted {len(batch)} rows. Response: {response.message}")




print('SUCCESS')

#endregion


#endregion













#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================

#==============================================================================================================================================================================================
#First, let's pull our project data from our smartsheet and update our database:
#region 


#============================================================================
#Pulling data from our smartsheet and saving it to a list

#Creating a sheet object for the smartsheet that we want to read data from, and passing it the sheet id which can be found by looking on the sheet properties on smartsheet (File>Properties>Sheet ID:)
MySheet = smart.Sheets.get_sheet('3259554229866372')

smartSheetProjectInfoList = []

for MyRow in MySheet.rows:
    #========================================
    #Defining some initial values that will be pulled straight from the smartsheet: 
    hcssAPIid = MyRow.cells[0].value
    hcssLegacyID = MyRow.cells[1].value
    jobNum = MyRow.cells[2].value
    jobName = MyRow.cells[3].value
    jobCreationDate = MyRow.cells[4].value
    jobStatus = MyRow.cells[5].value
    lattitude = MyRow.cells[6].value
    longitude = MyRow.cells[7].value
    address1 = MyRow.cells[8].value
    address2 = MyRow.cells[9].value
    jobCity = MyRow.cells[10].value
    jobState = MyRow.cells[11].value
    jobZip = MyRow.cells[12].value
    projectManager = MyRow.cells[13].value
    projectSuper = MyRow.cells[14].value
    startDate = MyRow.cells[15].value
    endDate = MyRow.cells[16].value

    #========================================
    #Updating our list:
    smartSheetProjectInfoList.append([hcssAPIid, hcssLegacyID, jobNum, jobName, jobCreationDate, jobStatus, lattitude, longitude, address1, address2, jobCity, jobState, jobZip, projectManager, projectSuper, startDate, endDate])


#============================================================================
#Deleting all existing entries in our Supabase "Master_Project_Information" database table:
def truncate_table(supabase_url: str, supabase_key: str, table_name: str):
    # Create a Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
                            
    # Truncate the specified table
    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()
                            
truncate_table(supabase_url, supabase_key, 'Master_Project_Information')

#============================================================================
#Function to insert data into the "Master_Project_Information" table
def insert_data(data: dict):
    response = supabase_client.table('Master_Project_Information').insert(data).execute()
    return response

#============================================================================
#Inserting the data into our Supabase database table:
rowcount = 1

for i in range(len(smartSheetProjectInfoList)):
    data_to_insert = {
        'id':rowcount,
        'jobNum':smartSheetProjectInfoList[i][2],
        'jobDescription':smartSheetProjectInfoList[i][3],
        'creationDate':smartSheetProjectInfoList[i][4],
        'jobStatus':smartSheetProjectInfoList[i][5],
        'lattitude':smartSheetProjectInfoList[i][6],
        'longitude':smartSheetProjectInfoList[i][7],
        'address1':smartSheetProjectInfoList[i][8],
        'address2':smartSheetProjectInfoList[i][9],
        'city':smartSheetProjectInfoList[i][10],
        'state':smartSheetProjectInfoList[i][11],
        'zip':smartSheetProjectInfoList[i][12],
        'projectManager':smartSheetProjectInfoList[i][13],
        'projectSuperintendent':smartSheetProjectInfoList[i][14],
        'startDate':smartSheetProjectInfoList[i][15],
        'endDate':smartSheetProjectInfoList[i][16],
        'hcssAPIid':smartSheetProjectInfoList[i][0],
        'legacyID':smartSheetProjectInfoList[i][1]

    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)

#endregion


#==============================================================================================================================================================================================
#Next, pulling the most recent project data from our HCSS API:
#region

#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/heavyjob/api/v1/jobs"

#============================================
#Generating today's date/time and converting it into UTC formatting so that we can feed it as a parameter into our HCSS API query:
from datetime import datetime

def get_current_datetime():
    now = datetime.utcnow()
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_datetime

endDate = str(get_current_datetime())

#============================================
#Listing any parameters here (typically won't use any, for some reason this has been giving me issues):
query = {
        # "jobId": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        # "foremanId": APIID,
        # "employeeId": APIID,
        #"startDate": "2021-01-01T00:00:00Z",
        #"endDate": endDate
        # "modifiedSince": "2019-08-24T14:15:22Z",
        # "cursor": "string",
         "limit": "1000000"
}

#============================================
#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

#============================================
#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.get(HCSS_API_ENDPOINT, headers=HEADERS, params=query)

#A 200 response status code means that the request was successful! Thusly if this repsonse is returned, we will run our script:
if response.status_code == 200:
    data = response.json()

    projectInfoList = []


    for i in range(len(data)):
        hcssID = data[i].get('id')
        legacyID = data[i].get('legacyId')
        jobNum = data[i].get('code')
        jobDescription = data[i].get('description')
        createdDate = data[i].get('createdDate')
        status = data[i].get('status')
        lattitude = data[i].get('latitude')
        longitude = data[i].get('longitude')
        address1 = data[i].get('address1')
        address2 = data[i].get('address2')
        city = data[i].get('city')
        state = data[i].get('state')
        zip = data[i].get('zip')

        projectInfoList.append([hcssID, legacyID, jobNum, jobDescription, createdDate, status, lattitude, longitude, address1, address2, city, state, zip])


#endregion


#==============================================================================================================================================================================================
#Creating a list of projects from our HCSS API data that ARE NOT currently in our smartsheet:
#region

#============================================================================
#First, let's create a list of all projects currently in our smartsheet using our "smartSheetProjectInfoList" created above, and while we're at it store each project's status in a dictionary:

#smartSheetProjectInfoList.append([hcssAPIid, hcssLegacyID, jobNum, jobName, jobCreationDate, jobStatus, lattitude, longitude, address1, address2, jobCity, jobState, jobZip, projectManager, projectSuper, startDate, endDate])

currentSmartsheetProjectNumList = []
smartsheetProjectStatusDict = {}

for i in range(len(smartSheetProjectInfoList)):
    currentSmartsheetProjectNumList.append(smartSheetProjectInfoList[i][2])

    #Storing our project status in a dictionary:
    smartsheetProjectStatusDict[smartSheetProjectInfoList[i][2]]=smartSheetProjectInfoList[i][5]


#============================================================================
#Next, let's iterate through our list of HCSS API project data and create a list of any projects not currently in our smartsheet data list created in the first step of this section. While we're at it, let's also check to update our status if need be:
newProjectInfoList = []

for i in range(len(projectInfoList)):
    apiJobNum = projectInfoList[i][2]

    #=======================================
    #Updating the project status in our smartsheet if it has changed
    entryStatus = projectInfoList[i][5]
    originalStatus = smartsheetProjectStatusDict[apiJobNum]

    #If the status in the smartsheet does not match the status in the API, then we will want to delete the existing entry 
    if entryStatus!=originalStatus:
        pass

    #=======================================
    #If this project isn't currently in our smartsheet, let's add it to our list of values to add to our smartsheet!
    if apiJobNum not in currentSmartsheetProjectNumList:
        newProjectInfoList.append([projectInfoList[i][0], projectInfoList[i][1], projectInfoList[i][2], projectInfoList[i][3], projectInfoList[i][4], projectInfoList[i][5], projectInfoList[i][6], projectInfoList[i][7], projectInfoList[i][8], projectInfoList[i][9], projectInfoList[i][10], projectInfoList[i][11], projectInfoList[i][12]])





#endregion


#==============================================================================================================================================================================================
#Updating our "Master Project Information List" database table with any new entries identified in the previous step:
#region

#=================================================================================================
#Let's calculate what the starting ID value shoudl be so we don't run into any primary key database issues:
#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Master_Project_Information")

rowcount = len(data)+1

#============================================================================
#Function to insert data into the "Master_Project_Information" table
def insert_data(data: dict):
    response = supabase_client.table('Master_Project_Information').insert(data).execute()
    return response

#============================================================================
#Inserting the data into our Supabase database table:

for i in range(len(newProjectInfoList)):
    data_to_insert = {
        'id':rowcount,
        'jobNum':newProjectInfoList[i][2],
        'jobDescription':newProjectInfoList[i][3],
        'creationDate':newProjectInfoList[i][4],
        'jobStatus':newProjectInfoList[i][5],
        'lattitude':newProjectInfoList[i][6],
        'longitude':newProjectInfoList[i][7],
        'address1':newProjectInfoList[i][8],
        'address2':newProjectInfoList[i][9],
        'city':newProjectInfoList[i][10],
        'state':newProjectInfoList[i][11],
        'zip':newProjectInfoList[i][12],
        'projectManager':'NEED TO ADD',
        'projectSuperintendent':'NEED TO ADD',
        'startDate':'NEED TO ADD',
        'endDate':'NEED TO ADD',
        'hcssAPIid':newProjectInfoList[i][0],
        'legacyID':newProjectInfoList[i][1]

    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)

#endregion


#==============================================================================================================================================================================================
#Updating our "Master Project Information List" Smartsheet with our newly updated database values:
#region

#=================================================================================================
#First, let's clear all of the existing values from our smartsheet using the 'delete all rows' function defined at the top of this script:
delete_all_rows(3259554229866372)


#=================================================================================================
#Next, let's update the smartsheet with the values from our database:

#===============================================
#Fetching our database data:
data = fetch_data_from_table("Master_Project_Information")

#===============================================
# Specify your sheet ID
SHEET_ID = 3259554229866372 

#===============================================
#Iterating through our list of values from our databse and updating the smartsheet:
newRowList = []

for i in range(len(data)):

    newRowList.append(smartsheet.models.Row({
        'to_top': True,  # Add row to the top of the sheet
        'cells': [
            {'column_id': 845215518904196, 'value': str(data[i][16])},  
            {'column_id': 4676342050410372, 'value': str(data[i][17])},
            {'column_id': 520962265272196, 'value': str(data[i][1])},
            {'column_id': 5024561892642692, 'value': str(data[i][2])},
            {'column_id': 2424542236725124, 'value': str(data[i][3])},
            {'column_id': 6928141864095620, 'value': str(data[i][4])},
            {'column_id': 1298642329882500, 'value': str(data[i][5])},
            {'column_id': 5802241957252996, 'value': str(data[i][6])},
            {'column_id': 3550442143567748, 'value': str(data[i][7])},
            {'column_id': 8054041770938244, 'value': str(data[i][8])},
            {'column_id': 2772762078957444, 'value': str(data[i][9])},
            {'column_id': 7276361706327940, 'value': str(data[i][10])},
            {'column_id': 735692376461188, 'value': str(data[i][11])},
            {'column_id': 6150461799485316, 'value': str(data[i][12])},
            {'column_id': 8163564913381252, 'value': str(data[i][13])},
            {'column_id': 5315550624567172, 'value': str(data[i][14])},
            {'column_id': 3063750810881924, 'value': str(data[i][15])}
        ]
    }))


#===============================================
#Add rows to the sheet
response = smart.Sheets.add_rows(SHEET_ID, newRowList)



#endregion
