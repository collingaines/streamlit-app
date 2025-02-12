#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #0 | IMPORTING OUR PYTHON LIBRARIES: 
#region CLICK HERE TO EXPAND SECTION


#===============================================================================================================================================================
#Importing misc libraries
#region

print('IMPORTING PYTHON LIBRARIES...')

import pandas as pd
import numpy as np
import datetime

#The time module will alow us to pause the script for set periods of time. This can be useful when some information takes a couple of seconds to update properly on the webpage
import time

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

from openpyxl import Workbook
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
#Connecting to the Smartsheet API:
#region

print('CONNECTING TO OUR SMARTSHEET API...')

#Importing the Smartsheet library so that I can interact with it's API:
#SMARTSHEET API TOKEN (Collin's Application) ==> gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1
import smartsheet
import logging

#Initialize client. Uses the API token in the environment variable "SMARTSHEET_ACCESS_TOKEN"
smart = smartsheet.Smartsheet('gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1')

#Make sure we don't miss any errors:
smart.errors_as_exceptions(True)

print('SUCCESS')

#endregion


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================




























#==============================================================================================================================================================================================
#Pulling the GPS data from the HCSS API and updating our "Equipment GPS All Data" database
#region

#===============================================================================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/heavyjob/api/v1/hours/equipment"


#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

#===============================================================================================
#We only want to pull entries for the past 2 weeks, as that is what we will be updating:
#Generating today's date/time and converting it into UTC formatting so that we can feed it as a parameter into our HCSS API query:
from datetime import datetime, timedelta

def get_current_datetime():
    now = datetime.utcnow()
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_datetime

endDate = str(get_current_datetime())

#For our start date of our API query, let's go back 2 weeks. We DO NOT want to use the time, just the date:
current_utc_time = datetime.utcnow()

twoWeeksAgoUTC = current_utc_time - timedelta(weeks=2)

startDate = str(twoWeeksAgoUTC)[0:10]+'T00:00:00'


#Defining our "payload" which will be the filter information that we send to the HCSS API:
payload = {
    "includeAllJobs": True,
    "includeInactiveEquipment": True,
    "startDate": startDate,
    "endDate": endDate,
    }

#===============================================================================================
#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.post(HCSS_API_ENDPOINT, headers=HEADERS, json=payload)


#===============================================================================================
#Looping through the API data and generating a list of values for our database table:

