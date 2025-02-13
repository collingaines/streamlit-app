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

def get_lat_lng_bounds(lat, lng, radius_miles):
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

    # print(f"Deleting {len(row_ids)} rows...")

    # Delete rows in batches (Smartsheet API allows up to 500 rows per request)
    batch_size = 500
    for i in range(0, len(row_ids), batch_size):
        batch = row_ids[i:i+batch_size]
        response = smart.Sheets.delete_rows(sheet_id, batch)
        # print(f"Deleted {len(batch)} rows. Response: {response.message}")




print('SUCCESS')

#endregion


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Smartsheet Equipment Inspection Sheet Info>')
print('<========================================================================================================================>')
print('Connecting to the Smartsheet API and pulling data from the "Equipment Inspection" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION

start_time = time.time()

#==========================================================================================================================================================================
#Deleting all existing entries in our Supabase "Cost_Code_Classifiers" database table:
def truncate_table(supabase_url: str, supabase_key: str, table_name: str):
    # Create a Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
                            
    # Truncate the specified table
    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()
                            
truncate_table(supabase_url, supabase_key, 'Equipment_Inspection_Log')

#==========================================================================================================================================================================
#Connecting to the smartsheet api and pulling data from the equipment inspection smartsheet

#Creating a sheet object for the smartsheet that we want to read data from, and passing it the sheet id which can be found by looking on the sheet properties on smartsheet (File>Properties>Sheet ID:)
MySheet = smart.Sheets.get_sheet('8508814782687108')

#==========================================================================================================================================================================
#Now, let's itterate through each of the smartsheet rows and add the values to a list which we can send to our database: 
dbEntryList = []
rowcount = 1

for MyRow in MySheet.rows:
    #============================================================================
    #Defining some initial values that will be pulled straight from the smartsheet: 
    equipmentDescription = MyRow.cells[0].value
    jobSite = MyRow.cells[1].value
    inspectionDate = MyRow.cells[2].value
    notes = MyRow.cells[3].value
    superintendent = MyRow.cells[4].value
    foremanCapataz = MyRow.cells[5].value
    hourReader = MyRow.cells[6].value
    fuelLevel = MyRow.cells[7].value
    fireExtinguisher = MyRow.cells[8].value
    mirrorCondition = MyRow.cells[9].value
    glassCondition = MyRow.cells[10].value
    batteryCondition = MyRow.cells[11].value
    engineOilLevel = MyRow.cells[12].value
    hydraulicOilLevel = MyRow.cells[13].value
    coolantLevel = MyRow.cells[14].value
    engineBelt = MyRow.cells[15].value
    fluidLeaks = MyRow.cells[16].value
    hornWorking = MyRow.cells[17].value
    backupAlarmWorking = MyRow.cells[18].value
    lightsWorking = MyRow.cells[19].value
    seatBeltWorking = MyRow.cells[20].value
    brakesWorking = MyRow.cells[21].value
    tireTrackCondition = MyRow.cells[22].value
    forks = MyRow.cells[23].value
    bristleCondition = MyRow.cells[24].value
    drumCondition = MyRow.cells[25].value
    bucketCondition = MyRow.cells[26].value
    trailerBrakes = MyRow.cells[27].value
    operatorName = MyRow.cells[28].value
    foreman = MyRow.cells[29].value

    #============================================================================
    #Pulling the equipment ID from the equipment description:
    if equipmentDescription==None:
        equipID = 'No Eqiup ID Found'
    elif ":" in equipmentDescription:
        equipID = equipmentDescription[0:equipmentDescription.index(':')]
    else:
        equipID = 'No Eqiup ID Found'

    #============================================================================
    #Pulling the job number from our jobsite value:
    if jobSite==None:
        jobNum = 'None Found'
    else:
        jobNum = jobSite[0:5]

    #============================================================================
    #Converting our date value into our standard format (2025-09-30):
    if inspectionDate==None:
        dateFormatted = 'None Found'
    else:
        year = '20'+str(inspectionDate)[6:8]
        month = str(inspectionDate)[0:2]
        day = str(inspectionDate)[3:5]

        dateFormatted = str(inspectionDate)
        #dateFormatted = year+'-'+month+'-'+day

    #============================================================================
    #Function to insert data into the "Cost_Code_Classifiers" table
    def insert_data(data: dict):
        response = supabase_client.table('Equipment_Inspection_Log').insert(data).execute()
        return response

    #============================================================================
    #Inserting the data into our Supabase database table:
    data_to_insert = {
            'id':rowcount,
            'equipmentID':equipID,
            'equipmentDesc':equipmentDescription,
            'jobsite':jobSite,
            'jobNum':jobNum,
            'inspectionDate':dateFormatted,
            'notes':notes,
            'superintendent':superintendent,
            'foremanCapataz':foremanCapataz,
            'hourReading':hourReader,
            'fuelLevel':fuelLevel,
            'fireExtinguisher':fireExtinguisher,
            'mirrorCondition':mirrorCondition,
            'glassCondition':glassCondition,
            'batteryCondition':batteryCondition,
            'engineOilLevel':engineOilLevel,
            'hydraulicOilLevel':hydraulicOilLevel,
            'coolantLevel':coolantLevel,
            'engineBelt':engineBelt,
            'fluidLeaks':fluidLeaks,
            'hornWorking':hornWorking,
            'backupAlarmWorking':backupAlarmWorking,
            'lightsWorking':lightsWorking,
            'seatbeltWorking':seatBeltWorking,
            'brakesWorking':brakesWorking,
            'tireTrackCondition':tireTrackCondition,
            'forks':forks,
            'bristleCondition':bristleCondition,
            'drumCondition':drumCondition,
            'bucketCondition':bucketCondition,
            'trailerBrakes':trailerBrakes,
            'operatorName':operatorName,
            'foreman':foreman

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


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Updating "Master_Equipment_Asset_List" Database Table from our "Master Equipment List" Smartsheet>')
print('<========================================================================================================================>')
print('Connecting to the Smartsheet API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION

start_time = time.time()

#==========================================================================================================================================================================
#Deleting all existing entries in our Supabase "Cost_Code_Classifiers" database table:
def truncate_table(supabase_url: str, supabase_key: str, table_name: str):
    # Create a Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
                            
    # Truncate the specified table
    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()
                            
truncate_table(supabase_url, supabase_key, 'Master_Equipment_Asset_List')

#==========================================================================================================================================================
#First, let's pull all of the updated equipment info from our "Master Equipment List" smartsheet and add the values to a list:

#Creating a sheet object for the smartsheet that we want to read data from, and passing it the sheet id which can be found by looking on the sheet properties on smartsheet (File>Properties>Sheet ID:)
MySheet = smart.Sheets.get_sheet('1336754816634756')

rowcount=1

for MyRow in MySheet.rows:
    #============================================================================
    #Defining some initial values that will be pulled straight from the smartsheet: 
    equipmentID = MyRow.cells[0].value
    equipmentDescription = MyRow.cells[1].value
    equipmentCategory = MyRow.cells[2].value
    make = MyRow.cells[3].value
    model = MyRow.cells[4].value
    year = MyRow.cells[5].value
    serialNumber = MyRow.cells[6].value
    equipmentStatus = MyRow.cells[7].value
    purchaseDate = MyRow.cells[8].value
    sellDate = MyRow.cells[9].value
    inspectionStatus = MyRow.cells[10].value
    chargeType = MyRow.cells[11].value
    telematicEquipID = MyRow.cells[13].value
    heavyJobEquipID = MyRow.cells[14].value
    ceEquipID = MyRow.cells[15].value

    #============================================================================
    #Function to insert data into the "Cost_Code_Classifiers" table
    def insert_data(data: dict):
        response = supabase_client.table('Master_Equipment_Asset_List').insert(data).execute()
        return response

    #============================================================================
    #Inserting the data into our Supabase database table:
    data_to_insert = {
            'id':rowcount,
            'equipID':equipmentID,
            'equipDesc':equipmentDescription,
            'equipCategory':equipmentCategory,
            'make':make,
            'model':model,
            'year':year,
            'serialNum':serialNumber,
            'status':equipmentStatus,
            'purchaseDate':purchaseDate,
            'sellDate':sellDate,
            'inspectionsReqd':inspectionStatus,
            'chargeType':chargeType,
            'telematicEquipID':telematicEquipID,
            'heavyJobEquipID':heavyJobEquipID,
            'ceEquipID':ceEquipID
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


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Updating Smartsheet Equipment Inspection & Fuel Log Dropdown Data>')
print('<========================================================================================================================>')
print('Connecting to the Smartsheet API and updating dropdown lists...')
#region CLICK HERE TO EXPAND THIS SECTION

start_time = time.time()

#==========================================================================================================================================================
#First, let's pull all of the updated equipment info from our "Master Equipment List" smartsheet and add the values to a list:

#Creating a sheet object for the smartsheet that we want to read data from, and passing it the sheet id which can be found by looking on the sheet properties on smartsheet (File>Properties>Sheet ID:)
MySheet = smart.Sheets.get_sheet('1336754816634756')

equipmentInfoList = []

for MyRow in MySheet.rows:
    #============================================================================
    #Defining some initial values that will be pulled straight from the smartsheet: 
    equipmentID = MyRow.cells[0].value
    equipmentDescription = MyRow.cells[1].value
    equipmentStatus = MyRow.cells[7].value
    inspectionStatus = MyRow.cells[10].value

    #If this is an active piece of equipment and requires an inspection, then we will add it to our list:
    if equipmentStatus=="Active":
        if inspectionStatus=='Yes':
            equipmentListValue = equipmentID+': '+equipmentDescription

            equipmentInfoList.append(equipmentListValue)

    
#Sorting the equipment IDs so that they are in alphabetical order: 
equipmentInfoList=sorted(equipmentInfoList, key=lambda x: x[0])

#==========================================================================================================================================================
#Next, let's navigate to our equipment inspection sheet and update the list of dropdown values:
#TEMPORARY: THIS SCRIPT WILL UPDATE A DROPDOWN ON THE MASTER LIST AS A TEST

# Step 1: Get the list of columns and find the dropdown column ID
columns = smart.Sheets.get_sheet('1336754816634756').columns
dropdown_column = next((col for col in columns if col.title == "TEST"), None)

if not dropdown_column:
    print(f"Column not found!")
    exit()

COLUMN_ID = dropdown_column.id  # Store the column ID
#current_options = list(dropdown_column.options)  # Convert TypedList to a standard list

# Step 2: Add new options to the dropdown list
new_options = equipmentInfoList  # Replace with your items
# updated_options = list(set(new_options))  # Ensure unique values

# Step 3: Update the column WITHOUT specifying "id"
updated_column = smartsheet.models.Column()
updated_column.title = dropdown_column.title  # Keep column title the same
updated_column.type = "PICKLIST"  # Explicitly set the column type
updated_column.options = new_options  # Apply new dropdown values

# Step 4: Send update request
response = smart.Sheets.update_column('1336754816634756', COLUMN_ID, updated_column)

#print(f"Updated Dropdown List: {new_options}")

#==========================================================================================================================================================
#Next, let's navigate to our equipment fuel log smartsheet and update the list of dropdown values:
#TEMPORARY: THIS SCRIPT WILL UPDATE A DROPDOWN ON THE MASTER LIST AS A TEST

# Step 1: Get the list of columns and find the dropdown column ID
columns = smart.Sheets.get_sheet('1336754816634756').columns
dropdown_column = next((col for col in columns if col.title == "TEST"), None)

if not dropdown_column:
    print(f"Column not found!")
    exit()

COLUMN_ID = dropdown_column.id  # Store the column ID
#current_options = list(dropdown_column.options)  # Convert TypedList to a standard list

# Step 2: Add new options to the dropdown list
new_options = equipmentInfoList  # Replace with your items
# updated_options = list(set(new_options))  # Ensure unique values

# Step 3: Update the column WITHOUT specifying "id"
updated_column = smartsheet.models.Column()
updated_column.title = dropdown_column.title  # Keep column title the same
updated_column.type = "PICKLIST"  # Explicitly set the column type
updated_column.options = new_options  # Apply new dropdown values

# Step 4: Send update request
response = smart.Sheets.update_column('1336754816634756', COLUMN_ID, updated_column)


#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")

#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our project data, and updating our database and smartsheet "Master Project Info List">')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and updating our "Master_Project_Information" database table...')
#region CLICK HERE TO EXPAND THIS SECTION

start_time = time.time()

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
    projectRadius = MyRow.cells[17].value

    #========================================
    #Updating our list:
    smartSheetProjectInfoList.append([hcssAPIid, hcssLegacyID, jobNum, jobName, jobCreationDate, jobStatus, lattitude, longitude, address1, address2, jobCity, jobState, jobZip, projectManager, projectSuper, startDate, endDate, projectRadius])


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
        'legacyID':smartSheetProjectInfoList[i][1],
        'projectRadius':smartSheetProjectInfoList[i][17]

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
        'legacyID':newProjectInfoList[i][1],
        'projectRadius':'NEED TO ADD'

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
            {'column_id': 3063750810881924, 'value': str(data[i][15])},
            {'column_id': 205938309156740, 'value': str(data[i][18])}
        ]
    }))


