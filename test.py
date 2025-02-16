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

#importing openpyxl for excel interaction, including modules that allow us to incorporate conditional formatting:
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Color, PatternFill, Font, Border
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.styles import Border, Side

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
#Writing a function that will convert the HCSS API UTC date/time into a date that is in US central time: 
from datetime import datetime
from dateutil import tz

def convert_utc_to_central(utc_date_str: str) -> str:
    # Define UTC and Central Time zones
    utc_zone = tz.tzutc()
    central_zone = tz.gettz('America/Chicago')
    
    # Parse the input date string
    utc_datetime = datetime.fromisoformat(utc_date_str)
    
    # Convert to Central Time
    central_datetime = utc_datetime.astimezone(central_zone)
    
    # Return the date in YYYY-MM-DD format
    return central_datetime.strftime('%Y-%m-%d')


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


#================================================================
#Writing a function that will pull the city out of our string that gets returned in our master gps data database table:
import re

def extract_city(address_string: str) -> str:
    """
    Extracts the city name from the given address string.
    The city is always the fourth element in the comma-separated address after 'GPS Coordinate Address:'.
    
    :param address_string: str, formatted address string
    :return: str, extracted city name
    """
    # Extract the part after 'GPS Coordinate Address:'
    match = re.search(r'GPS Coordinate Address: (.+)', address_string)
    
    if match:
        address_parts = [part.strip() for part in match.group(1).split(',')]
        
        # The city is the fourth element in the address structure
        if len(address_parts) >= 4:
            return address_parts[2]  # City name is at index 2 (zero-based index)
    
    return "City not found"  # Return a fallback message if extraction fails

# Example usage
#address_string = "OUTSIDE OF GEOFENCES! GPS Coordinate Address: 308, Plantation Drive, Coppell, Dallas County, Texas, 75019, United States"
#city = extract_city(address_string)


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

print("Pulling the GPS data from the HCSS API and updating our Equipment GPS All Data database...")
start_time = time.time()


#============================================================================
#Connecting to the telematics endpoint of the HCSS API and creating a list of values to be used in updating our "Equipment GPS All Data" database:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/telematics/api/v1/equipment"

#============================================================================
#Listing any parameters here (typically won't use any, for some reason this has been giving me issues):
query = {
        # "jobId": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        # "foremanId": APIID,
        # "employeeId": APIID,
        #"startDate": "2021-01-01T00:00:00Z",
        #"endDate": endDate
        # "modifiedSince": "2019-08-24T14:15:22Z",
        # "cursor": "string",
        # "limit": "1000000"
}

#============================================================================
#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

#============================================================================
#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.get(HCSS_API_ENDPOINT, headers=HEADERS, params=query)

#============================================================================
#Creating a dictionary of values that converts the equipment IDs shown in our telematics system to the standard IDs defined in our "Master Equipment List" smartsheet:

MySheet = smart.Sheets.get_sheet('1336754816634756')

telematicEquipIDconversionDict = {}

for MyRow in MySheet.rows:
    telematicEquipID = MyRow.cells[13].value
    masterListEquipID = MyRow.cells[0].value

    if telematicEquipID!=None:
        telematicEquipIDconversionDict[telematicEquipID]=masterListEquipID