#A 200 response status code means that the request was successful! Thusly if this repsonse is returned, we will run our script:
if response.status_code == 200:
    data = response.json()

    results = data.get('results')

    equipmentHourInfoList = []

    for i in range(len(results)):
        equipmentHCSSAPIid = results[i].get('equipment').get('equipmentId')
        equipmentCode = results[i].get('equipment').get('equipmentCode')
        equipmentDescription = results[i].get('equipment').get('equipmentDescription')
        isRental = results[i].get('equipment').get('isRental')
        
        foremanHCSSAPIid = results[i].get('foreman').get('employeeId')
        employeeCode = results[i].get('foreman').get('employeeCode')
        employeeFirstName = results[i].get('foreman').get('employeeFirstName')
        employeeLastName = results[i].get('foreman').get('employeeLastName')

        jobHCSSAPIId = results[i].get('job').get('jobId')
        jobCode = results[i].get('job').get('jobCode')
        jobDescription = results[i].get('job').get('jobDescription')

        date = results[i].get('date')

        notes = results[i].get('notes')

        meterStart = results[i].get('meterStart')
        meterStop = results[i].get('meterStop')
        timeCardShift = results[i].get('timeCardShift')
        timeCardRevision = results[i].get('timeCardRevision')

        gpsID = results[i].get('gpsID')
        rowOrder = results[i].get('rowOrder')

        if results[i].get('linkedEmployee')!=None:
            linkedEmployeeHCSSAPIid = results[i].get('linkedEmployee').get('id')
            code = results[i].get('linkedEmployee').get('code')
            firstName = results[i].get('linkedEmployee').get('firstName')
            lastName = results[i].get('linkedEmployee').get('lastName')

            linkedEmployeeRowOrder = results[i].get('linkedEmployeeRowOrder')
        else:
            linkedEmployeeHCSSAPIid = 'None'
            code = 'None'
            firstName = 'None'
            lastName = 'None'

            linkedEmployeeRowOrder = 'None'


        #The hours charged for each piece of eqiupment come in a list of dictinoaries for each cost code, so let's create a list here to store these values
        costCodeHourList = results[i].get('hoursDetails')


        for j in range(len(costCodeHourList)):
            costCodeHCSSAPIid = costCodeHourList[j].get('costCode').get('costCodeId')
            costCodeCode = costCodeHourList[j].get('costCode').get('costCodeCode')
            costCodeDescription = costCodeHourList[j].get('costCode').get('costCodeDescription')
        
            totalHours = costCodeHourList[j].get('totalHours')
            isInTimeCardHours = costCodeHourList[j].get('isInTimeCardHours')
            isCosted = costCodeHourList[j].get('isCosted')

            #======================================================
            #Finally, updating our database. Let's keep it inside of this loop so that a new row of our databse is added for each cost code entry for this equipment:
            
            equipmentHourInfoList.append([
                equipmentHCSSAPIid,
                equipmentCode,
                equipmentDescription,
                isRental,
                foremanHCSSAPIid,
                employeeCode,
                employeeFirstName,
                employeeLastName,
                jobHCSSAPIId,
                jobCode,
                jobDescription,
                date,
                notes,
                meterStart,
                meterStop,
                timeCardShift,
                timeCardRevision,
                costCodeHCSSAPIid,
                costCodeCode,
                costCodeDescription,
                totalHours,
                isInTimeCardHours,
                isCosted,
                gpsID,
                rowOrder,
                linkedEmployeeHCSSAPIid,
                code,
                firstName,
                lastName,
                linkedEmployeeRowOrder
                ])


#===============================================================================================
#Let's delete all existing entries up to 2 weeks back so that we don't enter any duplicate entries into our database:

#=======================================
#First, let's create a list of dates to iterate through when delete prior entries: 
from datetime import datetime, timedelta
import pytz

# Define US Central Time Zone
central_tz = pytz.timezone('America/Chicago')

# Get today's date in US Central Time
today = datetime.now(central_tz).date()

# Generate list of dates for the past 14 days
dateToDeleteList = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15)]

#=======================================
#Next, let's iterate through our date list and delete the entries in our databse for each:
for i in range(len(dateToDeleteList)):
    entryDate = dateToDeleteList[i]
    result = delete_rows_by_value(supabase_url, supabase_key, "Equipment_Timecard_All_Data", "date", entryDate)


#=================================================================================================
#Let's calculate what the starting ID value shoudl be so we don't run into any primary key database issues:
#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Equipment_Timecard_All_Data")

rowcount = len(data)+1


#=========================================================================================
#Function to insert data into the "Equipment_GPS_All_Data" table
def insert_data(data: dict):
    response = supabase_client.table('Equipment_Timecard_All_Data').insert(data).execute()
    return response


#=========================================================================================
#Inserting the data into our Supabase database table:
for i in range(len(equipmentHourInfoList)):

    data_to_insert = {
        'id':rowcount,
        'equipmentHCSSAPIid':equipmentHourInfoList[i][0],
        'equipmentCode':equipmentHourInfoList[i][1],
        'equipmentDescription':equipmentHourInfoList[i][2],
        'isRental':equipmentHourInfoList[i][3],
        'foremanHCSSAPIid':equipmentHourInfoList[i][4],
        'employeeCode':equipmentHourInfoList[i][5],
        'employeeFirstName':equipmentHourInfoList[i][6],
        'employeeLastName':equipmentHourInfoList[i][7],
        'jobHCSSAPIId':equipmentHourInfoList[i][8],
        'jobCode':equipmentHourInfoList[i][9],
        'jobDescription':equipmentHourInfoList[i][10],
        'date':equipmentHourInfoList[i][11],
        'notes':equipmentHourInfoList[i][12],
        'meterStart':equipmentHourInfoList[i][13],
        'meterStop':equipmentHourInfoList[i][14],
        'timeCardShift':equipmentHourInfoList[i][15],
        'timeCardRevision':equipmentHourInfoList[i][16],
        'costCodeHCSSAPIid':equipmentHourInfoList[i][17],
        'costCodeCode':equipmentHourInfoList[i][18],
        'costCodeDescription':equipmentHourInfoList[i][19],
        'totalHours':equipmentHourInfoList[i][20],
        'isInTimeCardHours':equipmentHourInfoList[i][21],
        'isCosted':equipmentHourInfoList[i][22],
        'gpsID':equipmentHourInfoList[i][23],
        'rowOrder':equipmentHourInfoList[i][24],
        'linkedEmployeeHCSSAPIid':equipmentHourInfoList[i][25],
        'code':equipmentHourInfoList[i][26],
        'firstName':equipmentHourInfoList[i][27],
        'lastName':equipmentHourInfoList[i][28],
        'linkedEmployeeRowOrder':equipmentHourInfoList[i][29]

    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)