#===============================================
#Add rows to the sheet
response = smart.Sheets.add_rows(SHEET_ID, newRowList)



#endregion




#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our timecard data, and updating our database>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and updating our "Master_Timecard_Information" database table...')
#region CLICK HERE TO EXPAND THIS SECTION

start_time = time.time()

#==========================================================================================================================
#First, let's create a dictionary that ties the project HCSS API ID to a project name for use when updating our database

#=================================
#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Master_Project_Information")

apiProjectNameDict = {}

for i in range(len(data)):
    apiID = data[i][16]
    jobNum = data[i][1]
    jobDescription = data[i][2]

    apiProjectNameDict[apiID]=[jobNum, jobDescription]


#=================================
#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Users")

userCraftDict = {}

for i in range(len(data)):
    employeeID = data[i][1]
    employeeCraft = data[i][5]

    userCraftDict[employeeID]=employeeCraft




#==========================================================================================================================
#Creating a list of timecard values for use later in calculating the timecard values for each foreman:
#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/heavyjob/api/v1/timeCardApprovalInfo"

#Generating today's date/time and converting it into UTC formatting so that we can feed it as a parameter into our HCSS API query:
from datetime import datetime

def get_current_datetime():
    now = datetime.utcnow()
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_datetime

endDate = str(get_current_datetime())