#============================================================================
#A 200 response status code means that the request was successful! Thusly if this repsonse is returned, we will run our script:
if response.status_code == 200:
    data = response.json()

    results = data.get('results')

    equipmentInfoList = []

    for i in range(len(results)):
        equipmentHCSSAPIid = results[i].get('id')
        equipID = results[i].get('code')
        equipDescription = results[i].get('description')
        fuelUom = results[i].get('fuelUom')
        lastBearing = results[i].get('lastBearing')
        lastLatitude = results[i].get('lastLatitude')
        lastLongitude = results[i].get('lastLongitude')
        lastLocationDateTime = results[i].get('lastLocationDateTime')
        lastHourMeterReadingInSeconds = results[i].get('lastHourMeterReadingInSeconds')
        lastHourMeterReadingInHours = results[i].get('lastHourMeterReadingInHours')
        lastHourReadingDateTime = results[i].get('lastHourMeterReadingDateTime')
        lastEngineStatus = results[i].get('lastEngineStatus')
        lastEngineStatusDateTime = results[i].get('lastEngineStatusDateTime')
        
        #===================
        #For some dumb reason, when SS-08 got entered into telematics it had a space added at the end. Correcting here:
        if equipID=='SS-08 ':
            equipID='SS-08'

        #===================
        #Converting equipment IDs to our standard formatting as is listed in the "Equipment Master List" smartsheet:
        if equipID in telematicEquipIDconversionDict:
            equipID=telematicEquipIDconversionDict[equipID]

        #===================
        #Updating our list:
        equipmentInfoList.append([equipmentHCSSAPIid, equipID, equipDescription, fuelUom, lastBearing, lastLatitude, lastLongitude, lastLocationDateTime, lastHourMeterReadingInSeconds, lastHourMeterReadingInHours, lastHourReadingDateTime, lastEngineStatus, lastEngineStatusDateTime])

#============================================================================
#If there wasn't a 200 code received, then there was an error and we will want to break this portion of the script and print out an error message:
else:
    #=======================================
    #Printing out our error message followed by some helpful notes on the response code:
    print('HCSS API ERROR: {}'.format(response.status_code))
    print('Response Code Text: {}'.format(response.text))
    print('Request Error Code Notes:')
    print('    > 400/Bad Request: The most common reason for receiving a a Bad Request (HTTP 400) is sending invalid input.  (e.g., trying to create a cost code on a job that does not exist).')
    print('    > 401/Unauthorized: Most of the time, this error code is caused by a missing token. ')
    print('    > 403/Forbidden: The HCSS API returns Forbidden (HTTP 403) if an authorization token lacks the required scope.  APIs typically have at least two scopes: one providing read access, and one providing read+write.')

    #=======================================
    #Using the "raise" method to throw off an error that will break the try/except statement that this script is running in. We don't want to delete the existing database data if we don't get data from our API!
    raise ValueError("There was an error and no data was retrieved from the HCSS API!")

#============================================================================
#Creating a variable for "today" that is in US Central time because haevy job uses UTC which can have wrong date late in the day!
from datetime import datetime
import pytz

def get_central_time():
    central_tz = pytz.timezone('America/Chicago')  # US Central Time Zone
    central_time = datetime.now(central_tz)  # Get current time in Central Time
    return central_time.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD

todayCentral=str(get_central_time())[0:10]

#============================================================================
#Let's calculate what the starting ID value shoudl be so we don't run into any primary key database issues:

#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Equipment_GPS_All_Data")

rowcount = len(data)+1


#============================================================================
#Function to insert data into the "Equipment_GPS_All_Data" table
def insert_data(data: dict):
    response = supabase_client.table('Equipment_GPS_All_Data').insert(data).execute()
    return response


#============================================================================
#Inserting the data into our Supabase database table:
for i in range(len(equipmentInfoList)):

    #===========================================================
    #Using our function defined at the top of this script to convert the "lastHourReadingDateTime" from our API data into a date that is in US central time:
    if equipmentInfoList[i][10]!=None:
        central_date = convert_utc_to_central(str(equipmentInfoList[i][10]))
    else:
        central_date = 'None'

    #===========================================================
    #If our meter reading date is not for today, then we don't want to add it to our database! This API call returns the last GPS reading for EVERY SINGLE piece of equipment that we have ever owned!
    if central_date==todayCentral:
        #===========================================================
        #Updating our dictionary:
        data_to_insert = {
            'id':rowcount,
            'date':central_date,
            'equipmentHCSSAPIid':equipmentInfoList[i][0],
            'equipID':equipmentInfoList[i][1],
            'equipDescription':equipmentInfoList[i][2],
            'fuelUom':equipmentInfoList[i][3],
            'lastBearing':equipmentInfoList[i][4],
            'lastLatitude':equipmentInfoList[i][5],
            'lastLongitude':equipmentInfoList[i][6],
            'lastLocationDateTime':equipmentInfoList[i][7],
            'lastHourMeterReadingInSeconds':equipmentInfoList[i][8],
            'lastHourMeterReadingInHours':equipmentInfoList[i][9],
            'lastHourReadingDateTime':equipmentInfoList[i][10],
            'lastEngineStatus':equipmentInfoList[i][11],
            'lastEngineStatusDateTime':equipmentInfoList[i][12]
        }

        rowcount=rowcount+1

        #===========================================================
        #Using the "insert_data" function defined at the top of this script
        insert_response = insert_data(data_to_insert)


