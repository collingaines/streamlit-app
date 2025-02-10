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


#SMARTSHEET API TOKEN (Collin's Application) ==> gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1
import smartsheet
import logging

#Initialize client. Uses the API token in the environment variable "SMARTSHEET_ACCESS_TOKEN"
smart = smartsheet.Smartsheet('gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1')

#Make sure we don't miss any errors:
smart.errors_as_exceptions(True)

#==============================================================================================================================================================================================
#Pulling the GPS data from the HCSS API and updating our "Equipment GPS All Data" database

print('PULLING EQUIPMENT GPS DATA FROM API AND UPDATING DATABASE')
#==========================================================================================================================
#Creating a list of timecard values for use later in calculating the timecard values for each foreman:

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


#==============================================================================================================================================================================================

#============================================
#First, let's make a list of all equipment IDs that we want to track data for:
#Creating a sheet object for the smartsheet that we want to read data from, and passing it the sheet id which can be found by looking on the sheet properties on smartsheet (File>Properties>Sheet ID:)
equipIDList = []

MySheet = smart.Sheets.get_sheet('1336754816634756')


for MyRow in MySheet.rows:
    #============================================================================
    #Defining some initial values that will be pulled straight from the smartsheet: 
    equipmentID = MyRow.cells[0].value
    status = MyRow.cells[7].value

    if status=='Active':
        equipIDList.append(equipmentID)


#============================================
#Next, let's create a variable that includes today's date in US central time:

from datetime import datetime
import pytz

def get_central_time():
    central_tz = pytz.timezone('America/Chicago')  # US Central Time Zone
    central_time = datetime.now(central_tz)  # Get current time in Central Time
    return central_time.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD

todayCentral=str(get_central_time())[0:10]


#============================================
#Next, let's iterate through our list of equipment created above and pull the E360 API data for each:

#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/e360/api/v1/equipment"

rowcount=1

for i in range(len(equipIDList)):
    entryID = equipIDList[i]

    #Listing any parameters here (typically won't use any, for some reason this has been giving me issues):
    query = {
            # "jobId": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            # "foremanId": APIID,
            # "employeeId": APIID,
            #"startDate": "2021-01-01T00:00:00Z",
            #"endDate": endDate
            # "modifiedSince": "2019-08-24T14:15:22Z",
            # "cursor": "string",
             "equipmentCode": entryID,
             "limit": "1000000"
    }

    response = requests.get(HCSS_API_ENDPOINT, headers=HEADERS, params=query)

    #A 200 response status code means that the request was successful! Thusly if this repsonse is returned, we will run our script:
    if response.status_code == 200:

        data = response.json()

        results = data.get('results')

        #Pulling all of our E360 values from our API call results and saving them to a variable:
        apiID = data.get("data")[0].get("id")
        equipmentID = data.get("data")[0].get("equipmentId")
        businessUnitID = data.get("data")[0].get("businessUnitId")
        code = data.get("data")[0].get("code")
        equipmentType = data.get("data")[0].get("equipmentType")
        description = data.get("data")[0].get("description")
        accountingCode = data.get("data")[0].get("accountingCode")
        make = data.get("data")[0].get("make")
        model = data.get("data")[0].get("model")
        year = data.get("data")[0].get("year")
        vin = data.get("data")[0].get("vin")
        serialNo = data.get("data")[0].get("serialNo")
        hourMeter = data.get("data")[0].get("hourMeter")
        hourMeterDate = data.get("data")[0].get("hourMeterDate")
        odometer = data.get("data")[0].get("odometer")
        enabled = data.get("data")[0].get("enabled")
        rentalFlag = data.get("data")[0].get("rentalFlag")
        jobCode = data.get("data")[0].get("jobCode")
        locationName = data.get("data")[0].get("locationName")

        #============================================================================
        #Function to insert data into the "Cost_Code_Classifiers" table
        def insert_data(data: dict):
            response = supabase_client.table('Master_Equipment_Asset_List').insert(data).execute()
            return response

        #============================================================================
        #Inserting the data into our Supabase database table:
        data_to_insert = {
                'id':rowcount,
                'date':todayCentral,
                'apiID':apiID,
                'equipmentID':equipmentID,
                'businessUnitID':businessUnitID,
                'code':code,
                'equipmentType':equipmentType,
                'description':description,
                'accountingCode':accountingCode,
                'make':make,
                'model':model,
                'year':year,
                'vin':vin,
                'serialNo':serialNo,
                'hourMeter':hourMeter,
                'hourMeterDate':hourMeterDate,
                'odometer':odometer,
                'enabled':enabled,
                'rentalFlag':rentalFlag,
                'jobCode':jobCode,
                'locationName':locationName

            }

        rowcount=rowcount+1

        #============================================================================
        #Using the "insert_data" function defined at the top of this script
        insert_response = insert_data(data_to_insert)

    else:
        print('Unable to retreive data for equipment: {}'.format(entryID))
    
    