#Listing any parameters here (typically won't use any, for some reason this has been giving me issues):
query = {
        # "jobId": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        # "foremanId": APIID,
        # "employeeId": APIID,
        "startDate": "2021-01-01T00:00:00Z",
        "endDate": endDate,
        # "modifiedSince": "2019-08-24T14:15:22Z",
        # "cursor": "string",
         "limit": "1000"
}

#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.get(HCSS_API_ENDPOINT, headers=HEADERS, params=query)

#A 200 response status code means that the request was successful! Thusly if this repsonse is returned, we will run our script:
if response.status_code == 200:
    data = response.json()

    #The data comes as a list with nested dictionaries format, with the data we want coming from the "results" index:
    results = data.get('results')

    timecardInfoList = []

    for i in range(len(results)):
        #Pulling our raw data from the API:
        timecardID = results[i].get('id')
        foremanAPIid = results[i].get('foreman').get('employeeId')
        foremanCode = results[i].get('foreman').get('employeeCode')
        employeeFN = results[i].get('foreman').get('employeeFirstName')
        employeeLN = results[i].get('foreman').get('employeeLastName')
        jobID = results[i].get('jobId')
        businessUnitId = results[i].get('businessUnitId')
        TCdate = results[i].get('date')
        revision = results[i].get('revision')
        shift = results[i].get('shift')
        lastModifiedDateTime = results[i].get('lastModifiedDateTime')
        isApproved = results[i].get('isApproved')
        lastChangedBy = results[i].get('lastChangedByName')
        lastPreparedBy = results[i].get('lastPreparedByName')
        isReviewed = results[i].get('isReviewed')
        isAccepted = results[i].get('isAccepted')
        isRejected = results[i].get('isRejected')
        firstSubmitted = results[i].get('lockedDateTime')

        #Creating a variable for the full employee name
        employee = str(employeeFN) + ' '+str(employeeLN)

        #Using our dictionary created above to pull job name/num using the HCSS job ID:
        #apiProjectNameDict[apiID]=[jobNum, jobDescription]
        if jobID in apiProjectNameDict:
            jobNum = apiProjectNameDict[jobID][0]
            jobDescription = apiProjectNameDict[jobID][1]
        else:
            jobNum = 'None Found'
            jobDescription = 'None Found'

        #Using our dictionary created above to pull the employee trade from our employeeID:
        #userCraftDict[employeeID]=employeeCraft
        if foremanCode in userCraftDict:
            employeeCraft = userCraftDict[foremanCode]
        else:
            employeeCraft = 'None'

        #Converting the timecard date to datetime format:
        import datetime

        TCdateDT = datetime.datetime(int(str(TCdate)[0:4]),int(str(TCdate)[5:7]),int(str(TCdate)[8:10]), 0, 0, 0)

        if firstSubmitted != None:
            firstSubmittedDT = datetime.datetime(int(str(firstSubmitted)[0:4]),int(str(firstSubmitted)[5:7]),int(str(firstSubmitted)[8:10]),abs(int(str(firstSubmitted)[11:13])-5),int(str(firstSubmitted)[14:16]),int(str(firstSubmitted)[17:19]))
            delta = firstSubmittedDT-TCdateDT

        else:
            firstSubmittedDT = TCdateDT
            delta = firstSubmittedDT-TCdateDT

        #====================
        #Copying older code from scraper:
        #If the timecard day is a Friday or Saturday, we won't expect that the timecard will be submitted until the following Monday.
        #let's write a function to check this, bc when i import "datetime from datetime" it throws the whole program off, bc i have datetime referenced in other places and at the top of the script i just imported datetime
        def dayofweek(date):
            from datetime import datetime
            return date.weekday()

        day = dayofweek(TCdateDT)

        #Let's go ahead and define our time periods which will constitute late vs on time timecard submissions:
        #Timecard cutoff is 10am the following date, so this will equate to exactly 34 hours after 12am on the previous day
        timecardLate = datetime.timedelta(days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=10, weeks=0)


        #If the day is Friday(4), then we will give them 3 days, 10 hours (until Monday morning at 10am) to submit their timecard
        if day == 4:
            timecardLate = datetime.timedelta(days=3, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=10, weeks=0)

        #If the day is Saturday(5), then we will give them 2 days, 10 hours (until Monday morning at 10am) to submit their timecard
        if day == 5:
            timecardLate = datetime.timedelta(days=2, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=10, weeks=0)

        #Finally, let's determine if the timecard is late or not:
        if delta>timecardLate:
            ontime = 'LATE'
        else:
            ontime = 'YES'

        #====================
        timecardInfoList.append([jobNum, jobDescription, employee, foremanCode, TCdate, firstSubmitted, str(delta), ontime, employeeCraft, timecardID, foremanAPIid, jobID, revision, lastModifiedDateTime, isApproved, lastChangedBy, lastPreparedBy, isReviewed, isAccepted, isRejected])


    # return render_template('Paperwork - Timecard Tracking Summary.html', tcList=tcList, results=results, token=token)
 #If a 200 response code is not recieved, then that means there was an error.