#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")

#endregion


#==============================================================================================================================================================================================
#Next, let's perform our calculations for the location/hours that each piece of equipment ran has run so far today:
#region

print("Next, let's perform our calculations for the location/hours that each piece of equipment ran has run so far today...")
start_time = time.time()

#=========================================================================================
#Creating a variable for today's date in UTC:
from datetime import datetime

def get_current_datetime():
    now = datetime.utcnow()
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_datetime

today = str(get_current_datetime())[0:10]

#=========================================================================================
#Creating a variable for yesterday's date in US central time as a string in the format "YYYY-MM-DD":
from datetime import datetime, timedelta
import pytz

def get_yesterdays_date_central():
    central_tz = pytz.timezone('America/Chicago')
    now_central = datetime.now(central_tz)
    yesterday = now_central - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


yesterdayCentral = get_yesterdays_date_central()

#=========================================================================================
#First, let's make a list of all equipment entries currently in our "Equipment_GPS_All_Data" table for TODAY'S DATE:
equipmentInfoTodayList = []

#=========================================================================================
#Using our "fetch_filtered_data" function defined at the top of this script to pull all entries for this date:
# filters = {"column1": "value1", "column2": "value2"}
# results = fetch_filtered_data(supabase_url, supabase_key, table_name, filters)
filters = {'date': todayCentral}
data = fetch_filtered_data(supabase_url, supabase_key, "Equipment_GPS_All_Data", filters)

#=========================================================================================
#Iterating through our list of database values and updating our dictionary: 
for i in range(len(data)):
    entryEquipID = data[i][2]
    equipDescr = data[i][3]

    #Making sure to not add duplicate equipment IDs to our list: 
    if [entryEquipID, equipDescr] not in equipmentInfoTodayList:
        equipmentInfoTodayList.append([entryEquipID, equipDescr])


#=========================================================================================
#Accessing our project latitude/longitude coordinates by pulling from our "Master_Project_Information" table:
projectData = fetch_data_from_table("Master_Project_Information")

projectCoordinateDict = {}

for j in range(len(projectData)):
    jobStatus = projectData[j][4]

    #We only want to update our dictionary for active projects
    if jobStatus=='active':
        jobNum = projectData[j][1]
        jobDesc = projectData[j][2]
    
        if projectData[j][5]!='None':
            lat = float(projectData[j][5])
        else:
            lat = 0
        if projectData[j][6]!='None':
            long = float(projectData[j][6])
        else:
            long = 0

        if projectData[j][18]!=None:
            jobRadius = float(projectData[j][18])
        else:
            jobRadius = 0

        #Calculating our lat/long max/min ranges using our function defined above: 
        coordinateMaxMins = get_lat_lng_bounds(lat, long, jobRadius) #Using our "get_lat_lng_bounds" function defined at the top of this script
        min_lat = coordinateMaxMins.get('min_lat')
        max_lat = coordinateMaxMins.get('max_lat')
        min_lng = coordinateMaxMins.get('min_lng')
        max_lng = coordinateMaxMins.get('max_lng')

        projectCoordinateDict[(jobNum, jobDesc)]=[min_lat, max_lat, min_lng, max_lng]


