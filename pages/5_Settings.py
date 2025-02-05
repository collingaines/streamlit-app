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


#===============================================================================================================================================================
#Connecting to our Pyramid Analytics database
#os.chdir('C:\\Users\\colli\\AppData\\Local\\Programs\\Python\\Python310\\My_Python_Scripts\\Main_App_Folder_2025\\streamlit_app')
conn = sqlite3.connect('Pyramid_Analytics_Database.db')
c = conn.cursor()

#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #1 | SETTING UP THE PAGE CONFIGURATIONS & COOKIE MANAGER: 
#region CLICK HERE TO EXPAND SECTION

#============================================================================================================================================================
#Setting page configurations:
st.set_page_config(
    #Web browser tab title and logo:
    page_title="Pyramid Construction Analytics",
    page_icon="static/Main_Logo.jpg",

    #App page layout:
    layout="wide",  # Choose "centered" or "wide"
    initial_sidebar_state="expanded"  # Sidebar default state
    
)



#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #2 | DEFINING CTC PERIODS AND FUNCTIONS TO BE USED LATER IN THE SCRIPT: 
#region CLICK HERE TO EXPAND SECTION

#============================================================================================================================================================
#Creating/initializing a cookie manager
cookies = EncryptedCookieManager(
    prefix="my_app",  # Optional: adds a prefix to all cookies for namespacing
    password="my_secret_password"  # Change this to a strong password
)

#Initialize the cookie manager
if not cookies.ready():
    st.stop()

#============================================================================================================================================================
#Number formatter for displaying comma delineated numbers:
def format_with_commas(number):
    """
    Formats a number as a string with commas as thousand separators.
    Args:
        number (int or float): The number to be formatted.
    Returns:
        str: The formatted number as a string.
    """
    try:
        return f"{number:,}"
    except (ValueError, TypeError):
        return "Invalid input: Please provide a valid number."

#============================================================================================================================================================
#Pandas dataframe creator. Streamlit likes to have table data supplied in the pandas dataframe format, so this function will take in column headers/data values and turn it into a pandas dataframe:
def create_dataframe(column_headers, data_values):
    """
    Creates a DataFrame from the given column headers and data values.

    Args:
        column_headers (list): A list of column headers.
        data_values (list of lists): A list containing lists of data values for each row.

    Returns:
        pd.DataFrame: A pandas DataFrame created from the provided headers and data.
    """
    try:
        if not isinstance(column_headers, list) or not all(isinstance(col, str) for col in column_headers):
            raise ValueError("Column headers must be a list of strings.")
        
        if not isinstance(data_values, list) or not all(isinstance(row, list) for row in data_values):
            raise ValueError("Data values must be a list of lists.")

        # Create the DataFrame
        dataframe = pd.DataFrame(data_values, columns=column_headers)
        return dataframe
    
    except Exception as e:
        print(f"Error: {e}")
        return None

#============================================================================================================================================================
# Create a function to generate the Excel file and allow users to download
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data



#============================================================================================================================================================
#Defining some CTC period info: 

#=======================================================
#Querying our "Master_Bonus_Period_Data" database table where all bonus/ctc period data is stored:
bonusPeriodQuery = c.execute("SELECT * FROM Master_Bonus_Period_Data")
bonusPeriodValues = c.fetchall()


#=======================================================
#Creating a dictionary of all start/end dates for each bonus period
bonusPeriodDateRangeDictionary = {}

for i in range(len(bonusPeriodValues)):
    periodType = bonusPeriodValues[i][2]

    if periodType=='Bonus Period':
        periodName = bonusPeriodValues[i][3]
        startDate = bonusPeriodValues[i][4]
        endDate = bonusPeriodValues[i][5]

        startDateDT = datetime.datetime(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10]))
        endDateDT = datetime.datetime(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))
    
        bonusPeriodDateRangeDictionary[periodName]=[startDateDT, endDateDT]


#=======================================================
#Creating a dictionary of all the CTC Period cutoff dates:
CTCcutoffDictionary = {}

for i in range(len(bonusPeriodValues)):
    periodType = bonusPeriodValues[i][2]

    if periodType=='CTC Period':
        periodName = bonusPeriodValues[i][3]
        startDate = bonusPeriodValues[i][4]
        endDate = bonusPeriodValues[i][5]

        startDateDT = datetime.datetime(int(startDate[0:4]),int(startDate[5:7]),int(startDate[8:10]))
        endDateDT = datetime.datetime(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))
    
        CTCcutoffDictionary[periodName]=[startDateDT, endDateDT]





