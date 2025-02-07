#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #0 | IMPORTING OUR PYTHON LIBRARIES: 
#region CLICK HERE TO EXPAND SECTION

#===============================================================================================================================================================
#Importing misc libraries
#region

import streamlit as st
import pandas as pd
import numpy as np
from streamlit_cookies_manager import EncryptedCookieManager
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from datetime import datetime

#endregion

#===============================================================================================================================================================
#Importing our libraries for our AgGrid table:
#region

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

from openpyxl import Workbook
import io

#endregion

#===============================================================================================================================================================
#Setting up our Supabase cloud database connection, logging in, AND creating some functions to use to access the data:
#region

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


#endregion

#===============================================================================================================================================================
#Generating our access token for the HCSS API:
#region

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

#endregion





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

    

#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Updating Smartsheet Equipment Inspection & Fuel Log Dropdown Data>')
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

print(f"Updated Dropdown List: {new_options}")

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

print(f"Updated Dropdown List: {new_options}")

#endregion



#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our project data, and updating our database and smartsheet "Master Project Info List">')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION


#==========================================================================================================================
#Creating a list of timecard values for use later in calculating the timecard values for each foreman:
#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/heavyjob/api/v1/jobs"

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
        #"startDate": "2021-01-01T00:00:00Z",
        #"endDate": endDate
        # "modifiedSince": "2019-08-24T14:15:22Z",
        # "cursor": "string",
         "limit": "1000000"
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

#============================================================================
#Deleting all existing entries in our Supabase "Cost_Code_Classifiers" database table:
def truncate_table(supabase_url: str, supabase_key: str, table_name: str):
    # Create a Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
                            
    # Truncate the specified table
    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()
                            
truncate_table(supabase_url, supabase_key, 'Master_Project_Information')
        
#============================================================================
#Function to insert data into the "Cost_Code_Classifiers" table
def insert_data(data: dict):
    response = supabase_client.table('Master_Project_Information').insert(data).execute()
    return response

#============================================================================
#Inserting the data into our Supabase database table:
rowcount = 1

for i in range(len(projectInfoList)):

    data_to_insert = {
        'id':rowcount,
        'jobNum':projectInfoList[i][2],
        'jobDescription':projectInfoList[i][3],
        'creationDate':projectInfoList[i][4],
        'jobStatus':projectInfoList[i][5],
        'lattitude':projectInfoList[i][6],
        'longitude':projectInfoList[i][7],
        'address1':projectInfoList[i][8],
        'address2':projectInfoList[i][9],
        'city':projectInfoList[i][10],
        'state':projectInfoList[i][11],
        'zip':projectInfoList[i][12],
        'projectManager':'',
        'projectSuperintendent':'',
        'startDate':'',
        'endDate':'',
        'hcssAPIid':projectInfoList[i][0],
        'legacyID':projectInfoList[i][1]

    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)





#endregion



#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our timecard data, and updating our database>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION


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




# def batch_update(table_name, data, batch_size=1000):
#     for i in range(0, len(data), batch_size):
#         batch = data[i : i + batch_size]
#         response = supabase.table(table_name).upsert(batch).execute()
#         print(f"Batch {i//batch_size + 1} inserted, status: {response}")

# batch_update("Master_Timecard_Information", dataList)






#endregion



#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our GPS hour/location data, and updating our database>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION


#==============================================================================================================================================================================================
#Pulling the GPS data from the HCSS API and updating our "Equipment GPS All Data" database

print('PULLING EQUIPMENT GPS DATA FROM API AND UPDATING DATABASE')
#==========================================================================================================================
#Creating a list of timecard values for use later in calculating the timecard values for each foreman:
#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/telematics/api/v1/equipment"


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

#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.get(HCSS_API_ENDPOINT, headers=HEADERS, params=query)

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

        equipmentInfoList.append([equipmentHCSSAPIid, equipID, equipDescription, fuelUom, lastBearing, lastLatitude, lastLongitude, lastLocationDateTime, lastHourMeterReadingInSeconds, lastHourMeterReadingInHours, lastHourReadingDateTime])


#=======================================================================================================================================
#Next, let's update our "Equipment_GPS_All_Data" database:
#=========================================
#Creating a variable for "today" that is in US Central time because haevy job uses UTC which can have wrong date late in the day!
from datetime import datetime
import pytz

def get_central_time():
    central_tz = pytz.timezone('America/Chicago')  # US Central Time Zone
    central_time = datetime.now(central_tz)  # Get current time in Central Time
    return central_time.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD

todayCentral=str(get_central_time())[0:10]

#============================================================================
#First let's calculate what the starting ID value shoudl be so we don't run into any primary key database issues:

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

    data_to_insert = {
        'id':rowcount,
        'date':todayCentral,
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
        'lastHourReadingDateTime':equipmentInfoList[i][10]


    }

    rowcount=rowcount+1

    #============================================================================
    #Using the "insert_data" function defined at the top of this script
    insert_response = insert_data(data_to_insert)


print('=====')
print('=====')
print('DONE')
#==============================================================================================================================================================================================
#Next, let's perform our calculations for the location/hours that each piece of equipment ran has run so far today:

print('CREATING A LIST OF ALL EQUIPMENT/DATES')

#=========================================
#Creating a variable for today's date:
from datetime import datetime

def get_current_datetime():
    now = datetime.utcnow()
    formatted_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_datetime