#=========================================================================================
#Next, let's iterate through our list created above and calculate the total hours and location for each:
equipmentInfoDictionary = {}

for i in range(len(equipmentInfoTodayList)):
    entryEquipID = equipmentInfoTodayList[i][0]
    equipDescript = equipmentInfoTodayList[i][1]

    #=========================================
    #Pulling all of the equipment data from our "Equipment_GPS_All_Data" database table for this piece of equipment TODAY and determining the highest meter reading for this equipment TODAY:

    #Using our "fetch_filtered_data" function defined at the top of this script to pull all entries for this equip ID today:
    filters = {"equipID": entryEquipID, 'date': todayCentral}
    results = fetch_filtered_data(supabase_url, supabase_key, "Equipment_GPS_All_Data", filters)

    highestHourReadingToday = 0
    lowestHourReadingToday = 5000000 #Setting this initial value to be an absurdly high number so that our first real value overwrites the initial value

    locationList = []

    for j in range(len(results)):
        #Calculating the min/max hour readings:
        if results[j][10]!=None:
            entryHourReading = float(results[j][10])
        else:
            entryHourReading = 0

        if entryHourReading>highestHourReadingToday:
            highestHourReadingToday=entryHourReading
        if entryHourReading<lowestHourReadingToday:
            lowestHourReadingToday=entryHourReading

        #Updating our location GPS coordinate list for this equipment/date:
        thisLat = results[j][6]
        thisLong = results[j][7]

        locationList.append([thisLat, thisLong])
    

    #=========================================
    #Calculating what the highest meter reading was for this piece of equipment YESTERDAY:

    #===================
    #Using our "fetch_filtered_data" function defined at the top of this script to pull all entries for this equip ID today:
    filters = {"equipID": entryEquipID, 'date': yesterdayCentral}
    results = fetch_filtered_data(supabase_url, supabase_key, "Equipment_GPS_All_Data", filters)

    highestHourReadingYesterday = 0

    #===================
    #If there was a meter reading for this equipment yesterday, then we will use this to define our value for our highest meter reading yesterday: 
    if results!=[]:
        for j in range(len(results)):
            #Calculating the min/max hour readings:
            if results[j][10]!=None:
                entryHourReading = float(results[j][10])
            else:
                entryHourReading = 0

            if entryHourReading>highestHourReadingYesterday:
                highestHourReadingYesterday=entryHourReading

    #===================
    #If there wasn't a meter reading yesterday, then we will want to go through our "Equipment_GPS_All_Data" database for all dates and find the highest reading for a previous date:
    else:
        filters = {"equipID": entryEquipID}
        results = fetch_filtered_data(supabase_url, supabase_key, "Equipment_GPS_All_Data", filters)

        for j in range(len(results)):
            queryDate = results[j][12]

            #Important! We don't want to consider today's date here, so let's filter it out of our calculation:
            if queryDate!=todayCentral:
                #Calculating the min/max hour readings:
                if results[j][10]!=None:
                    entryHourReading = float(results[j][10])
                else:
                    entryHourReading = 0

                if entryHourReading>highestHourReadingYesterday:
                    highestHourReadingYesterday=entryHourReading

        #If there aren't any meter readings for this equipment that aren't for today, then this may be a new piece of equipment. If so, we want to set the highest meter reading value for yesterday to be the lowest for today:
        highestHourReadingYesterday=lowestHourReadingToday


    #=========================================
    #Using our min/max hour readings to calculate the total hours that this equipment ran on this date:
    totalEquipHours = highestHourReadingToday-highestHourReadingYesterday







    print(entryEquipID)
    print(equipDescript)
    print('Total Equipment Hours = {}'.format(totalEquipHours))
    print('Highest Meter Reading TODAY = {}'.format(highestHourReadingToday))
    print('Highest Meter Reading YESTERDAY = {}'.format(highestHourReadingYesterday))
    print('====================================================')



    #=========================================
    #Iterating through our list of GPS coordinates, calculating which project each coordinate entry belongs to, and adding each project value to a list: 
    equipmentProjectList = []

    for j in range(len(locationList)):
        if locationList[j][0]!=None and locationList[j][1]!=None:
            entryLat = float(locationList[j][0])
            entryLong = float(locationList[j][1])
        else:
            entryLat = 0
            entryLong = 0

        #projectCoordinateDict[(jobNum, jobDesc)]=[min_lat, max_lat, min_lng, max_lng]
        for key,values in projectCoordinateDict.items():
            thisJobNum = key[0]
            thisJobDesc = key[1]
            thisJobValue = thisJobNum+'-'+thisJobDesc

            min_lat = values[0]
            max_lat = values[1]
            min_lng = values[2]
            max_lng = values[3]

            #If the longitude/latitude are within the ranges of this project, then we will add to our list:
            if entryLat>=min_lat and entryLat<=max_lat:
                if entryLong>=min_lng and entryLong<=max_lng:
                    equipmentProjectList.append(thisJobValue)

    
    
    #=========================================
    #Using our "most_frequent" function defined at the top of this script to pull the most frequently occuring project from our "equipmentProjectList":
    project = most_frequent(equipmentProjectList)


    #=========================================
    #If our function above does not return a project, then let's display the most frequent address of the equipment using our GPS coordinates
    if project==None:
        #Creating a list of all addresses
        addressList = []

        for j in range(len(locationList)):
            if locationList[j][0]!=None and locationList[j][1]!=None:
                entryLat = float(locationList[j][0])
                entryLong = float(locationList[j][1])
            else:
                entryLat = 0
                entryLong = 0

            address = get_address_from_coordinates(entryLat, entryLong) #using  our "get_address_from_coordinates" function defined at the top of this script
            
            #Adding our GPS coordinates to our address for reference in other scripts:
            address=address+' ('+str(entryLat)+', '+str(entryLong)+')'

            #Updating our address list:
            addressList.append(address)

        #Definng our project variable as the most common address found in our address list:
        project = most_frequent(addressList)
        project = 'OUTSIDE OF GEOFENCES! GPS Coordinate Address: '+str(project)


    #=========================================
    #Updating our dictionary of values to be entered into our database:
    equipmentInfoDictionary[(entryEquipID, todayCentral, equipDescript)] = [round(totalEquipHours,2), project]