#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #3 | SETTING UP THE SIDEBAR:
#region CLICK HERE TO EXPAND SECTION

# Add the custom logo to the sidebar
#st.sidebar.image("static/Main_Logo_With_Name.jpg", width=275)


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #4 | BUILDING OUT OUR USER PAGES:

#============================================================================================================================================================
#Using our "userPosition" variable assigned on our login page to determine the page we want to generate: 

#FIRST, pulling our userPosition variable value from our cookies: 
try:
    userPosition=cookies['userPosition']
except: 
    userPosition=None


#============================================================================================================================================================
#Using a "if/else" statement to return an error message if the user isn't logged in yet:
if userPosition!=None: 
    #================================================================================================================================================================================================================================================================================================================
    #================================================================================================================================================================================================================================================================================================================
    #OPERATIONS MANAGER BONUS PAGE: 
    if userPosition=='Operations Manager':
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION A | Title Section:
        #region CLICK HERE TO EXPAND SECTION 
        st.title('System Settings')


        st.markdown(
            """
            A portal for viewing and editting settings that control various functions of the Pyramid Analytics application.
        """
        )
        st.divider()

        #endregion
        
        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION B | Filter section:
        #region CLICK HERE TO EXPAND SECTION

        #==============================================================================================================================
        # Inject custom CSS
        st.markdown(
            """
            <style>
            .small-selectbox .stSelectbox {
                font-size: 12px;  /* Adjust the font size */
                height: 30px;     /* Adjust the height */
                width: 150px;     /* Adjust the width */
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


        st.subheader("Select a Setting Module To View/Edit:")

        #==============================================================================================================================
        #Creating our columns to split our filter section into 2 halves:
        col1, col2, col3 = st.columns(3)


        #==============================================================================================================================
        #"Select a Report Type" Dropdown menu:
        #region

        #"Report Type" Dropdown menu: 
        with col1: 
            #===========
            #Bonus period selectbox:
            settingType = st.selectbox(
            "Select a Setting Type",
            ("Cost Code Classifiers",
             "Bonus Value Settings",
             "Equipment Info Settings"
             ),
            index=None,
            placeholder="Select setting type...",
            )
        
        #endregion

        st.divider()


        #endregion

        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION C | If the "Cost Code Classifer" setting is selected:
        #region CLICK HERE TO EXPAND SECTION
        
        if settingType=='Cost Code Classifiers':
            st.markdown("# *Cost Code Classifiers*")
            
            st.markdown("")
            st.markdown("")

            #===========================================================================
            #Creating our dataframe:
            #region

            #=================================
            #Pulling our vlaues from our supabase database table using the "fetch_data_from_table" function defined at the top of this page:
            data = fetch_data_from_table("Cost_Code_Classifiers")

            #=================================
            #Removing the index from our nested list of data returned by the function above:
            data_values = []

            for i in range(len(data)):
                data_values.append([data[i][1], data[i][2], data[i][3], data[i][4], data[i][5], data[i][6], data[i][7], data[i][8], data[i][9], data[i][10], data[i][11], data[i][12], data[i][13], data[i][14], data[i][15]])


            #=================================
            #Defining column header labels for table and updating our dataframe with our data calculated above: 
            column_headers = ['Cost Code', 'Cost Code Description', 'Trade', 'Cost Code Classifier', 'Alternate Trade', 'Trade PF Cap', 'Foreman PF Cap', 'Project PF Cap', 'Trade Force PF', 'Foreman Force PF', 'Project Force PF', 'Omit From Trade (Y/N)', 'Omit From Foreman (Y/N)', 'Omit From Project (Y/N)', 'Notes']

            #=================================
            #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
            tradeSuperCostCodeData = create_dataframe(column_headers, data_values)

            df = tradeSuperCostCodeData

            #endregion


            #===========================================================================
            #Creating our AgGrid table:
            #region

            gb = GridOptionsBuilder.from_dataframe(df)

            #For formatting cells red/green that are above/below 0: 
            cell_style_jscode = JsCode("""
                function(params) {
                    if (params.value < 0) {
                        return {'color': 'black', 'backgroundColor': '#e1dfdf'};
                    } else if (params.value > 0) {
                        return {'color': 'black', 'backgroundColor': '#e1dfdf'};
                    } else {
                        return null;
                    }
                }
                """)
            
            
            #=================================
            #Applying the $ formatting AND red/green cell coloring to specified columns:
            for column in ['Trade PF Cap', 'Foreman PF Cap', 'Project PF Cap', 'Trade Force PF', 'Foreman Force PF', 'Project Force PF', 'Omit From Trade (Y/N)', 'Omit From Foreman (Y/N)', 'Omit From Project (Y/N)']:
                gb.configure_column(
                    column,
                    type=["numericColumn"],
                    #valueFormatter="x.toLocaleString('en-US', {style: 'currency', currency: 'USD', minimumFractionDigits: 2})",
                    cellStyle=cell_style_jscode,  # Use JS code for cell styling
                )

            #=================================
            #Setting columns to default be pinned to the left:
            gb.configure_column("Cost Code", pinned="left")
            gb.configure_column("Cost Code Description", pinned="left")
            gb.configure_column("Trade", pinned="left")
            gb.configure_column("Cost Code Classifier", pinned="left")

            #=================================
            #Configuring table to allow for column filtering:
            gb.configure_default_column(filter=True)  # Enable filtering globally

            gb.configure_default_column(editable=True)  # Make all columns editable
            gb.configure_selection("single", use_checkbox=True)  # Optional: Row selection


            #=================================
            #Configuring columns where we want info to be centered in the cell
            gb.configure_column("Trade PF Cap", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Foreman PF Cap", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Project PF Cap", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Trade Force PF", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Foreman Force PF", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Project Force PF", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Omit From Trade (Y/N)", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Omit From Foreman (Y/N)", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})
            gb.configure_column("Omit From Project (Y/N)", cellStyle={'textAlign': 'center', 'justifyContent': 'center', 'display': 'flex'})


            #=================================
            # Render the table
            grid_options = gb.build()
            # st.subheader("Cost Code Classifiers")
            grid_response = AgGrid(
                tradeSuperCostCodeData,
                gridOptions=grid_options,
                enable_enterprise_modules=True,
                height=750,
                theme="streamlit",
                # fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,  # Enable unsafe JS code
                update_mode=GridUpdateMode.VALUE_CHANGED,  # Capture cell edits
            )

            #endregion


            #===========================================================================
            #Creating our excel download button!
            #region

            excel_file = to_excel(tradeSuperCostCodeData)
            st.download_button(
                label="Download Data to Excel",
                data=excel_file,
                file_name="Cost Code Classifiers.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            #endregion


            #===========================================================================
            #Formatting our "Submit Changes" button: 
            #region

            st.markdown("""
                <style>
                [data-testid="stButton"] > button {
                    width: 300px;
                    height: 75px;
                    background-color: #02ab21;  /* Green background color */
                    color: black;  /* Text color */
                    
                }
                .stButton > button p {
                         font-size: 24px !important;
                         font-weight: bold;
                     }
                [data-testid="stButton"] > button:hover {
                    background-color: purple;  /* Change color on hover */
                    color: white;
                }
                </style>
            """, unsafe_allow_html=True)

            #endregion


            #===========================================================================
            #If the "Submit Changes" button is clicked, then we want to update our database
            if st.button("Submit Changes"):
                #========================================
                #Capture edited data
                updated_data = grid_response["data"]

                #========================================
                #Converting our dataframe to a list of tuples for SQLite
                updated_values = [tuple(row) for row in updated_data.to_numpy()]  # Convert DataFrame to list of tuples

                #========================================
                #Deleting all existing entries in our Supabase "Cost_Code_Classifiers" database table:
                def truncate_table(supabase_url: str, supabase_key: str, table_name: str):
                    # Create a Supabase client
                    supabase: Client = create_client(supabase_url, supabase_key)
                            
                    # Truncate the specified table
                    response = supabase.rpc('truncate_table', {'table_name': table_name}).execute()
                            
                truncate_table(supabase_url, supabase_key, 'Cost_Code_Classifiers')

                #========================================
                #Creating our progress bar: 
                # Create a progress bar
                progress_bar = st.progress(0)

                # Create a status text to show the current progress
                status_text = st.empty()

                #========================================
                #Function to insert data into the "Cost_Code_Classifiers" table
                def insert_data(data: dict):
                    response = supabase_client.table('Cost_Code_Classifiers').insert(data).execute()
                    return response

                #========================================
                #Inserting the data into our Supabase database table:
                rowcount=1

                for i in range(len(updated_values)):
                    data_to_insert = {
                        'id':rowcount,
                        'costCode':updated_values[i][0],
                        'ccDescription':updated_values[i][1],
                        'trade':updated_values[i][2],
                        'ccClassifier':updated_values[i][3],
                        'alternateTrade':updated_values[i][4],
                        'tradePFcap':updated_values[i][5],
                        'foremanPFcap':updated_values[i][6],
                        'projectPFcap':updated_values[i][7],
                        'tradeForcePF':updated_values[i][8],
                        'foremanForcePF':updated_values[i][9],
                        'projectForcePF':updated_values[i][10],
                        'omitFromTrade':updated_values[i][11],
                        'omitFromForeman':updated_values[i][12],
                        'omitFromProject':updated_values[i][13],
                        'notes':updated_values[i][14]
                    }

                    rowcount=rowcount+1

                    insert_response = insert_data(data_to_insert)

                    #=================
                    # Update the progress bar
                    progress = (i + 1) / len(updated_values)
                    progress_bar.progress(progress)
                            
                    # Update the status text
                    status_text.text(f"Processed {i+1}/{len(updated_values)} items")

                #========================================
                #Printing a success response once the database has been updated successfully:
                st.success("Data updated successfully!")



        #endregion


        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION E | REPORT: Bonus Report - Foremen:
        #region CLICK HERE TO EXPAND SECTION
        
        elif settingType=='Bonus Value Settings':
            st.markdown("# *Bonus Values (Base PF, Earn Rate, etc.)*")
            
            st.markdown("")
            st.markdown("")

            bonusValueQuery = c.execute("SELECT * FROM Master_Bonus_Settings")
            bonusValueValues = c.fetchall()

            data_values = []

            for i in range(len(bonusValueValues)):
                data_values.append([bonusValueValues[i][1], bonusValueValues[i][2], bonusValueValues[i][3], bonusValueValues[i][4], bonusValueValues[i][5], bonusValueValues[i][6], bonusValueValues[i][7]])

            
            #===========================================================================
            #Creating our dataframe:

            #=================================
            #Defining column header labels for table and updating our dataframe with our data calculated above: 
            column_headers = ['Position', 'Trade', 'Cost Code Type', 'Base PF (Floor)', 'Base PF (Ceiling)', 'Bonus Earn Rate', 'Position Trade Pool Share']

            #=================================
            #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
            tradeSuperCostCodeData = create_dataframe(column_headers, data_values)

            df = tradeSuperCostCodeData

            #===========================================================================
            # Create AgGrid options
            gb = GridOptionsBuilder.from_dataframe(df)


            #===========================================================================
            #Setting columns to default be pinned to the left:
            gb.configure_column("Position", pinned="left")
            

            #===========================================================================
            #Configuring table to allow for column filtering:
            gb.configure_default_column(filter=True)  # Enable filtering globally

            gb.configure_default_column(editable=True)  # Make all columns editable
            gb.configure_selection("single", use_checkbox=True)  # Optional: Row selection

            #===========================================================================
            # Render the table
            grid_options = gb.build()
            # st.subheader("Cost Code Classifiers")
            grid_response = AgGrid(
                tradeSuperCostCodeData,
                gridOptions=grid_options,
                enable_enterprise_modules=True,
                height=550,
                theme="streamlit",
                #fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,  # Enable unsafe JS code
                update_mode=GridUpdateMode.VALUE_CHANGED,  # Capture cell edits
            )

            #===========================================================================
            #Creating our excel download button!
            excel_file = to_excel(tradeSuperCostCodeData)
            st.download_button(
                label="Download Data to Excel",
                data=excel_file,
                file_name="Bonus Values.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


            #===========================================================================
            #Capture edited data
            updated_data = grid_response["data"]


            #===========================================================================
            #Creating our submit button and updating our classifier database when clicked:

            #==============================
            #Formatting our button: 
            st.markdown("""
                <style>
                [data-testid="stButton"] > button {
                    width: 300px;
                    height: 75px;
                    background-color: #02ab21;  /* Green background color */
                    color: black;  /* Text color */
                    
                }
                .stButton > button p {
                         font-size: 24px !important;
                         font-weight: bold;
                     }
                [data-testid="stButton"] > button:hover {
                    background-color: purple;  /* Change color on hover */
                    color: white;
                }
                </style>
            """, unsafe_allow_html=True)

            #==============================
            #If the "Submit Changes" button is clicked, then we want to update our database
            if st.button("Submit Changes"):
                
                #==========
                #Convert to list of tuples for SQLite
                updated_values = [tuple(row) for row in updated_data.to_numpy()]  # Convert DataFrame to list of tuples


                #==========
                #Supabase database password: 5Nw$sLg.wpj68wQ


                #==========
                #Progress bar: 
                # Create a progress bar
                progress_bar = st.progress(0)

                # Create a status text to show the current progress
                status_text = st.empty()





                #==========
                #Let's delete all previous data from the database:
                def deleteMultipleRecords():
                    c.execute("DELETE from Cost_Code_Classifiers")
                    conn.commit()

                deleteMultipleRecords()

                #==========
                #Updating our database:
                rowcount=1

                for i in range(len(updated_values)):
                    c.execute("INSERT INTO Cost_Code_Classifiers VALUES(:id, :costCode, :ccDescription, :trade, :ccClassifier, :alternateTrade, :tradePFcap, :foremanPFcap, :projectPFcap, :tradeForcePF, :foremanForcePF, :projectForcePF, :omitFromTrade, :omitFromForeman, :omitFromProject, :notes)",
                            {
                            'id':rowcount,
                            'costCode':updated_values[i][0],
                            'ccDescription':updated_values[i][1],
                            'trade':updated_values[i][2],
                            'ccClassifier':updated_values[i][3],
                            'alternateTrade':updated_values[i][4],
                            'tradePFcap':updated_values[i][5],
                            'foremanPFcap':updated_values[i][6],
                            'projectPFcap':updated_values[i][7],
                            'tradeForcePF':updated_values[i][8],
                            'foremanForcePF':updated_values[i][9],
                            'projectForcePF':updated_values[i][10],
                            'omitFromTrade':updated_values[i][11],
                            'omitFromForeman':updated_values[i][12],
                            'omitFromProject':updated_values[i][13],
                            'notes':updated_values[i][14]
                            })

                    rowcount=rowcount+1
                    conn.commit()

                    # Update the progress bar
                    progress = (i + 1) / len(updated_values)
                    progress_bar.progress(progress)
                    
                    # Update the status text
                    status_text.text(f"Processed {i+1}/{len(updated_values)} items")

                #==============================
                #Printing a success response once the data has been updated successfully:
                st.success("Data updated successfully!")

        #endregion


        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION F | REPORT: Bonus Report - ProjectTrade Pool:
        #region CLICK HERE TO EXPAND SECTION

        elif settingType=='Bonus Report - Project Trade Pool':         
           pass
        
        #endregion


        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION G | NO REPORT SELECTED:
        #region
        else:
            #If no valid report has been selected yet, we will want to display a yellow warning message indicating that they need to select a valid filter to see a report
            st.warning("Select a setting type from the dropdown menu above to display setting details!")

        #endregion


    #================================================================================================================================================================================================================================================================================================================
    #================================================================================================================================================================================================================================================================================================================
    #PROJECT CONTROLLS MANAGER BONUS PAGE:
    if userPosition=='Project Controls Manager':
        pass
    


    #================================================================================================================================================================================================================================================================================================================
    #================================================================================================================================================================================================================================================================================================================
    #PRESIDENT BONUS PAGE:
    if userPosition=='President':
        pass
    


    #================================================================================================================================================================================================================================================================================================================
    #================================================================================================================================================================================================================================================================================================================
    #TRADE SUPERINTENDENT BONUS PAGE:
    if userPosition=='Trade Superintendent':
        pass
    


    #================================================================================================================================================================================================================================================================================================================
    #================================================================================================================================================================================================================================================================================================================
    #FOREMAN BONUS PAGE:
    if userPosition=='Foreman':
        pass



    #================================================================================================================================================================================================================================================================================================================
    #================================================================================================================================================================================================================================================================================================================
    #EQUIPMENT MANAGER BONUS PAGE:
    if userPosition=='Equipment Manager':
        pass



#============================================================================================================================================================
#Using a "try/except block to return an error message if the user isn't logged in yet"
else:
    st.error("You must be logged in to access this page! Please return to the Home Page and login.")