else:
    #Returning the error code number and displaying on the webpage:
    print(f"Failed to retrieve data from the HCSS API for timecards. Status code: {response.status_code}")

    #Error Code Dictionary (info from: https://developer.hcssapps.com/getting-started/troubleshoot-bad-request/):
    #   > Bad Request (HTTP 400): The most common reason for receiving a a Bad Request (HTTP 400) is sending invalid input.  (e.g., trying to create a cost code on a job that does not exist).
    #   > Unauthorized (HTTP 401): The HCSS API returns Unauthorized (HTTP 401) if the authentication token is missing or expired. Most of the time, this error code is caused by a missing token.
    #   > Forbidden (HTTP 403): The HCSS API returns Forbidden (HTTP 403) if an authorization token lacks the required scope.  APIs typically have at least two scopes: one providing read access, and one providing read+write.


#==============================================================================================================================================================================================
#Next, let's update our "Master_Timecard_Information" database:
#============================================================================
#Deleting all existing entries in our Supabase "Cost_Code_Classifiers" database table:
def truncate_table(supabase_url: str, supabase_key: str, table_name: str):
    # Create a Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
                            
    # Truncate the specified table
    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()
                            
truncate_table(supabase_url, supabase_key, 'Master_Timecard_Information')

#============================================================================
#Function to insert data into the "Cost_Code_Classifiers" table
def insert_data(data: dict):
    response = supabase_client.table('Master_Timecard_Information').insert(data).execute()
    return response