#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")
#endregion


#==============================================================================================================================================================================================
#Next, let's enter the values above into our "Master Equipment GPS Data" database
#region

print("Next, let's enter the values above into our Master Equipment GPS Data database...")
start_time = time.time()

#============================================================================
#First, let's delete any rows in this table that are for our current date
result = delete_rows_by_value(supabase_url, supabase_key, "Master_Equipment_GPS_Data", "date", todayCentral)
#print(result)


#============================================================================
#Next, let's calculate what the starting ID value should be so we don't run into any primary key database issues:

#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Master_Equipment_GPS_Data")

rowcount = len(data)+1


#============================================================================
#Function to insert data into the "Master_Equipment_GPS_Data" table
def insert_data(data: dict):
    response = supabase_client.table('Master_Equipment_GPS_Data').insert(data).execute()
    return response

#============================================================================
#Iterating through our dictionary items created above: 
for key,values in equipmentInfoDictionary.items():
    equipID = key[0]
    equipDesc = key[2]
    todayDate = key[1]
    totalEquipHours = values[0]
    projectLocation = values[1]

    
    #============================================================================
    #Inserting the data into our Supabase database table:
    data_to_insert = {
        'id':rowcount,
        'date':todayCentral,
        'equipID':equipID,
        'equipDesc':equipDesc,
        'totalGPShours':totalEquipHours,
        'primaryLocation':projectLocation

    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)


#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")
#endregion


#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")


