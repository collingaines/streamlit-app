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

#===========================================================================
#Importing our libraries for our AgGrid table:
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

from openpyxl import Workbook
import io

#Connecting to our Pyramid Analytics database
#os.chdir('C:\\Users\\colli\\AppData\\Local\\Programs\\Python\\Python310\\My_Python_Scripts\\Main_App_Folder_2025\\streamlit_app')
conn = sqlite3.connect('Pyramid_Analytics_Database.db')
c = conn.cursor()


#endregion


#=====================================================================================================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================================================================================================
#SECTION #1 | SETTING UP THE PAGE CONFIGURATIONS: 
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
        st.title('Bonus Tracking')


        st.markdown(
            """
            A portal for reviewing current and historical bonus values for trade superintendents, foremen, and projects.
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

        #===========================================
        #Filter by Bonus/CTC Period

        #===========
        #Bonus Period:
        bonusPeriodList = []

        #Creating a list of bonus periods from our "bonusPeriodDateRangeDictionary" dictionary created in section #2:
        for key,values in bonusPeriodDateRangeDictionary.items():
            if key!='Pre Jan 2024':
                bonusPeriodList.append(key)

        #Converting this list to a tuple to feed to our dropdown box:
        bpTuple = tuple(bonusPeriodList)

        #Finally, creating our dropdown menu:
        with col1: 
            bpOptions = st.selectbox(
            "Filter by Bonus Period",
            bpTuple,
            index=None,
            placeholder="Select a bonus period...",
            )

        #===========
        #CTC Period:
        ctcPeriodList = []

        #Creating a list of CTC periods from our "CTCcutoffDictionary" dictionary created in section #2:
        for key,values in CTCcutoffDictionary.items():
            ctcPeriodList.append(key)

        #Converting this list to a tuple to feed to our dropdown box:
        ctcPeriodTuple = tuple(ctcPeriodList)

        with col2:
            monthOptions = st.selectbox(
            "Filter By Month/Year",
            ctcPeriodTuple,
            index=None,
            placeholder="Select a month/year...",
            )

        
            
        #==============================================================================================================================
        #Building a period selection variable based on the options selected in the selectboxes above: 
        latestBonusPeriod = 'Q3&4: 2024'

        #Our default value for the period selection will be the current bonus period
        if bpOptions==None and monthOptions==None:
            periodSelection = latestBonusPeriod

        #If they apply a bonus period filter:
        elif bpOptions!=None and monthOptions==None: 
            periodSelection=bpOptions

        #If they apply a month/year filter: 
        elif bpOptions==None and monthOptions!=None: 
            periodSelection=monthOptions

        #If the user selects a bad combo of filters, we want to display a warning message: 
        else:
            st.warning("Invalid filter chosen! You must choose either a Bonus Period OR Month/Year, not both. Defaulting to latest bonus period ({})".format(latestBonusPeriod))
            periodSelection = latestBonusPeriod

        #==============================================================================================================================
        #Here we will calculate our "Projection Ratio" which is essentially just the time % complete of the selected bonus period used to project final bonuses
        
        #======================================================================
        #If our filter selection is a bonus period we will pull data from our "Master_CostCode_Data" database: 
        if 'Q' in periodSelection:
            bpEndDate = bonusPeriodDateRangeDictionary[periodSelection][0]
            today = datetime.datetime.today()

            #=======================
            #If the current date is past the end date of the bonus period, then the projection ratio will be equal to 1:
            if today>bpEndDate:
                projectionRatio=1

            #=======================
            #If not, then we are going to want to do some funky shit
            else:
                monthNum = int(str(today)[5:7])

                if monthNum in [1,2,3,4,5,6]:
                    projectionRatio=6/monthNum
                else:
                    projectionRatio=6/(monthNum-6)


        #======================================================================
        #If our filter selection is a month/year period, our projected bonus amount will be the same as the current bonus amount: 
        elif '202' in periodSelection:
            projectionRatio=1 

        
        #==============================================================================================================================
        #Displaying the selected filter period on the app page:
        st.markdown("")
        st.markdown("")

        st.subheader("Filter Period=> {}".format(periodSelection))
        
            
        st.divider()

        #endregion

        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION C | Top of page summary values:
        #region CLICK HERE TO EXPAND SECTION

        #==============================================================================================================================
        #Genrating our values:
        #region


        #=================================================================
        #Connecting to our Pyramid Analytics database
        os.chdir('C:\\Users\\colli\\AppData\\Local\\Programs\\Python\\Python310\\My_Python_Scripts\\Main_App_Folder_2025\\streamlit_app')
        conn = sqlite3.connect('Pyramid_Analytics_Database.db')
        c = conn.cursor()


        #=================================================================
        #Calculating our Trade $O/U Budget Section:

        #If our filter selection is a bonus period we will pull data from our "Master_CostCode_Data" database: 
        if 'Q' in periodSelection:
            query = c.execute("SELECT * FROM Master_CostCode_Data WHERE bonusPeriod='{}'".format(periodSelection))
            values = c.fetchall()

        #If our filter selection is a month/year period we will pull data from our "Master_CostCode_Data" database: 
        elif '202' in periodSelection:
            query = c.execute("SELECT * FROM Master_CostCode_Data WHERE ctcPeriod='{}'".format(periodSelection))
            values = c.fetchall()

        #Calculating our Trade $O/U Budget Section:
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

           
        #=================================================================
        #Calculating our "Avg. Trade Super Bonus" value:
        #====================
        #Querying our database: 
        if "Q" in periodSelection:
            tradeSuperBonusQuery = c.execute("SELECT * FROM Trade_Superintendent_Bonus_Summary WHERE bonusPeriod='{}'".format(periodSelection))
            tradeSuperBonusValues = c.fetchall()
        elif "202" in periodSelection: 
            tradeSuperBonusQuery = c.execute("SELECT * FROM Trade_Superintendent_Bonus_Summary WHERE ctcPeriod='{}'".format(periodSelection))
            tradeSuperBonusValues = c.fetchall()
        else:
            pass
        
        #====================
        #Calculating the total number of trade supers this period
        tradeSuperList = []

        for i in range(len(tradeSuperBonusValues)):
            tradeSuperName = tradeSuperBonusValues[i][2]

            if tradeSuperName not in tradeSuperList:
                tradeSuperList.append(tradeSuperName)

        tradeSuperCount = len(tradeSuperList)

        #====================
        #Adding up the total trade super bonus amount for this period, and calculating the average: 
        totalTradeSuperBonus = 0

        for i in range(len(tradeSuperBonusValues)):
            totalTradeSuperBonus = totalTradeSuperBonus+float(tradeSuperBonusValues[i][17])

        averageTradeSuperBonus = round(totalTradeSuperBonus/tradeSuperCount,2)


        #=================================================================
        #Calculating our "Avg. Foreman Bonus" value:
        #====================
        #Querying our database: 
        if "Q" in periodSelection:
            foremanBonusQuery = c.execute("SELECT * FROM Foreman_Bonus_Summary_Table WHERE bonusPeriod='{}'".format(periodSelection))
            foremanBonusValues = c.fetchall()
        elif "202" in periodSelection: 
            foremanBonusQuery = c.execute("SELECT * FROM Foreman_Bonus_Summary_Table WHERE ctcPeriod='{}'".format(periodSelection))
            foremanBonusValues = c.fetchall()
        else:
            pass
        
        #====================
        #Creating a list of foreman that we want to evaluate bonuses for:
        entryUserQuery = c.execute("SELECT * FROM Users WHERE position='{}'".format('Foreman'))
        entryUserValues = c.fetchall()

        foremanNameList = []

        for i in range(len(entryUserValues)):
            foremanName = entryUserValues[i][2]
            foremanTrade = entryUserValues[i][5]

            if foremanTrade in ["Concrete", 'Earthwork', 'Utilities']:
                foremanNameList.append(foremanName)


        #====================
        #Adding up the total trade super bonus amount for this period, and calculating the average: 
        totalforemanBonus = 0
        foremanIncludedList = []

        for i in range(len(foremanBonusValues)):
            foremanName = foremanBonusValues[i][2]

            #If the foreman is not in our list of foreman that we want to evaluate bonuses for created above, we will not add this entry to the total
            if foremanName in foremanNameList:
                totalforemanBonus = totalforemanBonus+float(foremanBonusValues[i][16])
                #The "foremanIncludedList" is a list that I will use to keep track of how many foreman have bonus values this period
                if foremanName not in foremanIncludedList:
                    foremanIncludedList.append(foremanName)

        #====================
        #Calculating the average foreman bonus
        foremanCount = len(foremanIncludedList)

        averageforemanBonus = round(totalforemanBonus/foremanCount,2)



        #=================================================================
        #Calculating our "Total Trade Pool" value:
        #====================
        #Querying our database: 
        if "Q" in periodSelection:
            projectBonusQuery = c.execute("SELECT * FROM Project_Bonus_Summary_Table WHERE bonusPeriod='{}'".format(periodSelection))
            projectBonusValues = c.fetchall()
        elif "202" in periodSelection: 
            projectBonusQuery = c.execute("SELECT * FROM Project_Bonus_Summary_Table WHERE ctcPeriod='{}'".format(periodSelection))
            projectBonusValues = c.fetchall()
        else:
            pass
        
        #====================
        #Adding up the total trade pool amount:
        totalTradePool = 0

        for i in range(len(projectBonusValues)):
            tradePoolContribution = float(projectBonusValues[i][9])
            totalTradePool = totalTradePool + tradePoolContribution



        #endregion

        #==============================================================================================================================
        #Displaying values on the application page:
        #region 

        #================================================
        #Creating our columns:
        col1, col2, col3, col4 = st.columns(4)

        #================================================
        #Trade $O/U Budget
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
            st.subheader("Avg. Trade Super Bonus")

            #If the $ amount is positive, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if averageTradeSuperBonus>=0:
                st.success("$ "+format_with_commas(round(averageTradeSuperBonus,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number
            else:
                st.error("$ "+format_with_commas(round(averageTradeSuperBonus,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number

        #================================================
        #Paperwork:
        with col3:
            st.subheader("Avg. Foreman Bonus")

            #If the $ amount is positive, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if averageforemanBonus>=0:
                st.success("$ "+format_with_commas(round(averageforemanBonus,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number
            else:
                st.error("$ "+format_with_commas(round(averageforemanBonus,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number
        
        #================================================
        #Safety Incidents:
        with col4:
            st.subheader("Total Trade Pool")

            #If the $ amount is positive, we want to display it as a green success message on the app page. If not, then we will show it as a red error message: 
            if totalTradePool>=0:
                st.success("$ "+format_with_commas(round(totalTradePool,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number
            else:
                st.error("$ "+format_with_commas(round(totalTradePool,2))) #Using our "format_with_commas" fuction defined at the top of the page to comma delineate number

        st.divider()

        #endregion


        #endregion

        
        #=====================================================================================================================================================================================
        #=====================================================================================================================================================================================
        #SECTION D | Trade Superintendent Summary Section:
        #region CLICK HERE TO EXPAND SECTION

        #========================================================================================================================================
        #SECTION D-1 | Creating a dictionary of values to populate our application table:
        #region

        tradeSuperValuesDict = {}

        #===========================================================================
        #If our filter selection is for a bonus period, we are going to want to add up all of the ctc period values returned by our query: 
        if "Q" in periodSelection:
            tradeSuperBonusQuery = c.execute("SELECT * FROM Trade_Superintendent_Bonus_Summary WHERE bonusPeriod='{}'".format(periodSelection))
            tradeSuperBonusValues = c.fetchall()

            
            #Iterrating through our database list of values and adding up the totals for each ccType:
            for i in range(len(tradeSuperBonusValues)):
                #==================================
                #Defining some initial values:
                tradeSuper = tradeSuperBonusValues[i][2]
                trade = tradeSuperBonusValues[i][1]
                ccType = tradeSuperBonusValues[i][3]

                totalCost = float(tradeSuperBonusValues[i][4])
                totalEarned = float(tradeSuperBonusValues[i][5])
                totalOUbudget = float(tradeSuperBonusValues[i][6])
                totalPF = float(tradeSuperBonusValues[i][7])
                totalPaperwork = tradeSuperBonusValues[i][8]
                totalSafetyIncidents = float(tradeSuperBonusValues[i][9])
                totalBasePFdelta = float(tradeSuperBonusValues[i][10])
                totalPerformanceBonus = float(tradeSuperBonusValues[i][13])
                totalPaperworkDeduct = float(tradeSuperBonusValues[i][14])
                totalSafetyDeduct = float(tradeSuperBonusValues[i][15])
                totalPoolShare = float(tradeSuperBonusValues[i][16])
                totalTotalBonus = float(tradeSuperBonusValues[i][17])
                bonusAddOns = float(tradeSuperBonusValues[i][23])

                #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                projectedBonus = totalTotalBonus*projectionRatio

                #==================================
                #Adding the CC type row values to our dictionary:
                key = (tradeSuper, trade, ccType)

                #If this key is already in our dictonary, let's add these values to our existing dictionary entry: 
                if key in tradeSuperValuesDict:
                    newCost = totalCost + tradeSuperValuesDict[key][0]
                    newEarned = totalEarned + tradeSuperValuesDict[key][1]
                    newOUbudget = totalOUbudget + tradeSuperValuesDict[key][2]
                    newSafetyIncidents = totalSafetyIncidents + tradeSuperValuesDict[key][5]
                    newBasePFdelta = totalBasePFdelta + tradeSuperValuesDict[key][6]
                    newPerformanceBonus = totalPerformanceBonus + tradeSuperValuesDict[key][7]
                    newPaperworkDeduct = totalPaperworkDeduct + tradeSuperValuesDict[key][8]
                    newSafetyDeduct = totalSafetyDeduct + tradeSuperValuesDict[key][9]
                    newTotalPoolShare = totalPoolShare + tradeSuperValuesDict[key][10]
                    newTotalTotalBonus = totalTotalBonus + tradeSuperValuesDict[key][11]
                    newBonusAddOns = bonusAddOns + tradeSuperValuesDict[key][13]

                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedBonus = newTotalTotalBonus*projectionRatio

                    #The new total PF will have to be recalcd as well:
                    if newCost!=0:
                        newPF = newEarned/newCost
                    else:
                        newPF = 1

                    tradeSuperValuesDict[(tradeSuper, trade, ccType)] = [newCost, newEarned, newOUbudget, newPF, '', newSafetyIncidents, newBasePFdelta, newPerformanceBonus, newPaperworkDeduct, newSafetyDeduct, newTotalPoolShare, newTotalTotalBonus, projectedBonus, newBonusAddOns]
                #If not, we will add these values straight to our dictionary:
                else:
                    tradeSuperValuesDict[(tradeSuper, trade, ccType)] = [totalCost, totalEarned, totalOUbudget, totalPF, '', totalSafetyIncidents, totalBasePFdelta, totalPerformanceBonus, totalPaperworkDeduct, totalSafetyDeduct, totalPoolShare, totalTotalBonus, projectedBonus, bonusAddOns]

                #==================================
                #Updating our totals header row values in our dictionary as well: 
                totalsKey = (tradeSuper, trade, trade+' - '+tradeSuper)

                #==================================
                #If this key is already in our dictonary, let's add these values to our existing dictionary entry: 
                if totalsKey in tradeSuperValuesDict:
                    newCost = totalCost + tradeSuperValuesDict[totalsKey][0]
                    newEarned = totalEarned + tradeSuperValuesDict[totalsKey][1]
                    newOUbudget = totalOUbudget + tradeSuperValuesDict[totalsKey][2]
                    newSafetyIncidents = totalSafetyIncidents + tradeSuperValuesDict[totalsKey][5]
                    newBasePFdelta = totalBasePFdelta + tradeSuperValuesDict[totalsKey][6]
                    newPerformanceBonus = totalPerformanceBonus + tradeSuperValuesDict[totalsKey][7]
                    newPaperworkDeduct = totalPaperworkDeduct + tradeSuperValuesDict[totalsKey][8]
                    newSafetyDeduct = totalSafetyDeduct + tradeSuperValuesDict[totalsKey][9]
                    newTotalPoolShare = totalPoolShare + tradeSuperValuesDict[totalsKey][10]
                    newTotalTotalBonus = totalTotalBonus + tradeSuperValuesDict[totalsKey][11]
                    newBonusAddOns = bonusAddOns + tradeSuperValuesDict[key][13]

                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedBonus = newTotalTotalBonus*projectionRatio

                    #The paperwork value will have to be broken out and added seperately due to the fact that it is a string: 
                    #IMPORTANT! Because each cc type entry in our database contains a paperwork column value with the FULL paperwork amount, we want to divide each added entry by 4: 
                    newOT = (float(totalPaperwork[0:totalPaperwork.index('/')])/4) + float(tradeSuperValuesDict[totalsKey][4][0:tradeSuperValuesDict[totalsKey][4].index('/')])
                    newTotal = (float(totalPaperwork[totalPaperwork.index('/')+1:totalPaperwork.index(' ')])/4) + float(tradeSuperValuesDict[totalsKey][4][tradeSuperValuesDict[totalsKey][4].index('/')+1:tradeSuperValuesDict[totalsKey][4].index(' ')])
                    
                    #Calculating our new percent
                    if newTotal!=0:
                        newPercent = newOT/newTotal
                    else:
                        newPercent = 0

                    #Defining our new paperwork value:
                    newPaperwork = str(newOT)+'/'+str(newTotal)+' ('+str(round(newPercent*100,2))+'%)'

                    #The new total PF will have to be recalcd as well:
                    if newCost!=0:
                        newPF = newEarned/newCost
                    else:
                        newPF = 1

                    tradeSuperValuesDict[totalsKey] = [newCost, newEarned, newOUbudget, newPF, newPaperwork, newSafetyIncidents, newBasePFdelta, newPerformanceBonus, newPaperworkDeduct, newSafetyDeduct, newTotalPoolShare, newTotalTotalBonus, projectedBonus, newBonusAddOns*2]
                
                #==================================
                #If not, we will add these values straight to our dictionary:
                else:
                    #The paperwork value will have to be broken out and added seperately due to the fact that it is a string: 
                    newOT = int(totalPaperwork[0:totalPaperwork.index('/')])
                    newTotal = int(totalPaperwork[totalPaperwork.index('/')+1:totalPaperwork.index(' ')])
                    
                    #Dividing our total paperwork values by 4 because in our database there is an entry for each CC type that contains the total paperwork for that period:
                    newOT = newOT/4
                    newTotal = newTotal/4

                    #Calculating our new percent
                    if newTotal!=0:
                        newPercent = newOT/newTotal
                    else:
                        newPercent = 0

                    #Defining our new paperwork value:
                    newPaperwork = str(newOT)+'/'+str(newTotal)+' ('+str(round(newPercent*100,2))+'%)'

                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedBonus = totalTotalBonus*projectionRatio

                    #Updating our dictionary: 
                    tradeSuperValuesDict[totalsKey] = [totalCost, totalEarned, totalOUbudget, totalPF, newPaperwork, totalSafetyIncidents, totalBasePFdelta, totalPerformanceBonus, totalPaperworkDeduct, totalSafetyDeduct, totalPoolShare, totalTotalBonus, projectedBonus, bonusAddOns]


        #===========================================================================
        #If our filter selection is for a CTC period, we are just going to pull the needed values from our database and add them to the list:
        else:
            tradeSuperBonusQuery = c.execute("SELECT * FROM Trade_Superintendent_Bonus_Summary WHERE ctcPeriod='{}'".format(periodSelection))
            tradeSuperBonusValues = c.fetchall()

            #Iterrating through our database list of values and adding up the totals for each ccType:
            for i in range(len(tradeSuperBonusValues)):
                #Defining some initial values:
                tradeSuper = tradeSuperBonusValues[i][2]
                trade = tradeSuperBonusValues[i][1]
                ccType = tradeSuperBonusValues[i][3]

                totalCost = float(tradeSuperBonusValues[i][4])
                totalEarned = float(tradeSuperBonusValues[i][5])
                totalOUbudget = float(tradeSuperBonusValues[i][6])
                totalPF = float(tradeSuperBonusValues[i][7])
                totalPaperwork = tradeSuperBonusValues[i][8]
                totalSafetyIncidents = float(tradeSuperBonusValues[i][9])
                totalBasePFdelta = float(tradeSuperBonusValues[i][10])
                totalPerformanceBonus = float(tradeSuperBonusValues[i][13])
                totalPaperworkDeduct = float(tradeSuperBonusValues[i][14])
                totalSafetyDeduct = float(tradeSuperBonusValues[i][15])
                totalPoolShare = float(tradeSuperBonusValues[i][16])
                totalTotalBonus = float(tradeSuperBonusValues[i][17])
                bonusAddOns = float(tradeSuperBonusValues[i][23])

                #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                projectedBonus = totalTotalBonus*projectionRatio

                #==================================
                #Updating our CC type dictionary:
                tradeSuperValuesDict[(tradeSuper, trade, ccType)] = [totalCost, totalEarned, totalOUbudget, totalPF, totalPaperwork, totalSafetyIncidents, totalBasePFdelta, totalPerformanceBonus, totalPaperworkDeduct, totalSafetyDeduct, totalPoolShare, totalTotalBonus, projectedBonus, bonusAddOns]

                #==================================
                #Updating our totals header row values in our dictionary as well: 
                totalsKey = (tradeSuper, trade, trade+' - '+tradeSuper)

                #If this key is already in our dictonary, let's add these values to our existing dictionary entry: 
                if totalsKey in tradeSuperValuesDict:
                    newCost = totalCost + tradeSuperValuesDict[totalsKey][0]
                    newEarned = totalEarned + tradeSuperValuesDict[totalsKey][1]
                    newOUbudget = totalOUbudget + tradeSuperValuesDict[totalsKey][2]
                    newSafetyIncidents = totalSafetyIncidents + tradeSuperValuesDict[totalsKey][5]
                    newBasePFdelta = totalBasePFdelta + tradeSuperValuesDict[totalsKey][6]
                    newPerformanceBonus = totalPerformanceBonus + tradeSuperValuesDict[totalsKey][7]
                    newPaperworkDeduct = totalPaperworkDeduct + tradeSuperValuesDict[totalsKey][8]
                    newSafetyDeduct = totalSafetyDeduct + tradeSuperValuesDict[totalsKey][9]
                    newTotalPoolShare = totalPoolShare + tradeSuperValuesDict[totalsKey][10]
                    newTotalTotalBonus = totalTotalBonus + tradeSuperValuesDict[totalsKey][11]
                    newBonusAddOns = bonusAddOns + tradeSuperValuesDict[key][13]

                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedBonus = newTotalTotalBonus*projectionRatio

                    #The paperwork value will have to be broken out and added seperately due to the fact that it is a string: 
                    #IMPORTANT! Be sure to divide the paperwork value by 4, as the total paperwork value is listed for each cost type in the database
                    newOT = (int(float(totalPaperwork[0:totalPaperwork.index('/')])/4)) + int(float(tradeSuperValuesDict[totalsKey][4][0:tradeSuperValuesDict[totalsKey][4].index('/')]))
                    newTotal = (int(float(totalPaperwork[totalPaperwork.index('/')+1:totalPaperwork.index(' ')])/4))+int(float(tradeSuperValuesDict[totalsKey][4][tradeSuperValuesDict[totalsKey][4].index('/')+1:tradeSuperValuesDict[totalsKey][4].index(' ')]))
                    if newTotal!=0:
                        newPercent = newOT/newTotal
                    else:
                        newPercent = 0

                    newPaperwork = str(newOT)+'/'+str(newTotal)+' ('+str(round(newPercent*100,2))+'%)'

                    #The new total PF will have to be recalcd as well:
                    if newCost!=0:
                        newPF = newEarned/newCost
                    else:
                        newPF = 1

                    #Updating our dictionary: 
                    tradeSuperValuesDict[totalsKey] = [newCost, newEarned, newOUbudget, newPF, newPaperwork, newSafetyIncidents, newBasePFdelta, newPerformanceBonus, newPaperworkDeduct, newSafetyDeduct, newTotalPoolShare, newTotalTotalBonus, projectedBonus, newBonusAddOns]
                
                #If not, we will add these values straight to our dictionary:
                else:
                    #The paperwork value will have to be broken out and added seperately due to the fact that it is a string: 
                    #IMPORTANT! Be sure to divide the paperwork value by 4, as the total paperwork value is listed for each cost type in the database
                    newOT = int(totalPaperwork[0:totalPaperwork.index('/')])/4
                    newTotal = int(totalPaperwork[totalPaperwork.index('/')+1:totalPaperwork.index(' ')])/4
                    if newTotal!=0:
                        newPercent = newOT/newTotal
                    else:
                        newPercent = 0

                    newPaperwork = str(newOT)+'/'+str(newTotal)+' ('+str(round(newPercent*100,2))+'%)'
                    
                    #Updating our dictionary: 
                    tradeSuperValuesDict[totalsKey] = [totalCost, totalEarned, totalOUbudget, totalPF, newPaperwork, totalSafetyIncidents, totalBasePFdelta, totalPerformanceBonus, totalPaperworkDeduct, totalSafetyDeduct, totalPoolShare, totalTotalBonus, projectedBonus, bonusAddOns]
        
        #endregion

        #========================================================================================================================================
        #SECTION D-2 | Reformatting our values into a list that can be used to populate our table
        #region

        #===========================================================================
        #Creating a list of dictionary keys to be used to populate our final list for our table in the order that we'd like to see our values displayed:
        keyList = []

        #First, creating a list in the order we want our values:
        for key,values in tradeSuperValuesDict.items():
            tradeSuper = key[0]
            trade = key[1]
            ccType = key[2]
            if '-' in ccType:
                #Adding in our column header row key: 
                keyList.append(key)

                #Adding in the production row key:
                keyList.append((key[0], key[1], 'Production'))

                #Adding in the material row key:
                keyList.append((key[0], key[1], 'Material'))

                #Adding in the COR row key:
                keyList.append((key[0], key[1], 'COR'))

                #Adding in the rework row key:
                keyList.append((key[0], key[1], 'Rework'))


        #===========================================================================
        #Reformtting the data in the dictionary created above into a list to be fed into the pandas dataframe. Here we will make sure that the items in the list are in the order that we want to see them in the table:
        data_values = []

        for i in range(len(keyList)):
            entryKey = keyList[i]

            ccType = entryKey[2]

            #=========================================
            #If this is a header row, then we want to add values for all the columns: 
            if "-" in ccType: 
                totalCost = tradeSuperValuesDict[entryKey][0]
                totalEarned = tradeSuperValuesDict[entryKey][1]
                totalOUbudget = tradeSuperValuesDict[entryKey][2]
                totalPF = tradeSuperValuesDict[entryKey][3]
                paperwork = tradeSuperValuesDict[entryKey][4]
                safetyIncidents = round(tradeSuperValuesDict[entryKey][5])
                basePFdelta = tradeSuperValuesDict[entryKey][6]
                performanceBonus = tradeSuperValuesDict[entryKey][7]
                paperworkDeduct = tradeSuperValuesDict[entryKey][8]
                safetyDeduct = tradeSuperValuesDict[entryKey][9]
                poolShare = tradeSuperValuesDict[entryKey][10]
                totalBonus = tradeSuperValuesDict[entryKey][11]
                totalProjectBonus = tradeSuperValuesDict[entryKey][12]
                bonusAddOn = tradeSuperValuesDict[entryKey][13]

                #Rounding our paperwork values and reformatting: 
                ontime = int(float(paperwork[0:paperwork.index('/')]))
                total = int(float(paperwork[paperwork.index('/')+1:paperwork.index(' ')]))

                if total!=0:
                    percent = ontime/total
                else:
                    percent = 0

                newPaperwork = str(ontime)+'/'+str(total)+' ('+str(round(percent*100,2))+'%)'
                
                #Updating our list:
                data_values.append([ccType, totalCost, totalEarned, totalOUbudget, totalPF, newPaperwork, safetyIncidents, basePFdelta, performanceBonus, paperworkDeduct, safetyDeduct, poolShare, bonusAddOn, totalBonus, totalProjectBonus])
            
            #=========================================
            #If it is not a header row, then we will want to add a blank string for some values and omit others from our list:
            else:
                totalCost = tradeSuperValuesDict[entryKey][0]
                totalEarned = tradeSuperValuesDict[entryKey][1]
                totalOUbudget = tradeSuperValuesDict[entryKey][2]
                totalPF = tradeSuperValuesDict[entryKey][3]
                paperwork = ''
                safetyIncidents = ''
                basePFdelta = tradeSuperValuesDict[entryKey][6]
                performanceBonus = tradeSuperValuesDict[entryKey][7]
            

                #Updating our list:
                data_values.append([ccType, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, performanceBonus])


        #===========================================================================
        #Finally, defining column header labels for table and updating our dataframe with our data calculated above: 
        column_headers = ['Trade Superintendent/CC Type', 'Total Cost', 'Total Earned', '$O/U Budget', 'PF', 'Paperwork %', 'Safety Incidents', 'Base PF Delta', 'Performance Bonus', 'Paperwork Deduct', 'Safety Deduct', 'Pool Share', 'Bonus Add Ons', 'Total Bonus', 'Projected Bonus']


        #===========================================================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        tradeSuperTableData = create_dataframe(column_headers, data_values)

        #endregion

        #========================================================================================================================================
        #SECTION D-3 | Define functions to apply formatting to table:
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
            value_to_highlight = ['Concrete - Christopher Roberts', 'Earthwork - Gabino Gonzalez', 'Utilities - Miguel Soto', 'Utilities - Jesus Mosqueda']
            if row.iloc[0] in value_to_highlight:
                return [
                    'background-color: #D3D3D3; font-weight: bold; font-size: 20px'
                ] * len(row)
            else:
                return [''] * len(row)
            
        #===========================================================================
        #Defining a styling function to color PF cells red if they are below a 1.0 and green if they are above a 1.0:
        def highlight_ratio(val):
            if pd.isna(val):
                return 'background-color: white; color: white'  # Make NaN cells appear blank
            elif val >= 1:
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
        #SECTION D-4 | Generate summary table and apply formatting:
        #region CLICK HERE TO EXPAND SECTION

        #===========================================================================
        #Applying number formatting to each column: 
        tradeSuperTableData['Total Cost'] = tradeSuperTableData['Total Cost'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['Total Earned'] = tradeSuperTableData['Total Earned'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['$O/U Budget'] = tradeSuperTableData['$O/U Budget'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['PF'] = tradeSuperTableData['PF'].round(2)
        tradeSuperTableData['Base PF Delta'] = tradeSuperTableData['Base PF Delta'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['Performance Bonus'] = tradeSuperTableData['Performance Bonus'].apply(lambda x: f'${x:,.2f}')
        tradeSuperTableData['Paperwork Deduct'] = tradeSuperTableData['Paperwork Deduct'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Safety Deduct'] = tradeSuperTableData['Safety Deduct'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Pool Share'] = tradeSuperTableData['Pool Share'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Bonus Add Ons'] = tradeSuperTableData['Bonus Add Ons'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Total Bonus'] = tradeSuperTableData['Total Bonus'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')
        tradeSuperTableData['Projected Bonus'] = tradeSuperTableData['Projected Bonus'].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else '')

        #===========================================================================
        #Applying the grey row highlighting to our trade summary rows:
        styled_df = tradeSuperTableData.style.apply(highlight_and_bold_rows, axis=1)

        #===========================================================================
        #Coloring specified column cells red/green based on being a negative/positive $ value:
        columns_to_color = ['Total Bonus', 'Projected Bonus']
        
        for col in columns_to_color:
            styled_df = styled_df.applymap(color_negative_red, subset=[col])

        #===========================================================================
        #Specifying the columns that we'd like to color the number of and applying the coloring:
        styled_df = styled_df.applymap(color_dollar_values, subset=['$O/U Budget', 'Base PF Delta', 'Performance Bonus', 'Paperwork Deduct', 'Safety Deduct', 'Pool Share', 'Bonus Add Ons'])

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
                'Paperwork Deduct': st.column_config.TextColumn('Paperwork Deduct', help='Paperwork Deduction = Total Bonus X (100% - % On Time) X -0.2'),
                'Safety Deduct': st.column_config.TextColumn('Safety Deduct', help='Safety Deduction = Total Bonus X # of Safety Incidents X -0.3'),
                'Pool Share': st.column_config.TextColumn('Pool Share', help='Trade superintendents are given 29% of the total trade bonus pool, which is divided equally among all active trade superintendents'),
                'Bonus Add Ons': st.column_config.TextColumn('Bonus Add Ons', help='Additions/subtractions to the total bonus added at the discretion of Zack/Derek. See "" report on the "Data Reports & Analytics" tab for a description of what the reasons are for any values here.'),
                'Total Bonus': st.column_config.TextColumn('Total Bonus', help='Total Bonus = Performance Bonus + Paperwork Deduct + Safety Deduct + Pool Share + Bonus Add Ons'),
                'Projected Bonus': st.column_config.TextColumn('Projected Bonus', help='Total projected bonus $ amount for the 6 month bonus period')
            },
            height=800,
            use_container_width=True,
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
        #SECTION E-1 | Creating a dictionary of values to populate our application table:
        #region CLICK HERE TO EXPAND SECTION

        foremanValueDictionary = {}

        #===========================================================================
        #Generating values for our foreman summary table:
        #region

        #===========================================================================
        #Creating a list of foreman that we want to display bonuses for:
        entryUserQuery = c.execute("SELECT * FROM Users WHERE position='{}'".format('Foreman'))
        entryUserValues = c.fetchall()

        foremanNameList = []

        for i in range(len(entryUserValues)):
            foremanName = entryUserValues[i][2]
            foremanTrade = entryUserValues[i][5]
            terminationDate = entryUserValues[i][9]

            #We will only want to see foremen in the main trades on this table: 
            if foremanTrade in ["Concrete", 'Earthwork', 'Utilities']:
                #We will only want to see currently employed foremen as our default to view in our table:
                if terminationDate=='':
                    foremanNameList.append(foremanName)
        

        #===========================================================================
        #If our filter selection is for a bonus period, we are going to want to add up all of the ctc period values returned by our query: 
        if "Q" in periodSelection:
            foremanBonusQuery = c.execute("SELECT * FROM Foreman_Bonus_Summary_Table WHERE bonusPeriod='{}'".format(periodSelection))
            foremanBonusValues = c.fetchall()

            #If this foreman is in our list of forement that we want to display then we will perform our calcs:
            for i in range(len(foremanBonusValues)):
                foremanName = foremanBonusValues[i][2]

                if foremanName in foremanNameList:
                    #==================================
                    #Defining some initial values:
                    foremanTrade = foremanBonusValues[i][1]
                    totalCost = float(foremanBonusValues[i][3])
                    totalEarned = float(foremanBonusValues[i][4])
                    totalOUbudget = float(foremanBonusValues[i][5])
                    totalPF = float(foremanBonusValues[i][6])
                    totalPaperwork = foremanBonusValues[i][7]
                    totalSafetyIncidents = float(foremanBonusValues[i][8])
                    totalBasePFdelta = float(foremanBonusValues[i][9])
                    totalPerformanceBonus = float(foremanBonusValues[i][12])
                    totalPaperworkDeduct = float(foremanBonusValues[i][13])
                    totalSafetyDeduct = float(foremanBonusValues[i][14])
                    totalPoolShare = float(foremanBonusValues[i][15])
                    totalTotalBonus = float(foremanBonusValues[i][16])
                    bonusAddOns = float(foremanBonusValues[i][29])

                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedBonus = totalTotalBonus*projectionRatio 
                    

                    #==================================
                    #Defining the key for our dictionary:
                    key = (foremanName)

                    #==================================
                    #If this key is already in our dictonary, let's add these values to our existing dictionary entry: 
                    if key in foremanValueDictionary:
                        newCost = totalCost + foremanValueDictionary[key][0]
                        newEarned = totalEarned + foremanValueDictionary[key][1]
                        newOUbudget = totalOUbudget + foremanValueDictionary[key][2]
                        newSafetyIncidents = totalSafetyIncidents + foremanValueDictionary[key][5]
                        newBasePFdelta = totalBasePFdelta + foremanValueDictionary[key][6]
                        newPerformanceBonus = totalPerformanceBonus + foremanValueDictionary[key][7]
                        newPaperworkDeduct = totalPaperworkDeduct + foremanValueDictionary[key][8]
                        newSafetyDeduct = totalSafetyDeduct + foremanValueDictionary[key][9]
                        newTotalPoolShare = totalPoolShare + foremanValueDictionary[key][10]
                        newTotalTotalBonus = totalTotalBonus + foremanValueDictionary[key][11]
                        newBonusAddOns = bonusAddOns + foremanValueDictionary[key][14]

                        #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                        projectedBonus = newTotalTotalBonus*projectionRatio

                        #The paperwork value will have to be broken out and added seperately due to the fact that it is a string:  
                        newOT = float(totalPaperwork[0:totalPaperwork.index('/')]) + float(foremanValueDictionary[key][4][0:foremanValueDictionary[key][4].index('/')])
                        newTotal = float(totalPaperwork[totalPaperwork.index('/')+1:totalPaperwork.index(' ')]) + float(foremanValueDictionary[key][4][foremanValueDictionary[key][4].index('/')+1:foremanValueDictionary[key][4].index(' ')])
                        
                        #Calculating our new percent
                        if newTotal!=0:
                            newPercent = newOT/newTotal
                        else:
                            newPercent = 0

                        #Defining our new paperwork value:
                        newPaperwork = str(newOT)+'/'+str(newTotal)+' ('+str(round(newPercent*100,2))+'%)'

                        #The new total PF will have to be recalcd as well:
                        if newCost!=0:
                            newPF = newEarned/newCost
                        else:
                            newPF = 1

                        foremanValueDictionary[key] = [newCost, newEarned, newOUbudget, newPF, newPaperwork, newSafetyIncidents, newBasePFdelta, newPerformanceBonus, newPaperworkDeduct, newSafetyDeduct, newTotalPoolShare, newTotalTotalBonus, projectedBonus, foremanTrade, newBonusAddOns]
                    #If not, we will add these values straight to our dictionary:
                    else:
                        foremanValueDictionary[key] = [totalCost, totalEarned, totalOUbudget, totalPF, totalPaperwork, totalSafetyIncidents, totalBasePFdelta, totalPerformanceBonus, totalPaperworkDeduct, totalSafetyDeduct, totalPoolShare, totalTotalBonus, projectedBonus, foremanTrade, bonusAddOns]


        #===========================================================================
        #If our filter selection is for a CTC period, we are just going to pull the needed values from our database and add them to the list:
        else:
            foremanBonusQuery = c.execute("SELECT * FROM Foreman_Bonus_Summary_Table WHERE ctcPeriod='{}'".format(periodSelection))
            foremanBonusValues = c.fetchall()

            for i in range(len(foremanBonusValues)):
                foremanName = foremanBonusValues[i][2]

                #If this foreman is in our list of forement that we want to display then we will perform our calcs: 
                if foremanName in foremanNameList:
                    #==================================
                    #Defining some initial values:
                    foremanTrade = foremanBonusValues[i][1]
                    totalCost = float(foremanBonusValues[i][3])
                    totalEarned = float(foremanBonusValues[i][4])
                    totalOUbudget = float(foremanBonusValues[i][5])
                    totalPF = float(foremanBonusValues[i][6])
                    totalPaperwork = foremanBonusValues[i][7]
                    totalSafetyIncidents = float(foremanBonusValues[i][8])
                    totalBasePFdelta = float(foremanBonusValues[i][9])
                    totalPerformanceBonus = float(foremanBonusValues[i][12])
                    totalPaperworkDeduct = float(foremanBonusValues[i][13])
                    totalSafetyDeduct = float(foremanBonusValues[i][14])
                    totalPoolShare = float(foremanBonusValues[i][15])
                    totalTotalBonus = float(foremanBonusValues[i][16])
                    bonusAddOns = float(foremanBonusValues[i][29])

                    #==================================
                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedBonus = newTotalTotalBonus*projectionRatio
                    
                    #==================================
                    #Updating our dictionary:
                    key = foremanName

                    foremanValueDictionary[key] = [totalCost, totalEarned, totalOUbudget, totalPF, totalPaperwork, totalSafetyIncidents, totalBasePFdelta, totalPerformanceBonus, totalPaperworkDeduct, totalSafetyDeduct, totalPoolShare, totalTotalBonus, projectedBonus, foremanTrade, bonusAddOns]

        #endregion


        #===========================================================================
        #Defining column header labels for table and adding our values generated above:
        #region
        column_headers = ['Foreman Name', 'Trade', 'Total Cost', 'Total Earned', '$O/U Budget', 'PF', 'Paperwork', 'Safety Incidents', 'Base PF Delta', 'Performance Bonus', 'Paperwork Deduct', 'Safety Deduct', 'Pool Share', 'Bonus Add Ons', 'Total Bonus', 'Projected Bonus']
        
        data_values = [] #This variable is a nested list that will be entered into our dataframe in the next step: 

        for key,values in foremanValueDictionary.items():
            foreman = key
            trade = values[13]
            totalCost = values[0]
            totalEarned = values[1]
            totalOUbudget = values[2]
            totalPF = values[3]
            paperwork = values[4]
            safetyIncidents = int(values[5])
            basePFdelta = values[6]
            performanceBonus = values[7]
            paperworkDeduct = values[8]
            safetyDeduct = values[9]
            poolShare = values[10]
            totalBonus = values[11]
            projectedBonus = values[12]
            bonusAddOns = values[14]

            #Rounding our paperwork values and reformatting: 
            ontime = int(float(paperwork[0:paperwork.index('/')]))
            total = int(float(paperwork[paperwork.index('/')+1:paperwork.index(' ')]))

            if total!=0:
                percent = ontime/total
            else:
                percent = 0

            newPaperwork = str(ontime)+'/'+str(total)+' ('+str(round(percent*100,2))+'%)'

            #Updating our data list:
            data_values.append([foreman, trade, totalCost, totalEarned, totalOUbudget, totalPF, newPaperwork, safetyIncidents, basePFdelta, performanceBonus, paperworkDeduct, safetyDeduct, poolShare, bonusAddOns, totalBonus, projectedBonus])
            
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
        foremanTableData['Paperwork Deduct'] = foremanTableData['Paperwork Deduct'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Safety Deduct'] = foremanTableData['Safety Deduct'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Pool Share'] = foremanTableData['Pool Share'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Bonus Add Ons'] = foremanTableData['Bonus Add Ons'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Total Bonus'] = foremanTableData['Total Bonus'].apply(lambda x: f'${x:,.2f}')
        foremanTableData['Projected Bonus'] = foremanTableData['Projected Bonus'].apply(lambda x: f'${x:,.2f}')



        #===========================================================================
        #Coloring specified column cells red/green based on being a negative/positive $ value:

        #The "highlight_and_bold_rows" function below is actually not needed for this section, but because i am using the same styling functions from the superintendent table i had to include it
        styled_foreman_df = foremanTableData.style.apply(highlight_and_bold_rows, axis=1)

        #Specifying the columns that we'd like to color the ENTIRE cell of and applying the coloring:
        columns_to_color = ['Total Bonus', 'Projected Bonus'] 
        
        for col in columns_to_color:
            styled_foreman_df = styled_foreman_df.applymap(color_negative_red, subset=[col])

        #Specifying the columns that we'd like to color the number of and applying the coloring:
        styled_foreman_df = styled_foreman_df.applymap(color_dollar_values, subset=['$O/U Budget', 'Base PF Delta', 'Performance Bonus', 'Paperwork Deduct', 'Safety Deduct', 'Pool Share', 'Bonus Add Ons'])

        #===========================================================================
        #Coloring PF column cells red/green based on being a below/above a 1.0 PF:
        styled_foreman_df = styled_foreman_df.applymap(highlight_ratio, subset=['PF'])


        #===========================================================================
        #Displaying our project summary table on the left side of our applicaton page:
        st.subheader("Foreman Summary")

        st.dataframe(
            styled_foreman_df,
            column_config={
                'Foreman Name': st.column_config.TextColumn('Foreman Name', help='Trade & Trade Superintendent Name/ Cost Code Type'),
                'Total Cost': st.column_config.TextColumn('Total Cost', help='Total cost to date this period'),
                'Total Earned': st.column_config.TextColumn('Total Earned', help='Total budget $ earned to date this period'),
                '$O/U Budget': st.column_config.TextColumn("$O/U Budget", help="Total $ difference between cost and earned to date this period"),
                'PF': st.column_config.NumberColumn('PF', help='Performance factor is total $ earned divided by total cost to date this period', format="%.2f"),
                'Paperwork': st.column_config.TextColumn('Paperwork', help='The total number of timecards, JHAs, equipment inspections, and delivery tickets submitted on time to date this period'),
                'Safety Incidents': st.column_config.TextColumn('Safety Incidents', help='The total number of major safety incidents to date this period'),
                'Base PF Delta': st.column_config.TextColumn('Base PF Delta', help='The total $ O/U budget when the trade base PF is factored in'),
                'Performance Bonus': st.column_config.TextColumn('Performance Bonus', help='4% of the Base PF Delta'),
                'Paperwork Deduct': st.column_config.TextColumn('Paperwork Deduct', help='Paperwork Deduction = Total Bonus X (100% - % On Time) X -0.2'),
                'Safety Deduct': st.column_config.TextColumn('Safety Deduct', help='Safety Deduction = Total Bonus X # Safety Incidents X -0.3'),
                'Pool Share': st.column_config.TextColumn('Pool Share', help='Trade superintendents are given 29% of the total trade bonus pool, which is divided equally among all active trade superintendents'),
                'Bonus Add Ons':st.column_config.TextColumn('Bonus Add Ons', help='Additions/subtractions to the total bonus amount for this period added at the discretion of Zack/Derek. To see details about this add on amount, see the "" report on the "Data Reports & Analytics" tab'),
                'Total Bonus': st.column_config.TextColumn('Total Bonus', help='Total Bonus = Performance Bonus + Paperwork Deduct + Safety Deduct + Pool Share + Bonus Add Ons'),
                'Projected Bonus': st.column_config.TextColumn('Projected Bonus', help='Total projected bonus $ amount for the 6 month bonus period')
            },
            height=600,
            use_container_width=True,
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
        #SECTION F | Project/Trade Summary:
        #region CLICK HERE TO EXPAND SECTION

        #========================================================================================================================================
        #SECTION F-1 | Creating a dictionary of values to populate our application table:
        #region CLICK HERE TO EXPAND SECTION

        projectValueDictionary = {}


        #===========================================================================
        #If our filter selection is for a bonus period, we are going to want to add up all of the ctc period values returned by our query: 
        if "Q" in periodSelection:
            projectBonusQuery = c.execute("SELECT * FROM Project_Bonus_Summary_Table WHERE bonusPeriod='{}'".format(periodSelection))
            projectBonusValues = c.fetchall()

            #If this foreman is in our list of forement that we want to display then we will perform our calcs:
            for i in range(len(projectBonusValues)):

                #==================================
                #Defining some initial values:
                projectName = projectBonusValues[i][1]
                totalCost = float(projectBonusValues[i][3])
                totalEarned = float(projectBonusValues[i][4])
                totalOUbudget = float(projectBonusValues[i][5])
                totalPF = float(projectBonusValues[i][6])
                totalBasePFdelta = float(projectBonusValues[i][7])
                totalTradePoolContribution = float(projectBonusValues[i][9])

                #==================================
                #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                projectedTradePoolContribution = totalTradePoolContribution*projectionRatio 
                    
                #==================================
                #Defining the key for our dictionary:
                key = (projectName)

                #==================================
                #If this key is already in our dictonary, let's add these values to our existing dictionary entry: 
                if key in projectValueDictionary:
                    newCost = totalCost + projectValueDictionary[key][0]
                    newEarned = totalEarned + projectValueDictionary[key][1]
                    newOUbudget = totalOUbudget + projectValueDictionary[key][2]
                    newBasePFdelta = totalBasePFdelta + projectValueDictionary[key][4]
                    newTradePoolContribution = totalTradePoolContribution + projectValueDictionary[key][5]
 
                    #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                    projectedTradePoolContribution = newTradePoolContribution*projectionRatio

                    #The new total PF will have to be recalcd as well:
                    if newCost!=0:
                        newPF = newEarned/newCost
                    else:
                        newPF = 1

                    #Updating our dictionary: 
                    projectValueDictionary[key] = [newCost, newEarned, newOUbudget, newPF, newBasePFdelta, newTradePoolContribution, projectedTradePoolContribution]
                #If not, we will add these values straight to our dictionary:
                else:
                    projectValueDictionary[key] = [totalCost, totalEarned, totalOUbudget, totalPF, totalBasePFdelta, totalTradePoolContribution, projectedTradePoolContribution]


        #===========================================================================
        #If our filter selection is for a CTC period, we are just going to pull the needed values from our database and add them to the list:
        else:
            projectBonusQuery = c.execute("SELECT * FROM Project_Bonus_Summary_Table WHERE ctcPeriod='{}'".format(periodSelection))
            projectBonusValues = c.fetchall()

            #If this foreman is in our list of forement that we want to display then we will perform our calcs:
            for i in range(len(projectBonusValues)):
                #==================================
                #Defining some initial values:
                projectName = projectBonusValues[i][1]
                totalCost = float(projectBonusValues[i][3])
                totalEarned = float(projectBonusValues[i][4])
                totalOUbudget = float(projectBonusValues[i][5])
                totalPF = float(projectBonusValues[i][6])
                totalBasePFdelta = float(projectBonusValues[i][7])
                totalTradePoolContribution = float(projectBonusValues[i][9])

                #==================================
                #Calculating our projected bonus value using our "projectionRatio" variable defined in Section B:
                projectedTradePoolContribution = totalTradePoolContribution*projectionRatio 

                #==================================
                #Defining the key for our dictionary:
                key = (projectName)

                #==================================
                #Updating our dictionary:
                projectValueDictionary[key] = [totalCost, totalEarned, totalOUbudget, totalPF, totalBasePFdelta, totalTradePoolContribution, projectedTradePoolContribution]


        #===========================================================================
        #Defining column header labels for table and adding our values generated above:
        #region
        column_headers = ['Project Name', 'Total Cost', 'Total Earned', '$O/U Budget', 'PF', 'Base PF Delta', 'Trade Pool Contribution', 'Projected Trade Pool']

        data_values = [] #This variable is a nested list that will be entered into our dataframe in the next step

        #projectValueDictionary[key] = [totalCost, totalEarned, totalOUbudget, totalPF, totalBasePFdelta, totalSafetyIncidents, totalTradePoolContribution, projectedTradePoolContribution]
        for key,values in projectValueDictionary.items():
            projectName = key
            totalCost = values[0]
            totalEarned = values[1]
            totalOUbudget = values[2]
            totalPF = values[3]
            basePFdelta = values[4]
            tradePoolContribution = values[5]
            projectedTradePoolContribution = values[6]

            #Updating our data list:
            data_values.append([projectName, totalCost, totalEarned, totalOUbudget, totalPF, basePFdelta, tradePoolContribution, projectedTradePoolContribution])
        
        #endregion


        #===========================================================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        projectTableData = create_dataframe(column_headers, data_values)

        

        #endregion

        #========================================================================================================================================
        #SECTION F-2 | Define functions to apply formatting to table:
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
        #SECTION F-3 | Generate summary table and apply formatting:
        #region CLICK HERE TO EXPAND SECTION


        #===========================================================================
        #Applying dollar formatting to each column: 
        projectTableData['Total Cost'] = projectTableData['Total Cost'].apply(lambda x: f'${x:,.2f}')
        projectTableData['Total Earned'] = projectTableData['Total Earned'].apply(lambda x: f'${x:,.2f}')
        projectTableData['$O/U Budget'] = projectTableData['$O/U Budget'].apply(lambda x: f'${x:,.2f}')
        projectTableData['Base PF Delta'] = projectTableData['Base PF Delta'].apply(lambda x: f'${x:,.2f}')
        projectTableData['Trade Pool Contribution'] = projectTableData['Trade Pool Contribution'].apply(lambda x: f'${x:,.2f}')
        projectTableData['Projected Trade Pool'] = projectTableData['Projected Trade Pool'].apply(lambda x: f'${x:,.2f}')


        #===========================================================================
        #Coloring specified column cells red/green based on being a negative/positive $ value:

        #The "highlight_and_bold_rows" function below is actually not needed for this section, but because i am using the same styling functions from the superintendent table i had to include it
        styled_project_df = projectTableData.style.apply(highlight_and_bold_rows, axis=1)

        #Specifying the columns that we'd like to color the ENTIRE cell of and applying the coloring:
        columns_to_color = ['Trade Pool Contribution', 'Projected Trade Pool'] 
        
        for col in columns_to_color:
            styled_project_df = styled_project_df.applymap(color_negative_red, subset=[col])

        #Specifying the columns that we'd like to color the number of and applying the coloring:
        styled_project_df = styled_project_df.applymap(color_dollar_values, subset=['$O/U Budget', 'Base PF Delta'])

        #===========================================================================
        #Coloring PF column cells red/green based on being a below/above a 1.0 PF:
        styled_project_df = styled_project_df.applymap(highlight_ratio, subset=['PF'])

        #===========================================================================
        #Adding the totals bar at the bottom:
    



        #===========================================================================
        #Displaying our project summary table on the left side of our applicaton page:
        #column_headers = ['Project Name', 'Total Cost', 'Total Earned', '$O/U Budget', 'PF', 'Safety Incidents', 'Base PF Delta', 'Trade Pool Contribution', 'Projected Trade Pool Contribution']
        st.subheader("Project Trade Pool Summary")

        st.dataframe(
            styled_project_df,
            column_config={
                'Project Name': st.column_config.TextColumn('Project Name', help='Name and number of the project'),
                'Total Cost': st.column_config.TextColumn('Total Cost', help='Total cost to date this period'),
                'Total Earned': st.column_config.TextColumn('Total Earned', help='Total budget $ earned to date this period'),
                '$O/U Budget': st.column_config.TextColumn("$O/U Budget", help="Total $ difference between cost and earned this period"),
                'PF': st.column_config.NumberColumn('PF', help='Performance factor is total $ earned divided by total cost this period', format="%.2f"),
                'Base PF Delta': st.column_config.TextColumn('Base PF Delta', help='The total $ O/U budget when the trade base PF is factored in'),
                'Trade Pool Contribution': st.column_config.TextColumn('Trade Pool Contribution', help='8.25% of the Base PF Delta'),
                'Projected Trade Pool': st.column_config.TextColumn('Projected Trade Pool', help='Paperwork Deduction = Total Bonus X (100% - % On Time) X -0.2')
            },
            height=900,
            use_container_width=False,
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
        #SECTION G | Generate cost code summary table and apply formatting:
        #region

        #===========================================================================
        #Example table from streamlit 1/17 interaction!
        st.subheader("Cost Code Bonus Data Breakdown")


        #===========================================================================
        #Querying our "Master_CostCode_Data" database based on the filter period type:
        if "Q" in periodSelection:
            costCodeQuery = c.execute("SELECT * FROM Master_CostCode_Data WHERE bonusPeriod='{}'".format(periodSelection))
            costCodeValues = c.fetchall()
        else:
            costCodeQuery = c.execute("SELECT * FROM Master_CostCode_Data WHERE ctcPeriod='{}'".format(periodSelection))
            costCodeValues = c.fetchall()

        #===========================================================================
        #Updating our "data_values" list using the query values above
        data_values = []

        for i in range(len(costCodeValues)):
            #We don't want to include any "manual adjustment" cost codes in this list becuase they don't impact the overall trade bonus pool
            ccDescription = costCodeValues[i][4]


            #=======================================
            #Defining some initial values:
            trade = costCodeValues[i][12]
            jobName = costCodeValues[i][1]
            ctcPeriod = costCodeValues[i][2]
            costCode = costCodeValues[i][3]
            dollarBudget = float(costCodeValues[i][5])
            unitBudget = float(costCodeValues[i][6])
            uom = costCodeValues[i][7]
            unitsCompleted = round(float(costCodeValues[i][8]),2)
            totalEarned = float(costCodeValues[i][9])
            totalCost = float(costCodeValues[i][10])
            totalOUbudget = float(costCodeValues[i][11])
            trade = costCodeValues[i][12]
            ccType = costCodeValues[i][14]
            ctcTrend = float(costCodeValues[i][15])
            ctcProjection = float(costCodeValues[i][16])
            manualAdjusts = float(costCodeValues[i][17])
            budgetModsTP = float(costCodeValues[i][18])
            ctcNotes = costCodeValues[i][19]
            hjUC = float(costCodeValues[i][20])
            hjCost = float(costCodeValues[i][21])
            hjEarned = float(costCodeValues[i][22])
            hjOUbudget = float(costCodeValues[i][23])
            hjNotes = costCodeValues[i][24]

            #=======================================
            #Calculating our total PF:
            totalPF = costCodeValues[i][12]
            if totalCost!=0:
                totalPF = round(totalEarned/totalCost,2)
            else:
                totalPF = 1
                        
            #If our total is above or below 1,000, then we want to just make it 999 to avoid any crazy big PF values:
            if totalPF>=1000:
                totalPF=999
            if totalPF<=-1000:
                totalPF=-999

            #=======================================
            #Updating our list:

            #We don't want to bog our table down with loads of $0 O/U budget values, so let's filter those out here:
            if round(totalOUbudget)!=0:
                data_values.append([jobName, ctcPeriod, costCode, ccDescription, dollarBudget, unitBudget, uom, unitsCompleted, totalEarned, totalCost, totalOUbudget, totalPF, trade, ccType, ctcTrend, ctcProjection, manualAdjusts, budgetModsTP, ctcNotes, hjUC, hjCost, hjEarned, hjOUbudget, hjNotes])

        #===========================================================================
        #Creating our dataframe:

        #=================================
        #Defining column header labels for table and updating our dataframe with our data calculated above: 
        column_headers = ['Job Name', 'CTC Period', 'Cost Code', 'Cost Code Description', 'Dollar Budget', 'Unit Budget', 'UOM', 'Units Completed', 'Total Earned', 'Total Cost', '$O/U Budget', 'PF', 'Trade', 'CC Type', 
                            'CTC Trend', 'CTC Projection', 'Manual Adjusts', 'Budget Mods TP', 'CTC Notes', 'HJ UC', 'HJ Cost', 'HJ $ Earned', 'HJ $ OU Budget', 'HJ Notes']

        #=================================
        #Creating a pandas dataframe using the "create_dataframe" function defined in Section 1:
        tradeSuperCostCodeData = create_dataframe(column_headers, data_values)

        df = tradeSuperCostCodeData


        #===========================================================================
        # Round specified columns to the second decimal place
        columns_to_dollar_format = ['Dollar Budget', 'Total Earned', 'Total Cost', '$O/U Budget', 'CTC Trend', 'CTC Projection', 'Manual Adjusts', 'Budget Mods TP', 'HJ $ Earned', 'HJ Cost']
        tradeSuperCostCodeData[columns_to_dollar_format] = tradeSuperCostCodeData[columns_to_dollar_format].round(2)

        pfColumns = ["PF"]
        tradeSuperCostCodeData["PF"] = tradeSuperCostCodeData["PF"].round(4)

        #===========================================================================
        # Add a footer row with summed values
        sum_row = {
            "UOM": "TOTALS",
            # 'Units Completed': tradeSuperCostCodeData['Units Completed'].sum(),
            'Total Earned': tradeSuperCostCodeData['Total Earned'].sum(),
            'Total Cost': tradeSuperCostCodeData['Total Cost'].sum(),
            'CTC Trend': tradeSuperCostCodeData['CTC Trend'].sum(),
            'CTC Projection': tradeSuperCostCodeData['CTC Projection'].sum(),
            'Manual Adjusts': tradeSuperCostCodeData['Manual Adjusts'].sum(),
            'Budget Mods TP': tradeSuperCostCodeData['Budget Mods TP'].sum(),
            'HJ Cost': tradeSuperCostCodeData['HJ Cost'].sum(),
            'HJ $ Earned': tradeSuperCostCodeData['HJ $ Earned'].sum(),
            'HJ $ OU Budget': tradeSuperCostCodeData['HJ $ OU Budget'].sum(),




        }
        df_with_footer = pd.concat([tradeSuperCostCodeData, pd.DataFrame([sum_row])], ignore_index=True)

        #===========================================================================
        #Writing JavaScript for conditional formatting that can be applied later in the script: 

        #For formatting cells red/green that are above/below 0: 
        cell_style_jscode = JsCode("""
            function(params) {
                if (params.value < 0) {
                    return {'color': 'red', 'backgroundColor': '#ffe6e6'};
                } else if (params.value > 0) {
                    return {'color': 'green', 'backgroundColor': '#e6ffe6'};
                } else {
                    return null;
                }
            }
            """)

        cell_style_jscodePF = JsCode("""
            function(params) {
                if (params.value < 1) {
                    return {'color': 'red', 'backgroundColor': '#ffe6e6'};
                } else if (params.value >= 1) {
                    return {'color': 'green', 'backgroundColor': '#e6ffe6'};
                } else {
                    return null;
                }
            }
            """)

        #===========================================================================
        # Create AgGrid options
        gb = GridOptionsBuilder.from_dataframe(df_with_footer)

        #===========================================================================
        #Applying formatting to columns:
            
        #=================================
        #Applying the $ formatting AND red/green cell coloring to specified columns:
        for column in ['$O/U Budget', 'CTC Trend', 'CTC Projection', 'HJ $ OU Budget']:
            gb.configure_column(
                column,
                type=["numericColumn"],
                valueFormatter="x.toLocaleString('en-US', {style: 'currency', currency: 'USD', minimumFractionDigits: 2})",
                cellStyle=cell_style_jscode,  # Use JS code for cell styling
            )

        #=================================
        #Applying JUST the dollar formatting:
        for column in ['Dollar Budget', 'Total Earned', 'Total Cost', 'Manual Adjusts', 'Budget Mods TP', 'HJ $ Earned', 'HJ Cost']:
            gb.configure_column(
                column,
                type=["numericColumn"],
                valueFormatter="x.toLocaleString('en-US', {style: 'currency', currency: 'USD', minimumFractionDigits: 2})",
                    
            )

        #=================================
        #Applying the PF column styling:
        for column in pfColumns:
            gb.configure_column(
                column,
                type=["numericColumn"],
                #valueFormatter="x.toLocaleString('en-US', {style: 'currency', currency: 'USD', minimumFractionDigits: 2})",
                cellStyle=cell_style_jscodePF,  # Use JS code for cell styling
            )

        #===========================================================================
        #Configuring table to allow for column filtering:
        gb.configure_default_column(filter=True)  # Enable filtering globally

        #===========================================================================
        # Add footer row
        gb.configure_grid_options(pinnedBottomRowData=[{
            "Job Name": "TOTALS",
            # 'Units Completed': tradeSuperCostCodeData['Units Completed'].sum(),
            'Total Earned': tradeSuperCostCodeData['Total Earned'].sum(),
            'Total Cost': tradeSuperCostCodeData['Total Cost'].sum(),
            '$O/U Budget': tradeSuperCostCodeData['$O/U Budget'].sum(),
            'CTC Trend': tradeSuperCostCodeData['CTC Trend'].sum(),
            'CTC Projection': tradeSuperCostCodeData['CTC Projection'].sum(),
            'Manual Adjusts': tradeSuperCostCodeData['Manual Adjusts'].sum(),
            'Budget Mods TP': tradeSuperCostCodeData['Budget Mods TP'].sum(),
            'HJ Cost': tradeSuperCostCodeData['HJ Cost'].sum(),
            'HJ $ Earned': tradeSuperCostCodeData['HJ $ Earned'].sum(),
            'HJ $ OU Budget': tradeSuperCostCodeData['HJ $ OU Budget'].sum(),
        }])

        #===========================================================================
        #Seeting 
        gb.configure_column("Job Name", pinned="left")
        gb.configure_column("Cost Code", pinned="left")
        gb.configure_column("Cost Code Description", pinned="left")


        #===========================================================================
        # Render the table
        grid_options = gb.build()
        
        AgGrid(
            tradeSuperCostCodeData,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            height=750,
            theme="streamlit",
            # fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,  # Enable unsafe JS code
        )


        #===========================================================================
        #Creating our excel download button!
        excel_file = to_excel(tradeSuperCostCodeData)
        st.download_button(
                label="Download Data to Excel",
                data=excel_file,
                file_name="Cost Code Bonus Data Breakdown ('{}').xlsx".format(periodSelection),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )        


        #endregion


    #endregion


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