#============================================================================
#Inserting the data into our Supabase database table:
rowcount = 1

dataList = []

for i in range(len(timecardInfoList)):
    data_to_insert = {
        'id':rowcount,
        'jobCode':timecardInfoList[i][0],
        'jobDescription':timecardInfoList[i][1],
        'employeeName':timecardInfoList[i][2],
        'employeeCode':timecardInfoList[i][3],
        'timecardDate':timecardInfoList[i][4],
        'firstSubmittedDate':timecardInfoList[i][5],
        'timeDelta':timecardInfoList[i][6],
        'onTime':timecardInfoList[i][7],
        'employeeTrade':timecardInfoList[i][8],
        'timecardID':timecardInfoList[i][9],
        'employeeAPIid':timecardInfoList[i][10],
        'jobID':timecardInfoList[i][11],
        'revision':timecardInfoList[i][12],
        'lastModifiedDT':timecardInfoList[i][13],
        'isApproved':timecardInfoList[i][14],
        'lastChangedBy':timecardInfoList[i][15],
        'lastPrepedBy':timecardInfoList[i][16],
        'isReviewed':timecardInfoList[i][17],
        'isAccepted':timecardInfoList[i][18],
        'isRejected':timecardInfoList[i][19]

    }

    rowcount=rowcount+1

    dataList.append(data_to_insert)
    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)




