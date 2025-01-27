import streamlit as st
import pandas as pd
import numpy as np
from streamlit_cookies_manager import EncryptedCookieManager
import datetime

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

#=================================================================
#Connecting to our Pyramid Analytics database
conn = sqlite3.connect('Pyramid_Analytics_Database.db')
c = conn.cursor()

#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
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



#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#SECTION #2 | DEFINING FUNCTIONS TO BE USED LATER IN THE SCRIPT: 
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
#Defining some CTC period info: 

#=======================================================
#Creating a dictionary of all start/end dates for each bonus period:
bonusPeriodDateRangeDictionary = {}

#=============
#Q1&2: 2024
endDateDT = datetime.datetime(int('2024'),int('05'),int('27'))
startDateDT = datetime.datetime(int('2024'),int('01'),int('01'))

bonusPeriodDateRangeDictionary['Q1&2: 2024']=[startDateDT, endDateDT]

#=============
#Q3&4: 2024
endDateDT = datetime.datetime(int('2024'),int('11'),int('24'))
startDateDT = datetime.datetime(int('2024'),int('05'),int('28'))

bonusPeriodDateRangeDictionary['Q3&4: 2024']=[startDateDT, endDateDT]

#=============
#Q1&2: 2025
endDateDT = datetime.datetime(int('2024'),int('05'),int('25'))
startDateDT = datetime.datetime(int('2024'),int('11'),int('25'))

bonusPeriodDateRangeDictionary['Q1&2: 2025']=[startDateDT, endDateDT]


#=======================================================
#==================================================================================
#Creating a dictionary of all the CTC Period cutoff dates:
CTCcutoffDictionary = {}

#November 2024:
endDateDT = datetime.datetime(int('2024'),int('11'),int('24'))
startDateDT = datetime.datetime(int('2024'),int('10'),int('28'))

CTCcutoffDictionary['November-2024']=[startDateDT, endDateDT]

#October 2024:
endDateDT = datetime.datetime(int('2024'),int('10'),int('27'))
startDateDT = datetime.datetime(int('2024'),int('09'),int('30'))

CTCcutoffDictionary['October-2024']=[startDateDT, endDateDT]

#September 2024:
endDateDT = datetime.datetime(int('2024'),int('09'),int('29'))
startDateDT = datetime.datetime(int('2024'),int('08'),int('26'))

CTCcutoffDictionary['September-2024']=[startDateDT, endDateDT]

#August 2024:
endDateDT = datetime.datetime(int('2024'),int('08'),int('25'))
startDateDT = datetime.datetime(int('2024'),int('07'),int('29'))

CTCcutoffDictionary['August-2024']=[startDateDT, endDateDT]

#July 2024:
endDateDT = datetime.datetime(int('2024'),int('07'),int('28'))
startDateDT = datetime.datetime(int('2024'),int('07'),int('01'))

CTCcutoffDictionary['July-2024']=[startDateDT, endDateDT]

#June 2024:
endDateDT = datetime.datetime(int('2024'),int('06'),int('30'))
startDateDT = datetime.datetime(int('2024'),int('05'),int('27'))

CTCcutoffDictionary['June-2024']=[startDateDT, endDateDT]

#May 2024:
endDateDT = datetime.datetime(int('2024'),int('05'),int('26'))
startDateDT = datetime.datetime(int('2024'),int('04'),int('29'))

CTCcutoffDictionary['May-2024']=[startDateDT, endDateDT]

#April 2024:
endDateDT = datetime.datetime(int('2024'),int('04'),int('28'))
startDateDT = datetime.datetime(int('2024'),int('04'),int('01'))

CTCcutoffDictionary['April-2024']=[startDateDT, endDateDT]

#March 2024:
endDateDT = datetime.datetime(int('2024'),int('03'),int('31'))
startDateDT = datetime.datetime(int('2024'),int('03'),int('04'))

CTCcutoffDictionary['March-2024']=[startDateDT, endDateDT]

#February 2024:
endDateDT = datetime.datetime(int('2024'),int('03'),int('03'))
startDateDT = datetime.datetime(int('2024'),int('01'),int('29'))

CTCcutoffDictionary['February-2024']=[startDateDT, endDateDT]

#January 2024:
endDateDT = datetime.datetime(int('2024'),int('01'),int('28'))
startDateDT = datetime.datetime(int('2024'),int('01'),int('01'))

CTCcutoffDictionary['January-2024']=[startDateDT, endDateDT]

#December 2023:
endDateDT = datetime.datetime(int('2023'),int('12'),int('31'))
startDateDT = datetime.datetime(int('2000'),int('01'),int('01')) #Using an absurdly old date so that i can capture any pre-jan 2024 data here

CTCcutoffDictionary['Pre Jan 2024']=[startDateDT, endDateDT]

#Pre Jan 2024 (same as December 2023, but the CTC period is named differently in our bonus database table because i'm an idiot):
endDateDT = datetime.datetime(int('2023'),int('12'),int('31'))
startDateDT = datetime.datetime(int('2000'),int('01'),int('01')) #Using an absurdly old date so that i can capture any pre-jan 2024 data here

CTCcutoffDictionary['Pre Jan 2024']=[startDateDT, endDateDT]





#=======================================================


#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#SECTION #3 | SETTING UP THE SIDEBAR:
#region CLICK HERE TO EXPAND SECTION

# Add the custom logo to the sidebar
#st.sidebar.image("static/Main_Logo_With_Name.jpg", width=275)


#endregion





#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#<>
#<>
#USER PAGES: 
#<>
#<>
#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#Using our "userPosition" variable assigned on our login page to determine the page we want to generate: 


#============================================================================================================================================================
#FIRST, pulling our userPosition variable value from our cookies: 
try:
    userPosition=cookies['userPosition']
except: 
    userPosition=None