#endregion


#==============================================================================================================================================================================================
#Next, let's consolidate our equipment hour entries and enter them into our "Master_Equipment_Timecard_Data" database table:
#region


#=================================================================================================
#First, let's iterate through our list of equipment hour data created above and create a dictionary that sums the total hours for each piece of equipment/date:
equipmentHourDictionary = {}

for i in range(len(equipmentHourInfoList)):
    equipCode = equipmentHourInfoList[i][1]
    equipDescription = equipmentHourInfoList[i][2]
    date = equipmentHourInfoList[i][11]
    jobCode = equipmentHourInfoList[i][9]
    jobDescription = equipmentHourInfoList[i][10]
    foremanCode = equipmentHourInfoList[i][5]
    foreman = equipmentHourInfoList[i][6]+' '+equipmentHourInfoList[i][7]
    costCode = equipmentHourInfoList[i][18]
    fullCostCode = jobCode+'.'+costCode
    equipmentHours = equipmentHourInfoList[i][20]
    equipmentHCSSAPIid = equipmentHourInfoList[i][0]

    #Creating a key for our dictinoary:
    key = (equipCode, date)

    #If this key is already in our dictionary, we will add to the existing equipment hour values:
    if key in equipmentHourDictionary:
        newEquipmentHours = float(equipmentHourDictionary[key][4])+float(equipmentHours)

        equipmentHourDictionary[key]=[equipDescription, jobCode, fullCostCode, foreman, newEquipmentHours, equipmentHCSSAPIid, jobDescription, foremanCode]

    #If not, then we will enter our values straight into the dictionary:
    else:
        equipmentHourDictionary[key]=[equipDescription, jobCode, fullCostCode, foreman, equipmentHours, equipmentHCSSAPIid, jobDescription, foremanCode]


#=================================================================================================
#Next, let's iterate through our date list of every date the past 2 weeks (created above) and delete the entries in our database for each:
for i in range(len(dateToDeleteList)):
    entryDate = dateToDeleteList[i]
    result = delete_rows_by_value(supabase_url, supabase_key, "Master_Equipment_Timecard_Data", "date", entryDate)


#=================================================================================================
#Let's calculate what the starting ID value shoudl be so we don't run into any primary key database issues:
#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Master_Equipment_Timecard_Data")

rowcount = len(data)+1


#=================================================================================================
#Function to insert data into the "Master_Equipment_Timecard_Data" table
def insert_data(data: dict):
    response = supabase_client.table('Master_Equipment_Timecard_Data').insert(data).execute()
    return response


#=================================================================================================
#Finally, let's iterate through the items in our dictionary above and add them to our database: 
for key,values in equipmentHourDictionary.items():
    data_to_insert = {
        'id':rowcount,
        'equipmentCode':key[0],
        'equipmentDescription':values[0],
        'date':key[1],
        'jobCode':values[1],
        'fullCostCode':values[2],
        'foreman':values[3],
        'equipmentHours':values[4],
        'equipmentHCSSAPIid':values[5],
        'jobDescription':values[6],
        'foremanCode':values[7]

    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)





















#endregion