today = str(get_current_datetime())[0:10]

#============================================================================
#First, let's make a list of all equipment entries currently in our "Equipment_GPS_All_Data" table for TODAY'S DATE:
equipmentInfoTodayList = []

#=========================================
#Using our "etch_filtered_data" function defined at the top of this script to pull all entries for this equip ID:
# filters = {"column1": "value1", "column2": "value2"}
# results = fetch_filtered_data(supabase_url, supabase_key, table_name, filters)
filters = {'date': todayCentral}
data = fetch_filtered_data(supabase_url, supabase_key, "Equipment_GPS_All_Data", filters)

#=========================================
#Iterating through our list of database values and updating our dictionary: 
for i in range(len(data)):
    entryEquipID = data[i][3]
    equipDescr = data[i][4]

    equipmentInfoTodayList.append([entryEquipID, equipDescr])


#=========================================
#Accessing our project latitude/longitude coordinates by pulling from our "Master_Project_Information" table:
projectData = fetch_data_from_table("Master_Project_Information")

projectCoordinateDict = {}

for j in range(len(projectData)):
    jobNum = projectData[j][1]
    jobDesc = projectData[j][2]
    lat = projectData[j][5]
    long = projectData[j][6]

    projectCoordinateDict[(jobNum, jobDesc)]=[lat, long]




print('=====')
print('=====')
print('DONE')
#============================================================================
#Next, let's iterate through our list created above and calculate the total hours and location for each:



print('CALCULATING THE LOCATOIN AND TOTAL HOURS OF EACH PIECE OF EQUIPMENT')
equipmentInfoDictionary = {}

for i in range(len(equipmentInfoTodayList)):

    entryEquipID = equipmentInfoTodayList[i][0]
    equipDescript = equipmentInfoTodayList[i][1]

    #=========================================
    #Using our "etch_filtered_data" function defined at the top of this script to pull all entries for this equip ID:
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
        entryHourReading = float(results[j][11])

        if entryHourReading>highestHourReading:
            highestHourReading=entryHourReading
        if entryHourReading<lowestHourReading:
            lowestHourReading=entryHourReading

        #Updating our location GPS coordinate list for this equipment/date:
        thisLat = results[j][7]
        thisLong = results[j][8]

        locationList.append([thisLat, thisLong])
    
    #=========================================
    #Using our min/max hour readings to calculate the total hours that this equipment ran on this date:
    totalEquipHours = highestHourReading-lowestHourReading

    #=========================================
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

    #Example usage:
    # latitude = 37.7749  # San Francisco, CA
    # longitude = -122.4194
    # radius = 3  # miles

    # bounds = get_lat_lng_bounds(latitude, longitude, radius)
    # print(bounds)

    #Example output:
    # {
    # 'min_lat': 37.7314, 
    # 'max_lat': 37.8184, 
    # 'min_lng': -122.4609, 
    # 'max_lng': -122.3779
    # }

    #=========================================
    #Iterating through our list of GPS coordinates, calculating which project each coordinate entry belongs to, and adding each project value to a list: 
    equipmentProjectList = []

    for j in range(len(locationList)):
        entryLat = float(locationList[j][0])
        entryLong = float(locationList[j][1])

        #projectCoordinateDict[(jobNum, jobDesc)]=[lat, long]
        for key,values in projectCoordinateDict.items():
            thisJobNum = key[0]
            thisJobDesc = key[1]
            thisJobValue = thisJobNum+'-'+thisJobDesc

            if values[0]!=None and values[1]!=None:
                projectLat = float(values[0])
                projectLong = float(values[1])
            else:
                projectLat = 0
                projectLong = 0

            #Calculating our lat/long max/min ranges using our function defined above: 
            coordinateMaxMins = get_lat_lng_bounds(projectLat, projectLong, radius_miles=3)
            min_lat = coordinateMaxMins.get('min_lat')
            max_lat = coordinateMaxMins.get('max_lat')
            min_lng = coordinateMaxMins.get('min_lng')
            max_lng = coordinateMaxMins.get('max_lng')

            if projectLat>=min_lat and projectLat<=max_lat:
                if projectLong>=min_lng and projectLong<=max_lng:
                    equipmentProjectList.append(thisJobValue)


        
    #=========================================
    #Lastly, identifying the most frequently occuring project location in our list to determine the location of this equipment for this date: 
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
    
    project = most_frequent(equipmentProjectList)

    
    #=========================================
    #Updating our dictionary of values to be entered into our database:
    equipmentInfoDictionary[(entryEquipID, todayCentral, equipDescript)] = [totalEquipHours, project]


print('=====')
print('=====')
print('DONE')
#==============================================================================================================================================================================================
#Next, let's enter the values above into our "Master Equipment GPS Data" database



print('UPDATING OUR DATABASE')
#============================================================================
#First, let's delete any rows in this table that are for our current date
result = delete_rows_by_value(supabase_url, supabase_key, "Master_Equipment_GPS_Data", "date", todayCentral)
print(result)


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




print('=====')
print('=====')
print('DONE')


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Connecting to the HCSS API, pulling all of our equipment hour data, and updating our database>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('<Updating HCSS With Equipment IDs from the Master Equipment List>')
print('<========================================================================================================================>')
print('Connecting to the HCSS API and pulling data from the "Equipment Master List" sheet...')
#region CLICK HERE TO EXPAND THIS SECTION


#endregion