#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")



#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our GPS hour/location data, and updating our database>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and updating our "Equipment_GPS_All_Data" and "Master_Equipment_GPS_Data" database table...')
#region CLICK HERE TO EXPAND THIS SECTION

#==============================================================================================================================================================================================
#Pulling the GPS data from the HCSS API and updating our "Equipment GPS All Data" database
#region

print("Pulling the GPS data from the HCSS API and updating our Equipment GPS All Data database...")
start_time = time.time()


#=========================================================================================
#Connecting to the telematics endpoint of the HCSS API and creating a list of values to be used in updating our "Equipment GPS All Data" database:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/telematics/api/v1/equipment"

#=========================================
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

#=========================================
#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

#=========================================
#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.get(HCSS_API_ENDPOINT, headers=HEADERS, params=query)

#=========================================
#Creating a dictionary of values that converts the equipment IDs shown in our telematics system to the standard IDs defined in our "Master Equipment List" smartsheet:

MySheet = smart.Sheets.get_sheet('1336754816634756')

telematicEquipIDconversionDict = {}

for MyRow in MySheet.rows:
    telematicEquipID = MyRow.cells[13].value
    masterListEquipID = MyRow.cells[0].value

    if telematicEquipID!=None:
        telematicEquipIDconversionDict[telematicEquipID]=masterListEquipID


