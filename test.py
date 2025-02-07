import streamlit as st

import numpy as np

import datetime

from datetime import datetime



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
        #print("An exception occurred:", str(e))
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

































#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================
#=================================================================================================================================================================================================================================================================================

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
    entryEquipID = data[i][2]
    equipDescr = data[i][3]

    equipmentInfoTodayList.append([entryEquipID, equipDescr])

print('equipmentInfoTodayList is {}'.format(equipmentInfoTodayList))
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

print('projectCoordinateDic is {}'.format(projectCoordinateDict))


print('=====')
print('=====')
print('DONE')
#============================================================================
#Next, let's iterate through our list created above and calculate the total hours and location for each:



print('CALCULATING THE LOCATION AND TOTAL HOURS OF EACH PIECE OF EQUIPMENT')
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
        if locationList[j][0]!=None and locationList[j][1]!=None:
            entryLat = float(locationList[j][0])
            entryLong = float(locationList[j][1])
        else:
            entryLat = 0
            entryLong = 0
            
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
