if userPosition!=None: 
    #============================================================================================================================================================
    #OPERATIONS MANAGER KPI PAGE: 
    if userPosition=='Operations Manager':
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION A | Title Section:
        #region CLICK HERE TO EXPAND SECTION 
        st.title('Key Performance Indicators (KPIs)')


        st.markdown(
            """
            Below is a summary of all key performance indicators (KPIs) for trade superintendents and foremen.
        """
        )
        st.divider()

        #endregion
        
        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION B | Filter section:
        #region CLICK HERE TO EXPAND SECTION

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



        #==============================================================================================================================
        #Creating our columns to split our filter section into 2 halves:
        col1, col2, col3 = st.columns(3)

        #Aligning all filter selectboxes on the left side of the page by using column 1: 
        with col1: 
            #===========================================
            #Building our selectboxes for inputing the filters

            #===========
            #Bonus period selectbox:
            bpOptions = st.selectbox(
            "Filter by Bonus Period",
            ("Q1&2: 2024", "Q3&4: 2024", "Q1&2: 2025"),
            index=None,
            placeholder="Select bonus period...",
            )
        
        with col2:
            #===========
            #Custom selectbox:
            customOptions = st.selectbox(
            "Filter By A Custom Period",
            ("Current Pay Week", "Last Pay Week", "2 Weeks Ago", "3 Weeks Ago"),
            index=None,
            placeholder="Select a custom filter...",
            )

        with col3:
            #===========
            #Month selectbox:
            monthOptions = st.selectbox(
            "Filter By Month/Year",
            ("December-2024", "November-2024", "October-2024", "September-2024", "August-2024", "July-2024", "June-2024", "May-2024", "April-2024", "March-2024", "February-2024", "January-2024"),
            index=None,
            placeholder="Select a month/year...",
            )

        
            
        #==============================================================================================================================
        #Building a period selection variable based on the options selected in the selectboxes above: 

        #Our default value for the period selection will be the current bonus period
        periodSelection = 'Q1&2: 2025'

        #If they apply a bonus period filter:
        if bpOptions!=None and monthOptions==None and customOptions==None: 
            periodSelection=bpOptions

        #If they apply a month/year filter: 
        elif bpOptions==None and monthOptions!=None and customOptions==None: 
            periodSelection=monthOptions

        #If they apply a custom filter: 
        elif bpOptions==None and monthOptions==None and customOptions!=None:
            periodSelection=customOptions

        
        #==============================================================================================================================
        #Displaying the selected filter period on the app page:
        st.markdown("")
        st.markdown("")

        st.subheader("Filter Period=> {}".format(periodSelection))
        
            
        st.divider()

        #endregion

        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION C | Top of page summary values
        #region CLICK HERE TO EXPAND SECTION


        #==============================================================================================================================
        #Genrating our values:

        #=================================================================
        #Pulling cost code data from our "Master_CostCode_Data" database

        #If our filter selection is a bonus period we will pull data from our "Master_CostCode_Data" database: 
        if 'Q' in periodSelection:
            query = c.execute("SELECT * FROM Master_CostCode_Data WHERE bonusPeriod='{}'".format(periodSelection))
            values = c.fetchall()

        #If our filter selection is a month/year period we will pull data from our "Master_CostCode_Data" database: 
        elif '202' in periodSelection:
            query = c.execute("SELECT * FROM Master_CostCode_Data WHERE ctcPeriod='{}'".format(periodSelection))
            values = c.fetchall()

        #If our filter selection is a custom filter we will need to pull data from our "Heavy_Job_CostCode_Data" database: 
        else:
            #query = c.execute("SELECT * FROM Master_CostCode_Data WHERE bonusPeriod='{}'".format(periodSelection))
            #values = c.fetchall()
            pass

        #=================================================================
        #Itterating through our list of data generated above and adding up the production values:
        totalTradeCost = 0
        totalTradeEarned = 0
        totalTradeOUbudget = 0
        totalTradePF = 1

        for i in range(len(values)):
            ccTrade = values[i][12]

            #Adding up the total trade cost, earned, and $O/U budget:
            if ccTrade in ['Concrete', 'Earthwork', 'Utilities']: #First we want to make sure that this is a trade cost code, and not another type of cost code:
                entryOUbudget = values[i][11]
                entryCost = values[i][10]
                entryEarned = values[i][9]

                totalTradeOUbudget=totalTradeOUbudget+float(entryOUbudget)
                totalTradeCost = totalTradeCost+float(entryCost)
                totalTradeEarned = totalTradeEarned+float(entryEarned)

            #Calculating the PF using the total trade earned/cost values calcualted above: 
            if totalTradeCost!=0:
                totalTradePF = round(totalTradeEarned/totalTradeCost, 2)
            else:
                totalTradePF = 1


        #=================================================================
        #Querying our "Master_Paperwork_Tracking" database table and adding up the paperwork values:
        
        #Making our paperwork calculations for the total paperwork percent: 
        if "Q" in periodSelection:
            totalPaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE bonusPeriod='{}'".format(periodSelection))
            totalPaperworkValues = c.fetchall()
        elif "202" in periodSelection: 
            totalPaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE ctcPeriod='{}'".format(periodSelection))
            totalPaperworkValues = c.fetchall()
        else:
            pass
            
        #Adding up our total paperwork values for this foreman
        totalPaperwork = 0
        totalOnTime = 0
        totalLate = 0

        for j in range(len(totalPaperworkValues)):
            trade = totalPaperworkValues[j][8]

            #We only want to track paperwork for each of the main trades here, so let's check before we add each entry in!
            if trade in ['Concrete', 'Earthwork', 'Utilities']:
                totalPaperwork = totalPaperwork + 1
                if totalPaperworkValues[j][4]=="YES":
                    totalOnTime = totalOnTime + 1
                if totalPaperworkValues[j][4]=="NO":
                    totalLate = totalLate + 1

        #Calculating our paperwork percent:
        if totalPaperwork!=0:
            paperworkPercent = round(totalOnTime/totalPaperwork,2)
        else:
            paperworkPercent = 0

        #Calculate our paperwork value for display in our table: 
        paperworkValue = str(totalOnTime)+"/"+str(totalPaperwork)+" ("+str(paperworkPercent*100)+"%)"




        #=================================================================
        #Querying our "Master_Safety_Incident_Tracking" database table and adding up the paperwork values:
        safetyIncidents = 0


        #==============================================================================================================================
        #Displaying values on the application page:

        #================================================
        #Creating our columns:
        col1, col2, col3, col4 = st.columns(4)

        #================================================
        #Current $O/U Budget
        with col1:
            st.subheader("Trade $O/U Budget")

            #If the current $O/U budget is positive, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if totalTradeOUbudget>=0:
                st.success("$ "+format_with_commas(round(totalTradeOUbudget,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number
            else:
                st.error("$ "+format_with_commas(round(totalTradeOUbudget,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number

        #================================================
        #PF:
        with col2:
            st.subheader("Performance Factor (PF)")

            #If the current PF is greater than or equal to 1.0, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if totalTradePF>=1:
                st.success(str(totalTradePF))
            else:
                st.error(str(totalTradePF))

        #================================================
        #Paperwork:
        with col3:
            st.subheader("Paperwork %")

            #If the paperwork % is greater than or equal to 90%, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if paperworkPercent>=.9:
                st.success(paperworkValue)
            else:
                st.error(paperworkValue)
        
        #================================================
        #Safety Incidents:
        with col4:
            st.subheader("Safety Incidents")

            #If the safety incidents equal 0, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if safetyIncidents==0:
                st.success(str(safetyIncidents))
            else:
                st.error(str(safetyIncidents))

        st.divider()


        #endregion

        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION D | Trade Superintendent Summary Section:
        #region CLICK HERE TO EXPAND SECTION


        #========================================================================================================================================
        #SECTION D-1 | Pull table data from database and create dataframe:
        #region CLICK HERE TO EXPAND SECTION


        #===========================================================================
        #First, let's define some various bonus values for use later in this script:
        #region

        #====================================================
        #Base PF values for each trade [Celing, Floor]:
        concreteProductionBasePF = [.97, .95]
        concreteMaterialBasePF = [.97, .95]

        earthworkProductionBasePF = [1, .95]
        earthworkMaterialBasePF = [.97, .95]

        utilitiesProductionBasePF = [1, .95]
        utilitiesMaterialBasePF = [1, .95]

        #====================================================
        #Peformance bonus earn rate for each trade:
        performanceBonusEarnRate = .04

        #Bonus Pool Share for each trade:
        tradeSuperBonusPoolShare = 12502.03

        #"Projection Ratio" which is essentially just the time % complete of the selected bonus period used to project final bonuses
        projectionRatio=1

        #endregion


        #===========================================================================
        #Next, let's calculate our trade paperwork values:
        #region


        #====================================================
        #Concrete:

        #Querying our database for this trade: 
        if "Q" in periodSelection:
            tradePaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and bonusPeriod='{}'".format('Concrete', periodSelection))
            tradePaperworkValues = c.fetchall()
        elif "202" in periodSelection: 
            tradePaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and ctcPeriod='{}'".format('Concrete', periodSelection))
            tradePaperworkValues = c.fetchall()
        else:
            pass
            
        #Adding up our total paperwork values for this trade
        concretePaperwork = 0
        concretePWOT = 0
        concretePWLate = 0

        for j in range(len(tradePaperworkValues)):
            concretePaperwork = concretePaperwork + 1
            if tradePaperworkValues[j][4]=="YES":
                concretePWOT = concretePWOT + 1
            if tradePaperworkValues[j][4]=="NO":
                concretePWLate = concretePWLate + 1

        #Calculating our paperwork percent:
        if concretePaperwork!=0:
            concretePWpercent = round(concretePWOT/concretePaperwork,2)
        else:
            concretePWpercent = 0

        #Calculate our paperwork value for display in our table: 
        concretePWvalue = str(concretePWOT)+"/"+str(concretePaperwork)+" ("+str(round(concretePWpercent*100,2))+"%)"



        #====================================================
        #Earthwork 

        #Querying our database for this trade: 
        if "Q" in periodSelection:
            tradePaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and bonusPeriod='{}'".format('Earthwork', periodSelection))
            tradePaperworkValues = c.fetchall()
        elif "202" in periodSelection: 
            tradePaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and ctcPeriod='{}'".format('Earthwork', periodSelection))
            tradePaperworkValues = c.fetchall()
        else:
            pass
            
        #Adding up our total paperwork values for this trade
        earthworkPaperwork = 0
        earthworkPWOT = 0
        earthworkPWLate = 0

        for j in range(len(tradePaperworkValues)):
            earthworkPaperwork = earthworkPaperwork + 1
            if tradePaperworkValues[j][4]=="YES":
                earthworkPWOT = earthworkPWOT + 1
            if tradePaperworkValues[j][4]=="NO":
                earthworkPWLate = earthworkPWLate + 1

        #Calculating our paperwork percent:
        if earthworkPaperwork!=0:
            earthworkPWpercent = round(earthworkPWOT/earthworkPaperwork,2)
        else:
            earthworkPWpercent = 0

        #Calculate our paperwork value for display in our table: 
        earthworkPWvalue = str(earthworkPWOT)+"/"+str(earthworkPaperwork)+" ("+str(round(earthworkPWpercent*100,2))+"%)"

        #====================================================
        #Utilities 
        
        #Querying our database for this trade: 
        if "Q" in periodSelection:
            tradePaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and bonusPeriod='{}'".format('Utilities', periodSelection))
            tradePaperworkValues = c.fetchall()
        elif "202" in periodSelection: 
            tradePaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and ctcPeriod='{}'".format('Utilities', periodSelection))
            tradePaperworkValues = c.fetchall()
        else:
            pass
            
        #Adding up our total paperwork values for this trade
        utilitiesPaperwork = 0
        utilitiesPWOT = 0
        utilitiesPWLate = 0

        for j in range(len(tradePaperworkValues)):
            utilitiesPaperwork = utilitiesPaperwork + 1
            if tradePaperworkValues[j][4]=="YES":
                utilitiesPWOT = utilitiesPWOT + 1
            if tradePaperworkValues[j][4]=="NO":
                utilitiesPWLate = utilitiesPWLate + 1

        #Calculating our paperwork percent:
        if utilitiesPaperwork!=0:
            utilitiesPWpercent = round(utilitiesPWOT/utilitiesPaperwork,2)
        else:
            utilitiesPWpercent = 0

        #Calculate our paperwork value for display in our table: 
        utilitiesPWvalue = str(utilitiesPWOT)+"/"+str(utilitiesPaperwork)+" ("+str(round(utilitiesPWpercent*100,2))+"%)"

        #endregion


        #===========================================================================
        #Next, let's calculate our trade safety incident values:
        #region

        #====================================================
        #Concrete:

        #Querying our safety database and adding up the nubmer of safety incidents:
        if "Q" in periodSelection:
            tradeSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and bonusPeriod='{}'".format('Concrete', periodSelection))
            tradeSafetyValues = c.fetchall()
        elif "202" in periodSelection: 
            tradeSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and ctcPeriod='{}'".format('Concrete', periodSelection))
            tradeSafetyValues = c.fetchall()
        else:
            pass

        #Adding up the total safety incidents for this foreman: 
        concreteSafetyIncidents = 0

        for j in range(len(tradeSafetyValues)):
            concreteSafetyIncidents = concreteSafetyIncidents + 1

        #====================================================
        #Earthwork:

        #Querying our safety database and adding up the nubmer of safety incidents:
        if "Q" in periodSelection:
            tradeSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and bonusPeriod='{}'".format('Earthwork', periodSelection))
            tradeSafetyValues = c.fetchall()
        elif "202" in periodSelection: 
            tradeSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and ctcPeriod='{}'".format('Earthwork', periodSelection))
            tradeSafetyValues = c.fetchall()
        else:
            pass

        #Adding up the total safety incidents for this foreman: 
        earthworkSafetyIncidents = 0

        for j in range(len(tradeSafetyValues)):
            earthworkSafetyIncidents = earthworkSafetyIncidents + 1

        

        #====================================================
        #Utilities:

        #Querying our safety database and adding up the nubmer of safety incidents:
        if "Q" in periodSelection:
            tradeSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and bonusPeriod='{}'".format('Utilities', periodSelection))
            tradeSafetyValues = c.fetchall()
        elif "202" in periodSelection: 
            tradeSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and ctcPeriod='{}'".format('Utilities', periodSelection))
            tradeSafetyValues = c.fetchall()
        else:
            pass

        #Adding up the total safety incidents for this foreman: 
        utilitiesSafetyIncidents = 0

        for j in range(len(tradeSafetyValues)):
            utilitiesSafetyIncidents = utilitiesSafetyIncidents + 1
        

        #endregion


        #===========================================================================
        #Next, let's iterate through our query values variable "values" defined in Section C and add up all of our cost & earned values for each trade/CC type: 
        #region

        #====================================================
        #Setting initial variable values at zero that will be added to in our loop below:
        totalConcreteCost = 0
        totalConcreteProductionCost = 0
        totalConcreteMaterialCost = 0
        totalConcreteCORCost = 0
        totalConcreteReworkCost = 0
        totalConcreteEarned = 0
        totalConcreteProductionEarned = 0
        totalConcreteMaterialEarned = 0
        totalConcreteCOREarned = 0
        totalConcreteReworkEarned = 0

        totalEarthworkCost = 0
        totalEarthworkProductionCost = 0
        totalEarthworkMaterialCost = 0
        totalEarthworkCORCost = 0
        totalEarthworkReworkCost = 0
        totalEarthworkEarned = 0
        totalEarthworkProductionEarned = 0
        totalEarthworkMaterialEarned = 0
        totalEarthworkCOREarned = 0
        totalEarthworkReworkEarned = 0

        totalUtilitiesCost = 0
        totalUtilitiesProductionCost = 0
        totalUtilitiesMaterialCost = 0
        totalUtilitiesCORCost = 0
        totalUtilitiesReworkCost = 0
        totalUtilitiesEarned = 0
        totalUtilitiesProductionEarned = 0
        totalUtilitiesMaterialEarned = 0
        totalUtilitiesCOREarned = 0
        totalUtilitiesReworkEarned = 0

        #====================================================
        #Iterating through our "values" variable and adding up all of the values for our variables defined above:
        for i in range(len(values)):
            ccTrade = values[i][12]
            ccType = values[i][14]

            entryCost = float(values[i][10])
            entryEarned = float(values[i][9])

            #========================
            #Concrete calculations: 
            if ccTrade=='Concrete':
                totalConcreteCost=totalConcreteCost+entryCost
                totalConcreteEarned=totalConcreteEarned+entryEarned

                if ccType=='Production':
                    totalConcreteProductionCost=totalConcreteProductionCost+entryCost
                    totalConcreteProductionEarned=totalConcreteProductionEarned+entryEarned
                if ccType=='Material':
                    totalConcreteMaterialCost=totalConcreteMaterialCost+entryCost
                    totalConcreteMaterialEarned=totalConcreteMaterialEarned+entryEarned
                if ccType=='COR':
                    totalConcreteCORCost=totalConcreteCORCost+entryCost
                    totalConcreteCOREarned=totalConcreteCOREarned+entryEarned
                if ccType=='Rework':
                    totalConcreteReworkCost=totalConcreteReworkCost+entryCost
                    totalConcreteReworkEarned=totalConcreteReworkEarned+entryEarned

            #========================
            #Earthwork calculations: 
            if ccTrade=='Earthwork':
                totalEarthworkCost=totalEarthworkCost+entryCost
                totalEarthworkEarned=totalEarthworkEarned+entryEarned
                

                if ccType=='Production':
                    totalEarthworkProductionCost=totalEarthworkProductionCost+entryCost
                    totalEarthworkProductionEarned=totalEarthworkProductionEarned+entryEarned
                if ccType=='Material':
                    totalEarthworkMaterialCost=totalEarthworkMaterialCost+entryCost
                    totalEarthworkMaterialEarned=totalEarthworkMaterialEarned+entryEarned
                if ccType=='COR':
                    totalEarthworkCORCost=totalEarthworkCORCost+entryCost
                    totalEarthworkCOREarned=totalEarthworkCOREarned+entryEarned
                if ccType=='Rework':
                    totalEarthworkReworkCost=totalEarthworkReworkCost+entryCost
                    totalEarthworkReworkEarned=totalEarthworkReworkEarned+entryEarned

            #========================
            #Utilities calculations: 
            if ccTrade=='Utilities':
                totalUtilitiesCost=totalUtilitiesCost+entryCost
                totalUtilitiesEarned=totalUtilitiesEarned+entryEarned

                if ccType=='Production':
                    totalUtilitiesProductionCost=totalUtilitiesProductionCost+entryCost
                    totalUtilitiesProductionEarned=totalUtilitiesProductionEarned+entryEarned
                if ccType=='Material':
                    totalUtilitiesMaterialCost=totalUtilitiesMaterialCost+entryCost
                    totalUtilitiesMaterialEarned=totalUtilitiesMaterialEarned+entryEarned
                if ccType=='COR':
                    totalUtilitiesCORCost=totalUtilitiesCORCost+entryCost
                    totalUtilitiesCOREarned=totalUtilitiesCOREarned+entryEarned
                if ccType=='Rework':
                    totalUtilitiesReworkCost=totalUtilitiesReworkCost+entryCost
                    totalUtilitiesReworkEarned=totalUtilitiesReworkEarned+entryEarned
        
        
        #endregion
        

        #===========================================================================
        #Using our trade totals calculated above to calculate the total $O/U budget, PF, base PF delta, and performance bonus for each trade/cc type:
        #region

        #====================================================
        #Concrete Calculations
        #region

        #===========================
        #Production
        totalConcreteProductionOUbudget = totalConcreteProductionEarned-totalConcreteProductionCost

        if totalConcreteProductionCost!=0:
            totalConcreteProductionPF = round(totalConcreteProductionEarned/totalConcreteProductionCost,3)
        else:
            totalConcreteProductionPF = 1

        if totalConcreteProductionPF>=concreteProductionBasePF[0]:
            totalConcreteProductionBasePFdelta = round(totalConcreteProductionEarned-(totalConcreteProductionCost*concreteProductionBasePF[0]),2)
        elif totalConcreteProductionPF<=concreteProductionBasePF[1]:
            totalConcreteProductionBasePFdelta = round(totalConcreteProductionEarned-(totalConcreteProductionCost*concreteProductionBasePF[1]),2)
        else:
            totalConcreteProductionBasePFdelta = 0

        totalConcreteProductionPerformanceBonus = round(totalConcreteProductionBasePFdelta*performanceBonusEarnRate,2)

        #===========================
        #Material
        totalConcreteMaterialOUbudget = totalConcreteMaterialEarned-totalConcreteMaterialCost

        if totalConcreteMaterialCost!=0:
            totalConcreteMaterialPF = round(totalConcreteMaterialEarned/totalConcreteMaterialCost,3)
        else:
            totalConcreteMaterialPF = 1

        if totalConcreteMaterialPF>=concreteMaterialBasePF[0]:
            totalConcreteMaterialBasePFdelta = round(totalConcreteMaterialEarned-(totalConcreteMaterialCost*concreteMaterialBasePF[0]),2)
        elif totalConcreteMaterialPF<=concreteMaterialBasePF[1]:
            totalConcreteMaterialBasePFdelta = round(totalConcreteMaterialEarned-(totalConcreteMaterialCost*concreteMaterialBasePF[1]),2)
        else:
            totalConcreteMaterialBasePFdelta = 0

        totalConcreteMaterialPerformanceBonus = round(totalConcreteMaterialBasePFdelta*performanceBonusEarnRate,2)

        #===========================
        #COR
        totalConcreteCOROUbudget = totalConcreteCOREarned-totalConcreteCORCost

        if totalConcreteCORCost!=0:
            totalConcreteCORPF = round(totalConcreteCOREarned/totalConcreteCORCost,3)
        else:
            totalConcreteCORPF = 1

        totalConcreteCORPerformanceBonus = round(totalConcreteCOROUbudget*performanceBonusEarnRate,2)

        #===========================
        #Rework
        totalConcreteReworkOUbudget = totalConcreteReworkEarned-totalConcreteReworkCost

        if totalConcreteReworkCost!=0:
            totalConcreteReworkPF = round(totalConcreteReworkEarned/totalConcreteReworkCost,3)
        else:
            totalConcreteReworkPF = 1

        totalConcreteReworkPerformanceBonus = round(totalConcreteReworkOUbudget*performanceBonusEarnRate,2)

        #===========================
        #Safety Deduction
        concreteSafetyDeduction = 0

        #===========================
        #Totals
        totalConcreteOUbudget = totalConcreteEarned-totalConcreteCost

        if totalConcreteCost!=0:
            totalConcretePF = round(totalConcreteEarned/totalConcreteCost,3)
        else:
            totalConcretePF = 1

        totalConcreteBasePFdelta = totalConcreteProductionBasePFdelta+totalConcreteMaterialBasePFdelta+totalConcreteCOROUbudget+totalConcreteReworkOUbudget

        totalConcretePerformanceBonus=totalConcreteProductionPerformanceBonus+totalConcreteMaterialPerformanceBonus+totalConcreteCORPerformanceBonus+totalConcreteReworkPerformanceBonus

        #Paperwork Deduction
        concretePaperworkDeduction = -.2*(totalConcretePerformanceBonus+tradeSuperBonusPoolShare)*(1-concretePWpercent)

        #Safety Deduction
        concreteSafetyDeduction = -.3*(totalConcretePerformanceBonus+tradeSuperBonusPoolShare)*concreteSafetyIncidents                                      

        #Total bonus to date and projection
        totalConcreteBonustoDate = totalConcretePerformanceBonus+tradeSuperBonusPoolShare+concretePaperworkDeduction

        totalProjectedConcreteBonus = totalConcreteBonustoDate*projectionRatio

        #endregion

        #====================================================
        #Earthwork Calculations
        #region

        #===========================
        #Production
        totalEarthworkProductionOUbudget = totalEarthworkProductionEarned-totalEarthworkProductionCost

        if totalEarthworkProductionCost!=0:
            totalEarthworkProductionPF = round(totalEarthworkProductionEarned/totalEarthworkProductionCost,3)
        else:
            totalEarthworkProductionPF = 1

        if totalEarthworkProductionPF>=earthworkProductionBasePF[0]:
            totalEarthworkProductionBasePFdelta = round(totalEarthworkProductionEarned-(totalEarthworkProductionCost*earthworkProductionBasePF[0]),2)
        elif totalEarthworkProductionPF<=earthworkProductionBasePF[1]:
            totalEarthworkProductionBasePFdelta = round(totalEarthworkProductionEarned-(totalEarthworkProductionCost*earthworkProductionBasePF[1]),2)
        else:
            totalEarthworkProductionBasePFdelta = 0

        totalEarthworkProductionPerformanceBonus = round(totalEarthworkProductionBasePFdelta*performanceBonusEarnRate,2)

        #===========================
        #Material
        totalEarthworkMaterialOUbudget = totalEarthworkMaterialEarned-totalEarthworkMaterialCost

        if totalEarthworkMaterialCost!=0:
            totalEarthworkMaterialPF = round(totalEarthworkMaterialEarned/totalEarthworkMaterialCost,3)
        else:
            totalEarthworkMaterialPF = 1

        if totalEarthworkMaterialPF>=earthworkMaterialBasePF[0]:
            totalEarthworkMaterialBasePFdelta = round(totalEarthworkMaterialEarned-(totalEarthworkMaterialCost*earthworkMaterialBasePF[0]),2)
        elif totalEarthworkMaterialPF<=earthworkMaterialBasePF[1]:
            totalEarthworkMaterialBasePFdelta = round(totalEarthworkMaterialEarned-(totalEarthworkMaterialCost*earthworkMaterialBasePF[1]),2)
        else:
            totalEarthworkMaterialBasePFdelta = 0

        totalEarthworkMaterialPerformanceBonus = round(totalEarthworkMaterialBasePFdelta*performanceBonusEarnRate,2)

        #===========================
        #COR
        totalEarthworkCOROUbudget = totalEarthworkCOREarned-totalEarthworkCORCost

        if totalEarthworkCORCost!=0:
            totalEarthworkCORPF = round(totalEarthworkCOREarned/totalEarthworkCORCost,3)
        else:
            totalEarthworkCORPF = 1

        totalEarthworkCORPerformanceBonus = round(totalEarthworkCOROUbudget*performanceBonusEarnRate,2)

        #===========================
        #Rework
        totalEarthworkReworkOUbudget = totalEarthworkReworkEarned-totalEarthworkReworkCost

        if totalEarthworkReworkCost!=0:
            totalEarthworkReworkPF = round(totalEarthworkReworkEarned/totalEarthworkReworkCost,3)
        else:
            totalEarthworkReworkPF = 1

        totalEarthworkReworkPerformanceBonus = round(totalEarthworkReworkOUbudget*performanceBonusEarnRate,2)

        #===========================
        #Safety Deduction
        EarthworkSafetyDeduction = 0
        
        #===========================
        #Totals
        totalEarthworkOUbudget = totalEarthworkEarned-totalEarthworkCost

        if totalEarthworkCost!=0:
            totalEarthworkPF = round(totalEarthworkEarned/totalEarthworkCost,3)
        else:
            totalEarthworkPF = 1

        totalEarthworkBasePFdelta = totalEarthworkProductionBasePFdelta+totalEarthworkMaterialBasePFdelta+totalEarthworkCOROUbudget+totalEarthworkReworkOUbudget

        totalEarthworkPerformanceBonus=totalEarthworkProductionPerformanceBonus+totalEarthworkMaterialPerformanceBonus+totalEarthworkCORPerformanceBonus+totalEarthworkReworkPerformanceBonus

        #===========================
        #Paperwork Deduction
        EarthworkPaperworkDeduction = -.2*(totalEarthworkPerformanceBonus+tradeSuperBonusPoolShare)*(1-earthworkPWpercent)

        #===========================
        #Safety Deduction
        EarthworkSafetyDeduction = -.3*(totalEarthworkPerformanceBonus+tradeSuperBonusPoolShare)*earthworkSafetyIncidents                                      

        #===========================
        #Total bonus to date and projection
        totalEarthworkBonustoDate = totalEarthworkPerformanceBonus+tradeSuperBonusPoolShare+EarthworkPaperworkDeduction

        totalProjectedEarthworkBonus = totalEarthworkBonustoDate*projectionRatio

        #endregion

        #====================================================
        #Utilities Calculations
        #region

        #Production
        totalUtilitiesProductionOUbudget = totalUtilitiesProductionEarned-totalUtilitiesProductionCost

        if totalUtilitiesProductionCost!=0:
            totalUtilitiesProductionPF = round(totalUtilitiesProductionEarned/totalUtilitiesProductionCost,3)
        else:
            totalUtilitiesProductionPF = 1

        if totalUtilitiesProductionPF>=utilitiesProductionBasePF[0]:
            totalUtilitiesProductionBasePFdelta = round(totalUtilitiesProductionEarned-(totalUtilitiesProductionCost*utilitiesProductionBasePF[0]),2)
        elif totalUtilitiesProductionPF<=utilitiesProductionBasePF[1]:
            totalUtilitiesProductionBasePFdelta = round(totalUtilitiesProductionEarned-(totalUtilitiesProductionCost*utilitiesProductionBasePF[1]),2)
        else:
            totalUtilitiesProductionBasePFdelta = 0

        totalUtilitiesProductionPerformanceBonus = round(totalUtilitiesProductionBasePFdelta*performanceBonusEarnRate,2)

        #===========================
        #Material
        totalUtilitiesMaterialOUbudget = totalUtilitiesMaterialEarned-totalUtilitiesMaterialCost

        if totalUtilitiesMaterialCost!=0:
            totalUtilitiesMaterialPF = round(totalUtilitiesMaterialEarned/totalUtilitiesMaterialCost,3)
        else:
            totalUtilitiesMaterialPF = 1

        if totalUtilitiesMaterialPF>=utilitiesMaterialBasePF[0]:
            totalUtilitiesMaterialBasePFdelta = round(totalUtilitiesMaterialEarned-(totalUtilitiesMaterialCost*utilitiesMaterialBasePF[0]),2)
        elif totalUtilitiesMaterialPF<=utilitiesMaterialBasePF[1]:
            totalUtilitiesMaterialBasePFdelta = round(totalUtilitiesMaterialEarned-(totalUtilitiesMaterialCost*utilitiesMaterialBasePF[1]),2)
        else:
            totalUtilitiesMaterialBasePFdelta = 0

        totalUtilitiesMaterialPerformanceBonus = round(totalUtilitiesMaterialBasePFdelta*performanceBonusEarnRate,2)

        #===========================
        #COR
        totalUtilitiesCOROUbudget = totalUtilitiesCOREarned-totalUtilitiesCORCost

        if totalUtilitiesCORCost!=0:
            totalUtilitiesCORPF = round(totalUtilitiesCOREarned/totalUtilitiesCORCost,3)
        else:
            totalUtilitiesCORPF = 1

        totalUtilitiesCORPerformanceBonus = round(totalUtilitiesCOROUbudget*performanceBonusEarnRate,2)

        #===========================
        #Rework
        totalUtilitiesReworkOUbudget = totalUtilitiesReworkEarned-totalUtilitiesReworkCost

        if totalUtilitiesReworkCost!=0:
            totalUtilitiesReworkPF = round(totalUtilitiesReworkEarned/totalUtilitiesReworkCost,3)
        else:
            totalUtilitiesReworkPF = 1

        totalUtilitiesReworkPerformanceBonus = round(totalUtilitiesReworkOUbudget*performanceBonusEarnRate,2)

        #===========================
        #Safety Deduction
        UtilitiesSafetyDeduction = 0

        #===========================
        #Totals
        totalUtilitiesOUbudget = totalUtilitiesEarned-totalUtilitiesCost

        if totalUtilitiesCost!=0:
            totalUtilitiesPF = round(totalUtilitiesEarned/totalUtilitiesCost,3)
        else:
            totalUtilitiesPF = 1

        totalUtilitiesBasePFdelta = totalUtilitiesProductionBasePFdelta+totalUtilitiesMaterialBasePFdelta+totalUtilitiesCOROUbudget+totalUtilitiesReworkOUbudget

        totalUtilitiesPerformanceBonus=totalUtilitiesProductionPerformanceBonus+totalUtilitiesMaterialPerformanceBonus+totalUtilitiesCORPerformanceBonus+totalUtilitiesReworkPerformanceBonus

        #===========================
        #Paperwork Deduction
        UtilitiesPaperworkDeduction = -.2*(totalUtilitiesPerformanceBonus+tradeSuperBonusPoolShare)*(1-utilitiesPWpercent)

        #===========================
        #Safety Deduction
        UtilitiesSafetyDeduction = -.3*(totalUtilitiesPerformanceBonus+tradeSuperBonusPoolShare)*utilitiesSafetyIncidents                                      

        #===========================
        #Total bonus to date and projection
        totalUtilitiesBonustoDate = totalUtilitiesPerformanceBonus+tradeSuperBonusPoolShare+UtilitiesPaperworkDeduction

        totalProjectedUtilitiesBonus = totalUtilitiesBonustoDate*projectionRatio
        #endregion

        
        #endregion
        

        #===========================================================================
        #Finally, defining column header labels for table and updating our dataframe with our data calculated above: 
        #region

        column_headers = ['Trade Superintendent/CC Type', 'Total Cost       ', 'Total Earned      ', '$O/U Budget', 'PF', 'Paperwork %       ', 'Safety Incidents', 'Base PF Delta', 'Performance Bonus', 'PW Deduct', 'Safety Deduct', 'Pool Share', 'Total Bonus To Date', 'Projected Bonus']

        data_values = [
            ['Concrete - Chris Roberts', totalConcreteCost, totalConcreteEarned, totalConcreteOUbudget, totalConcretePF, concretePWvalue, concreteSafetyIncidents, totalConcreteBasePFdelta, totalConcretePerformanceBonus, concretePaperworkDeduction, concreteSafetyDeduction, tradeSuperBonusPoolShare, totalConcreteBonustoDate, totalProjectedConcreteBonus],
            ['Production', totalConcreteProductionCost, totalConcreteProductionEarned, totalConcreteProductionOUbudget, totalConcreteProductionPF, '', '', totalConcreteProductionBasePFdelta, totalConcreteProductionPerformanceBonus],
            ['Materials', totalConcreteMaterialCost, totalConcreteMaterialEarned, totalConcreteMaterialOUbudget, totalConcreteMaterialPF, '', '', totalConcreteMaterialBasePFdelta, totalConcreteMaterialPerformanceBonus],
            ['Change Orders', totalConcreteCORCost, totalConcreteCOREarned, totalConcreteCOROUbudget, totalConcreteCORPF, '', '', totalConcreteCOROUbudget, totalConcreteCORPerformanceBonus],
            ['Rework', totalConcreteReworkCost, totalConcreteReworkEarned, totalConcreteReworkOUbudget, totalConcreteReworkPF, '', '', totalConcreteReworkOUbudget, totalConcreteReworkPerformanceBonus],

            ['Earthwork - Gabino Gonzalez', totalEarthworkCost, totalEarthworkEarned, totalEarthworkOUbudget, totalEarthworkPF, earthworkPWvalue, earthworkSafetyIncidents, totalEarthworkBasePFdelta, totalEarthworkPerformanceBonus, EarthworkPaperworkDeduction, EarthworkSafetyDeduction, tradeSuperBonusPoolShare, totalEarthworkBonustoDate, totalProjectedEarthworkBonus],
            ['Production', totalEarthworkProductionCost, totalEarthworkProductionEarned, totalEarthworkProductionOUbudget, totalEarthworkProductionPF, '', '', totalEarthworkProductionBasePFdelta, totalEarthworkProductionPerformanceBonus],
            ['Materials', totalEarthworkMaterialCost, totalEarthworkMaterialEarned, totalEarthworkMaterialOUbudget, totalEarthworkMaterialPF, '', '', totalEarthworkMaterialBasePFdelta, totalEarthworkMaterialPerformanceBonus],
            ['Change Orders', totalEarthworkCORCost, totalEarthworkCOREarned, totalEarthworkCOROUbudget, totalEarthworkCORPF, '', '', totalEarthworkCOROUbudget, totalEarthworkCORPerformanceBonus],
            ['Rework', totalEarthworkReworkCost, totalEarthworkReworkEarned, totalEarthworkReworkOUbudget, totalEarthworkReworkPF, '', '', totalEarthworkReworkOUbudget, totalEarthworkReworkPerformanceBonus],

            ['Utilities - Miguel Soto', totalUtilitiesCost, totalUtilitiesEarned, totalUtilitiesOUbudget, totalUtilitiesPF, utilitiesPWvalue, utilitiesSafetyIncidents, totalUtilitiesBasePFdelta, totalUtilitiesPerformanceBonus, UtilitiesPaperworkDeduction, UtilitiesSafetyDeduction, tradeSuperBonusPoolShare, totalUtilitiesBonustoDate, totalProjectedUtilitiesBonus],
            ['Production', totalUtilitiesProductionCost, totalUtilitiesProductionEarned, totalUtilitiesProductionOUbudget, totalUtilitiesProductionPF, '', '', totalUtilitiesProductionBasePFdelta, totalUtilitiesProductionPerformanceBonus],
            ['Materials', totalUtilitiesMaterialCost, totalUtilitiesMaterialEarned, totalUtilitiesMaterialOUbudget, totalUtilitiesMaterialPF, '', '', totalUtilitiesMaterialBasePFdelta, totalUtilitiesMaterialPerformanceBonus],
            ['Change Orders', totalUtilitiesCORCost, totalUtilitiesCOREarned, totalUtilitiesCOROUbudget, totalUtilitiesCORPF, '', '', totalUtilitiesCOROUbudget, totalUtilitiesCORPerformanceBonus],
            ['Rework', totalUtilitiesReworkCost, totalUtilitiesReworkEarned, totalUtilitiesReworkOUbudget, totalUtilitiesReworkPF, '', '', totalUtilitiesReworkOUbudget, totalUtilitiesReworkPerformanceBonus],

            ['Utilities - Adrian Mosqueda', 425000.07, 678900.72, 245700.90, 1.41, '57/82 (67.54%)', 0, 90581.76, 3623.27, -1576.06, 0, 12502.03, 14549.24, 14549.24],
            ['Production', 425000.07, 678900.72, 245700.90, 1.41, '', '', 44809.83, 1729.39],
            ['Materials', 425000.07, 678900.72, 245700.90, 1.41, '', '', 44809.83, 1729.39],
            ['Change Orders', 425000.07, 678900.72, 245700.90, 1.41, '', '', 44809.83, 1729.39],
            ['Rework', 425000.07, 678900.72, 245700.90, 1.41, '', '', 44809.83, 1729.39],
            ]

        #===========================================================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        tradeSuperTableData = create_dataframe(column_headers, data_values)

        #endregion


        #endregion


        #========================================================================================================================================
        #SECTION D-2 | Define functions to apply formatting to table:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #Defining a styling function to color cells with negative values red and positive values green:
        def color_negative_red(val):
            if pd.isna(val) or val == '':
                return 'background-color: ; color: '  # Make NaN cells appear blank
            if isinstance(val, str):
                try:
                    numeric_val = float(val.replace('$', '').replace(',', ''))
                except ValueError:
                    return ''
            else:
                numeric_val = float(val)
            
            if numeric_val < 0:
                return 'background-color: #FF6961'  # Darker red for negative values
            else:
                return 'background-color: #77DD77'  # Darker green for positive values

        #===========================================================================
        #Defining a styling function to highlight summary rows grey:
        def highlight_and_bold_rows(row):
            value_to_highlight = ['Concrete - Chris Roberts', 'Earthwork - Gabino Gonzalez', 'Utilities - Miguel Soto', 'Utilities - Adrian Mosqueda']
            if row.iloc[0] in value_to_highlight:
                return [
                    'background-color: #D3D3D3; font-weight: 1200;'
                    'border-top: 2px solid black; border-bottom: 2px solid black;'
                ] * len(row)
            else:
                return [''] * len(row)

        #===========================================================================
        #Defining a styling function to color PF cells red if they are below a 1.0 and green if they are above a 1.0:
        def highlight_ratio(val):
            if pd.isna(val):
                return 'background-color: white; color: white'  # Make NaN cells appear blank
            elif val > 1:
                color = 'green' 
                return f'color: {color}'
            else:
                color = 'red' 
                return f'color: {color}'
        

        #===========================================================================
        #Defining a styling function to color numbers red/green based on a value over/under 0:
        def color_dollar_values(val):
            try:
                # Remove $ and convert to float
                num_val = float(val.replace('$', '').replace(',', ''))
                color = 'red' if num_val < 0 else 'green'
                return f'color: {color}'
            except ValueError:
                # Return default styling if conversion fails
                return ''
        
        
        #endregion


        #========================================================================================================================================
        #SECTION D-3 | Generate summary table and apply formatting:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #Applying number formatting to each column: 
        tradeSuperTableData['Total Cost       '] = tradeSuperTableData['Total Cost       '].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['Total Earned      '] = tradeSuperTableData['Total Earned      '].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['$O/U Budget'] = tradeSuperTableData['$O/U Budget'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['PF'] = tradeSuperTableData['PF'].round(2)
        tradeSuperTableData['Base PF Delta'] = tradeSuperTableData['Base PF Delta'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['Performance Bonus'] = tradeSuperTableData['Performance Bonus'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['PW Deduct'] = tradeSuperTableData['PW Deduct'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Safety Deduct'] = tradeSuperTableData['Safety Deduct'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Pool Share'] = tradeSuperTableData['Pool Share'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Total Bonus To Date'] = tradeSuperTableData['Total Bonus To Date'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Projected Bonus'] = tradeSuperTableData['Projected Bonus'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')

        #===========================================================================
        #Applying the grey row highlighting to our trade summary rows:
        styled_df = tradeSuperTableData.style.apply(highlight_and_bold_rows, axis=1)

        #===========================================================================
        #Coloring specified column cells red/green based on being a negative/positive $ value:
        columns_to_color = ['Total Bonus To Date', 'Projected Bonus']
        
        for col in columns_to_color:
            styled_df = styled_df.applymap(color_negative_red, subset=[col])

        #===========================================================================
        #Specifying the columns that we'd like to color the number of and applying the coloring:
        styled_df = styled_df.applymap(color_dollar_values, subset=['$O/U Budget', 'Base PF Delta', 'Performance Bonus', 'PW Deduct', 'Safety Deduct', 'Pool Share'])

        #===========================================================================
        #Coloring PF column cells red/green based on being a below/above a 1.0 PF:
        styled_df = styled_df.applymap(highlight_ratio, subset=['PF'])

        #===========================================================================
        #Generating our table title header and creating our table: 
        st.subheader("Trade Superintendent Summary")

        st.dataframe(
            styled_df,
            column_config={
                'Trade Super Name': st.column_config.TextColumn('Trade Super Name', help='Trade & Trade Superintendent Name/ Cost Code Type'),
                'Total Cost': st.column_config.TextColumn('Total Cost', help='Total cost to date this period'),
                'Total Earned': st.column_config.TextColumn('Total Earned', help='Total budget $ earned to date this period'),
                '$O/U Budget': st.column_config.TextColumn("$O/U Budget", help="Total $ difference between cost and earned to date this period"),
                'PF': st.column_config.NumberColumn('PF', help='Performance factor is total $ earned divided by total cost to date this period', format="%.2f"),
                'Paperwork': st.column_config.TextColumn('Paperwork', help='The total number of timecards, JHAs, equipment inspections, and delivery tickets submitted on time to date this period'),
                'Safety Incidents': st.column_config.TextColumn('Safety Incidents', help='The total number of major safety incidents to date this period'),
                'Base PF Delta': st.column_config.TextColumn('Base PF Delta', help='The total $ O/U budget when the trade base PF is factored in'),
                'Performance Bonus': st.column_config.TextColumn('Performance Bonus', help='4% of the Base PF Delta'),
                'PW Deduct': st.column_config.TextColumn('PW Deduct', help='Paperwork Deduction = Total Bonus X (100% - % On Time) X -0.2'),
                'Safety Deduct': st.column_config.TextColumn('Safety Deduct', help='Safety Deduction = Total Bonus X # of Safety Incidents X -0.3'),
                'Pool Share': st.column_config.TextColumn('Pool Share', help='Trade superintendents are given 29% of the total trade bonus pool, which is divided equally among all active trade superintendents'),
                'Total Bonus to Date': st.column_config.TextColumn('Total Bonus to Date', help='Total $ amount of bonus earned to date for the current bonus period'),
                'Projected Bonus': st.column_config.TextColumn('Projected Bonus', help='Total projected bonus $ amount for the 6 month bonus period')
            },
            hide_index=True
        )

        #===========================================================================
        #Adding some padding between our next summary table:
        st.markdown("")
        st.markdown("")

        #endregion


        #endregion


        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION E | Foreman Summary Section:
        #region CLICK HERE TO EXPAND SECTION


        #========================================================================================================================================
        #SECTION E-1 | Pull table data from database and create dataframe:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #First, let's define some various bonus values for use later in this script:
        #region

        #====================================================
        #Base PF values for each trade [Celing, Floor]:
        foremanBasePFDict={}

        foremanBasePFDict["Concrete"] = [.95, .91]
        foremanBasePFDict["Earthwork"] = [.95, .91]
        foremanBasePFDict["Utilities"] = [.98, .95]


        #====================================================
        #Peformance bonus earn rate for each foreman:
        foremanPerformanceBonusEarnRate = .1

        #Bonus Pool Share for each trade:
        foremanBonusPoolShare = 5323.20

        #"Projection Ratio" which is essentially just the time % complete of the selected bonus period used to project final bonuses
        projectionRatio=1

        #endregion


        #===========================================================================
        #Next, let's create a dictionary of info to be used to populate our foreman summary table: 
        #region

        #Querying our "Users" table of our "Pyramid_Analytics_Database" for all current employed foremen: 
        query = c.execute("SELECT * FROM Users WHERE position='{}' and employmentStatus='{}'".format('Foreman', 'Employed'))
        values = c.fetchall()

        #Iterating through our list of values and creating our foreman list: 
        foremanInfoDictionary = {}

        for i in range(len(values)):
            #====================================================
            #Pulling the name, trade, and hire date from our "Users" database
            name = values[i][2]
            craft = values[i][5]
            hireDate = values[i][8]
            hireDateDT = datetime.datetime(int(hireDate[0:4]),int(hireDate[5:7]),int(hireDate[8:10]))
            
            #====================================================
            #Calculating the bonus pool share for this foreman:
            
            #=====================
            #Determining the start/end date of each filter type:  
            if "Q" in periodSelection:
                startDate = bonusPeriodDateRangeDictionary[periodSelection][0]
                endDate = bonusPeriodDateRangeDictionary[periodSelection][1]
            elif "202" in periodSelection: 
                startDate = CTCcutoffDictionary[periodSelection][0]
                endDate = CTCcutoffDictionary[periodSelection][1]
            else:
                pass
            
            #=====================
            #Determining the % of the bonus period that this employee will earn based on their hire date: 
            bonusPeriodDuration = endDate-startDate

            #If the employee was hired after the start of the bonus period, their earn % will be non-zero:
            if hireDateDT<startDate:
                employedDuration = startDate-hireDateDT
                bonusPoolPercent = employedDuration/bonusPeriodDuration
            #If not, then they weren't around for this bonus period and will get no share of the bonus pool: 
            else:
                bonusPoolPercent = 0

            #=====================
            #Counting the number of foremen employed this period:
            entryUserQuery = c.execute("SELECT * FROM Users WHERE position='{}'".format('Foreman'))
            entryUserValues = c.fetchall()

            foremanCount = 0

            for j in range(len(entryUserValues)):
                entryHireDate=entryUserValues[i][8]
                entryHireDateDT = datetime.datetime(int(entryHireDate[0:4]),int(entryHireDate[5:7]),int(entryHireDate[8:10]))

                if entryHireDateDT<startDate:
                    foremanCount = foremanCount + 1

            #=====================
            #Next, calculating the total bonus pool amount for foreman this period by querying our "Master_CostCode_Data" database:
            if "Q" in periodSelection: 
                costCodeQuery = c.execute("SELECT * FROM Master_CostCode_Data WHERE bonusPeriod='{}'".format(periodSelection))
                costCodeValues = c.fetchall()
            elif "202" in periodSelection: 
                costCodeQuery = c.execute("SELECT * FROM Master_CostCode_Data WHERE ctcPeriod='{}'".format(periodSelection))
                costCodeValues = c.fetchall()
            else:
                pass
            
            #=====================
            #Adding up the total cost and earned:
            totalProjectCost = 0
            totalProjectEarned = 0

            for j in range(len(costCodeValues)):
                #IMPORTANT! WE DON'T WANT TO REMOVE ANY MANUAL ADJUSTMENTS FROM OUR BONUS POOL CALCS, SO FILTER THEM HERE!
                ccDescription = costCodeValues[j][3]

                if "MANUAL ADJUST" not in ccDescription:
                    totalProjectCost = totalProjectCost + float(costCodeValues[j][10])
                    totalProjectEarned = totalProjectEarned + float(costCodeValues[j][9])

            #=====================
            #Calculating the base PF delta:
            projectBasePFdelta = totalProjectEarned-(totalProjectCost*.96)

            #=====================
            #Foreman are allocated 29% of the total bonus pool, divided among the total number of foremen employed during this period: 
            totalForemanBonusPoolShare = .29*projectBasePFdelta/foremanCount
            
            #=====================
            #Finally, multiplying the total foreman pool share by the % of time that the foreman was employed for this period:
            entryBonusPoolShare = round(totalForemanBonusPoolShare*bonusPoolPercent,2)
            
            #entryBonusPoolShare = 5323.20

            
            #====================================================
            #Querying our "Master_Foreman_Data" database for our bonus values, keeping in mind the filtering method
            if "Q" in periodSelection:
                foremanBonusQuery = c.execute("SELECT * FROM Master_Foreman_Data WHERE foreman='{}' and bonusPeriod='{}'".format(name, periodSelection))
                foremanBonusValues = c.fetchall()
            elif "202" in periodSelection: 
                foremanBonusQuery = c.execute("SELECT * FROM Master_Foreman_Data WHERE foreman='{}' and ctcPeriod='{}'".format(name, periodSelection))
                foremanBonusValues = c.fetchall()
            else:
                pass 
            
            #====================================================
            #Itterating through our list of values from our database and adding up the total cost, earned, $O/U budget, and PF:
            totalCost = 0
            totalEarned = 0
             
            for j in range(len(foremanBonusValues)):
                #Defining our variables from our database:
                entryCost = float(foremanBonusValues[j][16])
                entryEarned = float(foremanBonusValues[j][17])

                totalCost = totalCost+entryCost
                totalEarned = totalEarned+entryEarned

            totalOUbudget = totalEarned-totalCost
            
            if totalCost!=0:
                totalPF = round(totalEarned/totalCost,2)
            else:
                totalPF = 1

            #====================================================
            #Making our paperwork calculations for the total paperwork percent: 
            if "Q" in periodSelection:
                foremanPaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE employeeName='{}' and bonusPeriod='{}'".format(name, periodSelection))
                foremanPaperworkValues = c.fetchall()
            elif "202" in periodSelection: 
                foremanPaperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE employeeName='{}' and ctcPeriod='{}'".format(name, periodSelection))
                foremanPaperworkValues = c.fetchall()
            else:
                pass
            
            #Adding up our total paperwork values for this foreman
            totalPaperwork = 0
            totalOnTime = 0
            totalLate = 0

            for j in range(len(foremanPaperworkValues)):
                totalPaperwork = totalPaperwork + 1
                if foremanPaperworkValues[j][4]=="YES":
                    totalOnTime = totalOnTime + 1
                if foremanPaperworkValues[j][4]=="NO":
                    totalLate = totalLate + 1

            #Calculating our paperwork percent:
            if totalPaperwork!=0:
                paperworkPercent = round(totalOnTime/totalPaperwork,2)
            else:
                paperworkPercent = 0

            #Calculate our paperwork value for display in our table: 
            paperworkDisplayValue = str(totalOnTime)+"/"+str(totalPaperwork)+" ("+str(round(paperworkPercent*100,2))+"%)"

            #====================================================
            #Querying our safety database and adding up the nubmer of safety incidents:
            if "Q" in periodSelection:
                foremanSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE employeeName='{}' and bonusPeriod='{}'".format(name, periodSelection))
                foremanSafetyValues = c.fetchall()
            elif "202" in periodSelection: 
                foremanSafetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE employeeName='{}' and ctcPeriod='{}'".format(name, periodSelection))
                foremanSafetyValues = c.fetchall()
            else:
                pass

            #Adding up the total safety incidents for this foreman: 
            foremanSafetyIncidents = 0

            for j in range(len(foremanSafetyValues)):
                foremanSafetyIncidents = foremanSafetyIncidents + 1

            #====================================================
            #Calculating the base PF delta, performance bonus, paperwork deduction, safety deduction, total bonus, and projected bonus:

            #Base PF delta calculation: 
            basePFvalues = foremanBasePFDict[craft]

            if totalPF>=basePFvalues[0]:
                adjustedCost = round(basePFvalues[0]*totalCost,2)
                basePFdelta = totalEarned-adjustedCost
            elif totalPF<=basePFvalues[1]:
                adjustedCost = round(basePFvalues[1]*totalCost,2)
                basePFdelta = totalEarned-adjustedCost
            else:
                basePFdelta = 0

            #Performance bonus calculation: 
            performanceBonus = round(basePFdelta*foremanPerformanceBonusEarnRate,2)

            #Paperwork and safety deduction calculations: 
            bonusSubTotal = performanceBonus+entryBonusPoolShare

            paperworkDeduct = -.2*bonusSubTotal*(1-paperworkPercent)

            safetyDeduct = -.3*bonusSubTotal*foremanSafetyIncidents

            #Total bonus to date calculation: 
            totalBonus = entryBonusPoolShare+performanceBonus+paperworkDeduct+safetyDeduct

            #Projected bonus calculation
            projectedBonus = totalBonus*projectionRatio

            #====================================================
            #Finally, updating our dictionary
            foremanInfoDictionary[name]=[craft, totalCost, totalEarned, totalOUbudget, totalPF, paperworkDisplayValue, foremanSafetyIncidents, basePFdelta, performanceBonus, paperworkDeduct, safetyDeduct, entryBonusPoolShare, totalBonus, projectedBonus]


        #endregion


        #===========================================================================
        #Defining column header labels for table and adding our values generated above:
        #region
        column_headers = ['Foreman Name', 'Trade', 'Total Cost', 'Total Earned', '$O/U Budget', 'PF', 'Paperwork', 'Safety Incidents', 'Base PF Delta', 'Performance Bonus', 'PW Deduct', 'Safety Deduct', 'Pool Share', 'Total Bonus To Date', 'Projected Bonus']
        
        data_values = [] #This variable is a nested list that will be entered into our dataframe in the next step: 

        for key,values in foremanInfoDictionary.items():
            foreman=key
            trade = values[0]
            totalCost = values[1]
            totalEarned = values[2]
            totalOUbudget = values[3]
            totalPF = values[4]
            paperwork = values[5]
            safetyIncidents = values[6]
            basePFdelta = values[7]
            performanceBonus = values[8]
            paperworkDeduct = values[9]
            safetyDeduct = values[10]
            poolShare = values[11]
            totalBonus = values[12]
            projectedBonus = values[13]

            data_values.append([foreman, trade, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, performanceBonus, paperworkDeduct, safetyDeduct, poolShare, totalBonus, projectedBonus])
            
        #endregion


        #===========================================================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        #region
        foremanTableData = create_dataframe(column_headers, data_values)

        #endregion

        #endregion
        

        #========================================================================================================================================
        #SECTION E-2 | Define functions to apply formatting to table:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #Defining a styling function to color cells with negative values red and positive values green:
        def color_negative_red(val):
            if pd.isna(val) or val == '':
                return 'background-color: ; color: '  # Make NaN cells appear blank
            if isinstance(val, str):
                try:
                    numeric_val = float(val.replace('$', '').replace(',', ''))
                except ValueError:
                    return ''
            else:
                numeric_val = float(val)
            
            if numeric_val < 0:
                return 'background-color: #FF6961'  # Darker red for negative values
            else:
                return 'background-color: #77DD77'  # Darker green for positive values

        #===========================================================================
        #Defining a styling function to color PF cells red if they are below a 1.0 and green if they are above a 1.0:
        def highlight_ratio(val):
            if pd.isna(val):
                return 'background-color: white; color: white'  # Make NaN cells appear blank
            elif val > 1:
                color = 'green' 
                return f'color: {color}'
            else:
                color = 'red' 
                return f'color: {color}'
        
        #===========================================================================
        #Defining a styling function to color numbers red/green based on a value over/under 0:
        def color_dollar_values(val):
            try:
                # Remove $ and convert to float
                num_val = float(val.replace('$', '').replace(',', ''))
                color = 'red' if num_val < 0 else 'green'
                return f'color: {color}'
            except ValueError:
                # Return default styling if conversion fails
                return ''
                
        #endregion


        #========================================================================================================================================
        #SECTION E-3 | Generate summary table and apply formatting:
        #region CLICK HERE TO EXPAND SECTION
    
        #===========================================================================
        #Applying number formatting to each column: 
        foremanTableData['Total Cost'] = foremanTableData['Total Cost'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Total Earned'] = foremanTableData['Total Earned'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['$O/U Budget'] = foremanTableData['$O/U Budget'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Base PF Delta'] = foremanTableData['Base PF Delta'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Performance Bonus'] = foremanTableData['Performance Bonus'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['PW Deduct'] = foremanTableData['PW Deduct'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Safety Deduct'] = foremanTableData['Safety Deduct'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Pool Share'] = foremanTableData['Pool Share'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Total Bonus To Date'] = foremanTableData['Total Bonus To Date'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Projected Bonus'] = foremanTableData['Projected Bonus'].apply(lambda x: f'${x:,.2f}')



        #===========================================================================
        #Coloring specified column cells red/green based on being a negative/positive $ value:

        #The "highlight_and_bold_rows" function below is actually not needed for this section, but because i am using the same styling functions from the superintendent table i had to include it
        styled_foreman_df = foremanTableData.style.apply(highlight_and_bold_rows, axis=1)

        #Specifying the columns that we'd like to color the ENTIRE cell of and applying the coloring:
        columns_to_color = ['Total Bonus To Date', 'Projected Bonus'] 
        
        for col in columns_to_color:
            styled_foreman_df = styled_foreman_df.applymap(color_negative_red, subset=[col])

        #Specifying the columns that we'd like to color the number of and applying the coloring:
        styled_foreman_df = styled_foreman_df.applymap(color_dollar_values, subset=['$O/U Budget', 'Base PF Delta', 'Performance Bonus', 'PW Deduct', 'Safety Deduct', 'Pool Share'])

        #===========================================================================
        #Coloring PF column cells red/green based on being a below/above a 1.0 PF:
        styled_foreman_df = styled_foreman_df.applymap(highlight_ratio, subset=['PF'])


        #===========================================================================
        #Displaying our project summary table on the left side of our applicaton page:
        st.subheader("Foreman Summary")

        st.dataframe(
            styled_foreman_df,
            column_config={
                'Foreman Name': st.column_config.TextColumn('Trade Super Name', help='Trade & Trade Superintendent Name/ Cost Code Type'),
                'Total Cost': st.column_config.TextColumn('Total Cost', help='Total cost to date this period'),
                'Total Earned': st.column_config.TextColumn('Total Earned', help='Total budget $ earned to date this period'),
                '$O/U Budget': st.column_config.TextColumn("$O/U Budget", help="Total $ difference between cost and earned to date this period"),
                'PF': st.column_config.NumberColumn('PF', help='Performance factor is total $ earned divided by total cost to date this period', format="%.2f"),
                'Paperwork': st.column_config.TextColumn('Paperwork', help='The total number of timecards, JHAs, equipment inspections, and delivery tickets submitted on time to date this period'),
                'Safety Incidents': st.column_config.TextColumn('Safety Incidents', help='The total number of major safety incidents to date this period'),
                'Base PF Delta': st.column_config.TextColumn('Base PF Delta', help='The total $ O/U budget when the trade base PF is factored in'),
                'Performance Bonus': st.column_config.TextColumn('Performance Bonus', help='4% of the Base PF Delta'),
                'PW Deduct': st.column_config.TextColumn('PW Deduct', help='Paperwork Deduction = Total Bonus X (100% - % On Time) X -0.2'),
                'Safety Deduct': st.column_config.TextColumn('Safety Deduct', help='Safety Deduction = Total Bonus X # Safety Incidents X -0.3'),
                'Pool Share': st.column_config.TextColumn('Pool Share', help='Trade superintendents are given 29% of the total trade bonus pool, which is divided equally among all active trade superintendents'),
                'Total Bonus to Date': st.column_config.TextColumn('Total Bonus to Date', help='Total $ amount of bonus earned to date for the current bonus period'),
                'Projected Bonus': st.column_config.TextColumn('Projected Bonus', help='Total projected bonus $ amount for the 6 month bonus period')
            },
            hide_index=True
        )

        #===========================================================================
        #Adding some padding between our next summary table:
        st.markdown("")
        st.markdown("")

        #endregion


        #endregion


        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION F | Paperwork Summary:
        #region CLICK HERE TO EXPAND SECTION

        #========================================================================================================================================
        #SECTION F-1 | Pull table data from database and create dataframe:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #Defining column header labels for table:
        column_headers = ['Trade           ', 'Trade Superintendent/Foreman', 'Total Paperwork', 'Timecards', 'JHAs', 'Equipment Inspections', 'Delivery Tickets']
        
        #===========================================================================
        #Pulling trade super bonus values from our database:
        data_values = [
            ['Concrete', 'Chris Robers', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)'],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['Earthwork', 'Gabino Gonzalez', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)'],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['Utilities', 'Miguel Soto/Adrian Mosqueda', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)'],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', ''],
            ['', 'Raymundo Soto', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '57/82 (67.54%)', '']
            ]


        #===========================================================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        paperworkTableData = create_dataframe(column_headers, data_values)


        #endregion

        #========================================================================================================================================
        #SECTION F-2 | Define functions to apply formatting to table:
        #region CLICK HERE TO EXPAND SECTION


        #endregion

        #========================================================================================================================================
        #SECTION F-3 | Generate summary table and apply formatting:
        #region CLICK HERE TO EXPAND SECTION

        #Displaying our project summary table on the left side of our applicaton page:
        st.subheader("Paperwork Summary")
        st.dataframe(data=paperworkTableData, hide_index=True) 


        #endregion


        st.markdown("")
        st.markdown("")
        #endregion


        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION G | Project/Trade Summary:
        #region CLICK HERE TO EXPAND SECTION

        #========================================================================================================================================
        #SECTION G-1 | Pull table data from database and create dataframe:
        #region CLICK HERE TO EXPAND SECTION


        #===========================================================================
        #Defining column header labels for table:
        column_headers = ['Project Name', 'Total Cost', 'Total Earned', '$O/U Budget', 'PF', 'Safety Incidents', 'Base PF Delta', 'Trade Pool Contribution To Date', 'Projected Trade Pool Contribution']
        

        #===========================================================================
        #Pulling trade super bonus values from our database:
        data_values = [
            ['21008 - Dallas CBD Fairpark', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Concrete', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Earthwork', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Miguel Soto', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Adrian Mosqueda', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['22010 - Dallas Street Reconstruction 12-463', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Concrete', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Earthwork', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Miguel Soto', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Adrian Mosqueda', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['23017 - Prosper Preston Road/Prosper Trail', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Concrete', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Earthwork', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Miguel Soto', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Adrian Mosqueda', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['23018 - Richardson Sherwood Dr Recon', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Concrete', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Earthwork', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Miguel Soto', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55],
            ['Utilities - Adrian Mosqueda', 425000.07, 678900.72, 245700.90, 1.41, 0, 407873.35, 33649.55, 33649.55]
            ]


        #===========================================================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        projectTableData = create_dataframe(column_headers, data_values)

        #endregion

        #========================================================================================================================================
        #SECTION G-2 | Define functions to apply formatting to table:
        #region CLICK HERE TO EXPAND SECTION



        #endregion

        #========================================================================================================================================
        #SECTION G-3 | Generate summary table and apply formatting:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #Displaying our project summary table on the left side of our applicaton page:
        st.subheader("Project/Trade Summary")
        st.dataframe(data=projectTableData, hide_index=True) 

        #===========================================================================
        #Adding some padding between our next summary table: 

        st.markdown("")
        st.markdown("")
        #endregion

        #endregion



#============================================================================================================================================================
#Using a "try/except block to return an error message if the user isn't logged in yet"
else:
    st.error("You must be logged in to access this page! Please return to the Home Page and login.")