#=========================================
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


#=========================================================================================
#Creating a variable for "today" that is in US Central time because haevy job uses UTC which can have wrong date late in the day!
from datetime import datetime
import pytz

def get_central_time():
    central_tz = pytz.timezone('America/Chicago')  # US Central Time Zone
    central_time = datetime.now(central_tz)  # Get current time in Central Time
    return central_time.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD

todayCentral=str(get_central_time())[0:10]

#=========================================================================================
#Let's calculate what the starting ID value shoudl be so we don't run into any primary key database issues:

#Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
data = fetch_data_from_table("Equipment_GPS_All_Data")

rowcount = len(data)+1


#=========================================================================================
#Function to insert data into the "Equipment_GPS_All_Data" table
def insert_data(data: dict):
    response = supabase_client.table('Equipment_GPS_All_Data').insert(data).execute()
    return response


#=========================================================================================
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
#Creating a variable for today's date:
from datetime import datetime

def get_current_datetime():
    now = datetime.utcnow()
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_datetime

today = str(get_current_datetime())[0:10]

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
    #Using our "fetch_filtered_data" function defined at the top of this script to pull all entries for this equip ID:
    # filters = {"column1": "value1", "column2": "value2"}
    # results = fetch_filtered_data(supabase_url, supabase_key, table_name, filters)
    filters = {"equipID": entryEquipID, 'date': todayCentral}
    results = fetch_filtered_data(supabase_url, supabase_key, "Equipment_GPS_All_Data", filters)

    #=========================================
    #Iterating through our list of values from our database and determining the highest/lowest hour readings to calculate our total hours for this date/equipment:
    lowestHourReading = 5000000 #Putting this as an absurdly high number so that the first hour reading becomes the lowest
    highestHourReading = 0
    locationList = []

    for j in range(len(results)):
        #Calculating the min/max hour readings:
        if results[j][10]!=None:
            entryHourReading = float(results[j][10])
        else:
            entryHourReading = 0

        if entryHourReading>highestHourReading:
            highestHourReading=entryHourReading
        if entryHourReading<lowestHourReading:
            lowestHourReading=entryHourReading

        #Updating our location GPS coordinate list for this equipment/date:
        thisLat = results[j][6]
        thisLong = results[j][7]

        locationList.append([thisLat, thisLong])
    
    #=========================================
    #Using our min/max hour readings to calculate the total hours that this equipment ran on this date:
    totalEquipHours = highestHourReading-lowestHourReading


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


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our equipment hour data, and updating our database>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION

start_time = time.time()


#==============================================================================================================================================================================================
#Pulling the Heavy Job Equipment data from the HCSS API and updating our "Equipment GPS All Data" database
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
#Creating a dictionary of values that converts the equipment IDs shown in Heavy Job to the standard IDs defined in our "Master Equipment List" smartsheet:

MySheet = smart.Sheets.get_sheet('1336754816634756')

heavyJobEquipIDconversionDict = {}

for MyRow in MySheet.rows:
    heavyJobEquipID = MyRow.cells[14].value
    masterListEquipID = MyRow.cells[0].value

    if heavyJobEquipID!=None:
        heavyJobEquipIDconversionDict[heavyJobEquipID]=masterListEquipID


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
            #Converting our heavy job equipment ID to the standard equipment ID defined in the "Master Equipment List" smartsheet using our dictionary created above:
            #heavyJobEquipIDconversionDict[heavyJobEquipID]=masterListEquipID

            if equipmentCode in heavyJobEquipIDconversionDict:
                equipmentCode=heavyJobEquipIDconversionDict[equipmentCode]
            

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



#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")

#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Updating HCSS With Equipment IDs from the Master Equipment List>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION



#endregion



