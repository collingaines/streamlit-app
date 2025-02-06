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


from datetime import datetime

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


time = get_current_time()


#========================================
#Inserting data into our "test" table:
def insert_data(data: dict):
    response = supabase_client.table('test').insert(data).execute()
    return response

data_to_insert = {
    'id':3,
    'test':str(time)
}

insert_response = insert_data(data_to_insert)



#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Smartsheet Equipment Inspection Sheet Info>')
print('<========================================================================================================================>')
print('Connecting to the Smartsheet API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION

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

#Importing the Smartsheet library so that I can interact with it's API:
#SMARTSHEET API TOKEN (Collin's Application) ==> gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1
import smartsheet
import logging

#Initialize client. Uses the API token in the environment variable "SMARTSHEET_ACCESS_TOKEN"
smart = smartsheet.Smartsheet('gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1')

#Make sure we don't miss any errors:
smart.errors_as_exceptions(True)

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
    date = MyRow.cells[2].value
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
    if date==None:
        dateFormatted = 'None Found'
    else:
        year = '20'+str(date)[6:8]
        month = str(date)[0:2]
        day = str(date)[3:5]

        dateFormatted = year+'-'+month+'-'+day

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
            'date':dateFormatted,
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

    

#endregion

#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Updating Smartsheet Equipment Inspection Dropdown Data>')
print('<========================================================================================================================>')
print('Connecting to the Smartsheet API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION

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

    


#==========================================================================================================================================================
#Next, let's navigate to our equipment inspection sheet and update the list of dropdown values:
#TEMPORARY: THIS SCRIPT WILL UPDATE A DROPDOWN ON THE MASTER LIST AS A TEST

# Step 1: Get the list of columns and find the dropdown column ID
columns = smart.Sheets.get_sheet('1336754816634756').columns
dropdown_column = next((col for col in columns if col.title == "TEST"), None)

if not dropdown_column:
    print(f"Column '{"TEST"}' not found!")
    exit()

COLUMN_ID = dropdown_column.id  # Store the column ID
current_options = dropdown_column.options  # Get existing dropdown options

# Step 2: Add new options to the dropdown list
new_options = ["New Option 1", "New Option 2"]  # Replace with your items
updated_options = list(set(current_options + new_options))  # Ensure unique values

# Step 3: Update the column with new options
updated_column = smartsheet.models.Column({
    "id": COLUMN_ID,
    "options": updated_options
})

response = smart.Sheets.update_column('1336754816634756', COLUMN_ID, updated_column)

print(f"Updated Dropdown List: {updated_options}")





#==========================================================================================================================================================
# import smartsheet

# # Initialize Smartsheet client with your API token
# API_TOKEN = 'gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1'
# SHEET_ID = 123456789  # Replace with your actual sheet ID
# COLUMN_NAME = "Your Dropdown Column"  # Replace with your actual column name

# # Initialize Smartsheet client
# smartsheet_client = smartsheet.Smartsheet(API_TOKEN)

# # Step 1: Get the list of columns and find the dropdown column ID
# columns = smartsheet_client.Sheets.get_sheet(SHEET_ID).columns
# dropdown_column = next((col for col in columns if col.title == COLUMN_NAME), None)

# if not dropdown_column:
#     print(f"Column '{COLUMN_NAME}' not found!")
#     exit()

# COLUMN_ID = dropdown_column.id  # Store the column ID
# current_options = dropdown_column.options  # Get existing dropdown options

# # Step 2: Add new options to the dropdown list
# new_options = ["New Option 1", "New Option 2"]  # Replace with your items
# updated_options = list(set(current_options + new_options))  # Ensure unique values

# # Step 3: Update the column with new options
# updated_column = smartsheet.models.Column({
#     "id": COLUMN_ID,
#     "options": updated_options
# })

# response = smartsheet_client.Sheets.update_column(SHEET_ID, COLUMN_ID, updated_column)

# print(f"Updated Dropdown List: {updated_options}")






#endregion