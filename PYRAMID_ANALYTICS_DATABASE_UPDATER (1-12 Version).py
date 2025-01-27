#This data will be used to track employee timecard submission/review consistency
print('STARTING UP PYRAMID BOT: BONUS SUMMARY TABLE UPDATER')
print('<>')
print('<>')
print('<>')
print('<>')
#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#IMPORTING OUR LIBRARIES/MODULES:
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION
import time

#importing openpyxl for excel work:
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import NamedStyle
from openpyxl.styles import Font
from openpyxl.styles import Border, Side
from openpyxl.styles import Alignment

#importing the os module to allow us to work with our operating system in various ways
import os

#Import sqlite3 for all database functionality
import sqlite3

#importing the shutil library which will allow us to move files from one folder to another:
import shutil

#importing the date library for various applications
from datetime import date
import datetime

#Writing code to read the data from the xls file
import smtplib
from email.message import EmailMessage

#Importing the Smartsheet library so that I can interact with it's API:
#SMARTSHEET API TOKEN (Collin's Application) ==> gFRPGyUEO4ykQlJQlmbrBqZiTmhbVCEuw8ol1
import smartsheet
import logging

#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
#DEFINING FUNCTIONS AND DOING MISC SETUP STUFF LIKE CONNECTING TO OUR DATABASE: 
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION

#The function below will be designed to convert any date format into my selected standard format: 2023-01-16
def dateFormatter(date):
    #First, let's strip any trailing zeros/time data from our date value
    if len(date)>10:
        date = date[0:10].strip(' ')

    #Next, let's fix any dates that don't have 2 characters for the month/day values:
    if '/' in date:
        #First let's pull out the day and month values:
        month = date[0:date.index('/')]
        day = date[date.index('/')+1:date.index('/')+3]
        if '/' in month:
            month = date[date.index('/')+1:date.index('/')+2]
        if '/' in day:
            day='0'+day[0]

        year = date[-4:]
        
        #First let's fix the month value: 
        if len(month)==1:
            month='0'+month

        #Next, let's fix the day value:
        if len(day)==1:
            day='0'+day

        #Finally, let's compile each date value into our final format
        date = year+'-'+month+'-'+day

        return date

    if '-' in date:
        #First let's pull out the day and month values:
        month = date[date.index('-')+1:date.index('-')+3]
        if '-' in month:
            month = date[date.index('-')+1:date.index('-')+2]
            
        day = date[date.index('-')+3:date.index('-')+5]
        if '-' in day:
            day = date[date.index('-')+4:date.index('-')+6]

        year = date[0:4]

        #First let's fix the month value: 
        if len(month)==1:
            month='0'+month

        #Next, let's fix the day value:
        if len(day)==1:
            day='0'+day

        #Finally, let's compile each date value into our final format
        date = year+'-'+month+'-'+day

        return date

#The function below will convert any none type value to a zero string:  
def noneValueFixer(value):
    return '0' if value is None else value

def noneStringValueFixer(value):
    return '0' if value is None else value

#Connecting to our database and getting our previous period CC data:
os.chdir('C:\\Users\\colli\\AppData\\Local\\Programs\\Python\\Python310\\My_Python_Scripts\\Main_App_Folder_2025\\streamlit_app')
conn = sqlite3.connect('Pyramid_Analytics_Database.db')
c = conn.cursor()

#Writing a function that will format our code block run time print outs in the console to be easier to read: 
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes} minutes and {seconds:.2f} seconds"

#Starting our time for our full script runtime console printout
fullScritStart_Time = time.time()

#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #0: DEFINING ALL OF OUR CTC PERIOD VALUES')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION
start_time = time.time()


#[SECTION A]============================================================================================================================================
#=======================================================================================================================================================
#Creating a dictionary of all the CTC Period cutoff dates. UPDATE THE FOLLOWING VALUES FOR EAVERY NEW CTC PERIOD ENTRY:
#region

#============================================================================================================================================================
#Defining some CTC period info: 

#=================================================================================================
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


#=================================================================================================
#Creating a dictionary that will return the bonus period of the input CTC period:
ctcBonusPeriodDictionary = {}

for i in range(len(bonusPeriodValues)):
    periodType = bonusPeriodValues[i][2]

    if periodType=='CTC Period':
        periodName = bonusPeriodValues[i][3]
        entryBonusPeriod = bonusPeriodValues[i][6]

        ctcBonusPeriodDictionary[periodName] = entryBonusPeriod



#endregion

#[SECTION B]============================================================================================================================================
#=======================================================================================================================================================
#Creating a function that takes in a date and returns the CTC Period and Bonus Period:
#region

def ctcBonusPeriodFinder(inputDate):
    functionCTCperiod=''
    functionBonusPeriod=''

    for key,values in CTCcutoffDictionary.items():
        ctcPeriod = key
        startDate = values[0]
        endDate = values[1]

        if inputDate>=startDate and inputDate<=endDate:
            functionCTCperiod=ctcPeriod
            functionBonusPeriod = ctcBonusPeriodDictionary[functionCTCperiod]


    return [functionCTCperiod, functionBonusPeriod]




#endregion




#Printing out the code block runtime to the console: 
print('<SUCCESS>')
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CODE BLOCK RUNTIME = {format_time(elapsed_time)}")
#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #1: DEFINING INITIAL VALUES, LIKE BASE PF VALUES, ETC.')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION

#=====================================================================================================================================================================================
#Defining our system base bonus values:

#========================================================================================
#Project base PF: 
projectBasePF = 0.96

#========================================================================================
#Trade superintendent base PF values: 
tradeSuperBasePFdictionary = {}

tradeSuperBasePFdictionary[('Concrete', 'Production')] = [.97, .95]
tradeSuperBasePFdictionary[('Concrete', 'Material')] = [.97, .95]
tradeSuperBasePFdictionary[('Concrete', 'COR')] = [1, 1]
tradeSuperBasePFdictionary[('Concrete', 'Rework')] = [1, 1]

tradeSuperBasePFdictionary[('Earthwork', 'Production')] = [0.97, .95]
tradeSuperBasePFdictionary[('Earthwork', 'Material')] = [1, .95]
tradeSuperBasePFdictionary[('Earthwork', 'COR')] = [1, 1]
tradeSuperBasePFdictionary[('Earthwork', 'Rework')] = [1, 1]

tradeSuperBasePFdictionary[('Utilities', 'Production')] = [1, .95]
tradeSuperBasePFdictionary[('Utilities', 'Material')] = [1, .95]
tradeSuperBasePFdictionary[('Utilities', 'COR')] = [1, 1]
tradeSuperBasePFdictionary[('Utilities', 'Rework')] = [1, 1]

#========================================================================================
#Foreman base PF values: 
foremanBasePFdictionary = {}

foremanBasePFdictionary['Concrete']=[.95, .91]
foremanBasePFdictionary['Earthwork']=[.95, .91]
foremanBasePFdictionary['Utilities']=[.98, .95]

foremanBasePFdictionary['General']=[.95, .91] #For now setting our "General" foreman trade (Joe Hererra) to be the same as earthwork's


#=====================================================================================================================================================================================
#Peformance bonus earn rate for each position:
projectTradePoolEarnRate = .0825
tradeSuperPerformanceBonusEarnRate = .04
foremanPerformanceBonusEarnRate = .1

#=====================================================================================================================================================================================
#Bonus Pool share rates by position:
tradeSuperBonusPoolPercent = .29
foremanBonusPoolPercent = .71

#=====================================================================================================================================================================================
#Bonus period dictionary by ctc period: 
bonusPeriodDictionary = {}

query = c.execute("SELECT * FROM Master_CostCode_Data")
values = c.fetchall()

for i in range(len(values)):
    ctcPeriod = values[i][2]
    bonusPeriod = values[i][25]

    bonusPeriodDictionary[ctcPeriod]=bonusPeriod


#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #2: UPDATING OUR "Master_Paperwork_Data" DATABASE TABLE')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION

#=====================================================================================================================================================================================
#Connecting to our database and getting our previous period CC data:
os.chdir('C:\\Users\\colli\\AppData\\Local\\Programs\\Python\\Python310\\My_Python_Scripts\\Flask\\Pyramid_Performance')
conn = sqlite3.connect('pyramid.db')
c = conn.cursor()


#=====================================================================================================================================================================================
#Creating a list of all paperwork information:
#region
paperworkInfoList = []


#=================================================================================================================
#Equipment inspection calcs:
Query = c.execute("SELECT * FROM equipment_inspection_tracking")
EIvalues = c.fetchall()

for i in range(len(EIvalues)):
    employeeName = EIvalues[i][4]
    paperworkType = 'Equipment Inspection'
    pwDate = EIvalues[i][2]
    onTimeCheck = EIvalues[i][3]
    pwNotes = 'Equipment Number: '+EIvalues[i][1]

    paperworkInfoList.append([employeeName, paperworkType, pwDate, onTimeCheck, pwNotes])

#=================================================================================================================
#Safety meeting calcs:
Query = c.execute("SELECT * FROM safety_meeting_tracking")
SMvalues = c.fetchall()

for i in range(len(SMvalues)):
    employeeName = SMvalues[i][2]
    paperworkType = 'JHA/Safety Meeting'
    pwDate = SMvalues[i][3]

    #Converting the on time check to "YES/NO" value:
    onTimeCheck = SMvalues[i][6]
    if onTimeCheck=="Not Submitted":
        onTimeCheck='NO'
    if onTimeCheck=="Submitted":
        onTimeCheck='YES'

    pwNotes = ''

    paperworkInfoList.append([employeeName, paperworkType, pwDate, onTimeCheck, pwNotes])

#=================================================================================================================
#Timecard calcs:
Query = c.execute("SELECT * FROM timecard_log")
TCvalues = c.fetchall()
for i in range(len(TCvalues)):
    employeeName = TCvalues[i][3]
    paperworkType = 'Timecard'
    pwDate = TCvalues[i][4]

    #Converting the on time check to "YES/NO" value:
    onTimeCheck = TCvalues[i][20]
    if onTimeCheck=="LATE":
        onTimeCheck='NO'


    pwNotes = ''

    paperworkInfoList.append([employeeName, paperworkType, pwDate, onTimeCheck, pwNotes])

#endregion

#=====================================================================================================================================================================================
#Apply CTC/Bonus periods to each entry using the CTC period dates defined in section #0 and updating a list that will be used to update our database:
#region

paperworkDatabaseList = []

for i in range(len(paperworkInfoList)):
    #=======================================================
    #Defining some initial values: 
    employeeName = paperworkInfoList[i][0]
    paperworkType = paperworkInfoList[i][1]
    pwDate = paperworkInfoList[i][2]
    onTimeCheck = paperworkInfoList[i][3]
    pwNotes = paperworkInfoList[i][4]

    dateDT = datetime.datetime(int(pwDate[0:4]),int(pwDate[5:7]),int(pwDate[8:10]))

    #=======================================================
    #Using our "ctcBonusPeriodFinder" from step #0 to return the CTC and Bonus Periods based on the paperwork date:
    periodInfo = ctcBonusPeriodFinder(dateDT)

    ctcPeriod = periodInfo[0]
    bonusPeriod = periodInfo[1]

    #=======================================================
    #Figuring out the employee trade using our "Users" database:
    Query = c.execute("SELECT * FROM users WHERE name='{}'".format(employeeName))
    userValues = c.fetchall()

    if userValues!=[]:
        position = userValues[0][9]
        trade=userValues[0][8]

        #If the employee is Jesus Mosqueda, then we want to modify his trade value to distinguish it from Angel's utilities:
        if employeeName=='Jesus Mosqueda':
            trade='Utilities - Adrian Mosqueda'
        
    else:
        position=''
        trade=''

    #=======================================================
    #Finally, updating our list of values for our database:
    #We only want to track paperwork for foremen: 
    if position=='Foreman':
        paperworkDatabaseList.append([employeeName, paperworkType, pwDate, onTimeCheck, pwNotes, ctcPeriod, bonusPeriod, trade])



#endregion

#=====================================================================================================================================================================================
#Updating our database

#=======================================================
#First let's delete all previous entries in the database as they will be rewritten by this script:
#=====================================================================================================================================================================================
#Connecting to our database and getting our previous period CC data:
os.chdir('C:\\Users\\colli\\AppData\\Local\\Programs\\Python\\Python310\\My_Python_Scripts\\Main_App_Folder_2025\\streamlit_app')
conn = sqlite3.connect('Pyramid_Analytics_Database.db')
c = conn.cursor()


def deleteMultipleRecords():
    c.execute("DELETE from Master_Paperwork_Data")
    conn.commit()

deleteMultipleRecords()

#=======================================================
#Updating our database:

rowcount=1

for i in range(len(paperworkDatabaseList)):
    c.execute("INSERT INTO Master_Paperwork_Data VALUES(:id, :employeeName, :paperworkType, :date, :submittedOnTime, :paperworkNotes, :ctcPeriod, :bonusPeriod, :trade)",
                {
                'id':rowcount,
                'employeeName':paperworkDatabaseList[i][0],
                'paperworkType':paperworkDatabaseList[i][1],
                'date':paperworkDatabaseList[i][2],
                'submittedOnTime':paperworkDatabaseList[i][3],
                'paperworkNotes':paperworkDatabaseList[i][4],
                'ctcPeriod':paperworkDatabaseList[i][5],
                'bonusPeriod':paperworkDatabaseList[i][6],
                'trade':paperworkDatabaseList[i][7]
                })

    rowcount=rowcount+1
    conn.commit()


#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #3: CALCULATING OUR TRADE BONUS POOL SUMMARY VALUES')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION


#=====================================================================================================================================================================================
#Creating a dictionary of all cost related values for each cost code/ctc period:
#region


#=====================================================================================================
#Querying our "Master_CostCode_Data" database for the values to be used in calculating our project trade pool values:
costCodeBonusQuery = c.execute("SELECT * FROM Master_CostCode_Data")
costCodeBonusValues = c.fetchall()

#=====================================================================================================
#Iterating through the values, performing our calculations, and updating our dictionary: 
tradePoolBonusValueDict = {}


for i in range(len(costCodeBonusValues)):
    #FIRST! The "Master_CostCode_Data" database table includes all of the manual adjustments made to our trade super values. We DO NOT want to add these in! So let's check before running this code block: 
    ccDescription = costCodeBonusValues[i][4]

    if "MANUAL ADJUST" not in ccDescription:
        #===============================================================
        #Defining some initial variable values: 
        ctcPeriod = costCodeBonusValues[i][2]
        projectName = costCodeBonusValues[i][1]
        projectNum = projectName[0:5]
        totalCost = float(costCodeBonusValues[i][10])
        totalEarned = float(costCodeBonusValues[i][9])
        totalOUbudget = float(costCodeBonusValues[i][11])
        bonusPeriod = costCodeBonusValues[i][25]

        #===============================================================
        #Calculating our total PF value for this cost code: 
        if totalCost!=0:
            totalPF = round(totalEarned/totalCost,2)
        else:
            totalPF = 1

        #===============================================================
        #Calculating our base PF values and our total trade pool contribution: 

        #Pulling our "projectBasePF" and "projectTradePoolEarnRate" variables from step #1 to get our base PF value: 
        basePFcost = float(totalCost)*projectBasePF
        basePFdelta = float(totalEarned)-basePFcost
        
        tradePoolContribution = projectTradePoolEarnRate*basePFdelta

        #===============================================================
        #Finally, updating our dictionary:
        key = (projectNum, ctcPeriod)

        #If this key is already in our dictionary, adding to existing values: 
        if key in tradePoolBonusValueDict:
            newCost = tradePoolBonusValueDict[key][1] + totalCost
            newEarned = tradePoolBonusValueDict[key][2] + totalEarned
            newOUbudget = newEarned-newCost

            if newCost!=0:
                newTotalPF = round(newEarned/newCost,2)
            else:
                newTotalPF = 1

            newBasePFcost = newCost*projectBasePF
            newBasePFdelta = newEarned-newBasePFcost
            newTradePoolContribution = projectTradePoolEarnRate*newBasePFdelta

            tradePoolBonusValueDict[(projectNum, ctcPeriod)] = [projectName, newCost, newEarned, newOUbudget, newTotalPF, round(newBasePFdelta,2), round(newBasePFcost,2), round(newTradePoolContribution,2), bonusPeriod]
        #If not, adding values to dictionary
        else:
            tradePoolBonusValueDict[(projectNum, ctcPeriod)] = [projectName, totalCost, totalEarned, totalOUbudget, totalPF, round(basePFdelta,2), round(basePFcost,2), round(tradePoolContribution,2), bonusPeriod]

#endregion



#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #4: UPDATING OUR "Project_Bonus_Summary_Table" DATABASE TABLE WITH THE VALUES FROM STEP #3')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION


#=============================================================================================================
#First let's delete all previous entries in the database as they will be rewritten by this script:
def deleteMultipleRecords():
    c.execute("DELETE from Project_Bonus_Summary_Table")
    conn.commit()

deleteMultipleRecords()

#=====================================================================================================================================================================================
#Itterating through our dictionary created in step #3 and updating our database:
#region

#tradePoolBonusValueDict[(projectNum, ctcPeriod)] = [projectName, totalCost, totalEarned, totalOUbudget, totalPF, round(basePFdelta,2), round(basePFcost,2), round(tradePoolContribution,2), bonusPeriod]
rowcount=1

for key,values in tradePoolBonusValueDict.items():
    #=============================================================================================================
    #Including any "Add Ons" to the project bonuses for this period: 
    projectName = values[0]
    ctcPeriod = key[1]

    bonusAddOn = 0
    costAddOn = 0
    earnedAddOn = 0
    totalOUAddOn = 0
    basePFDeltaAddOn = 0

    addOnQuery = c.execute("SELECT * FROM Master_Bonus_Add_On_Summary WHERE employeeName='{}' and ctcPeriod='{}'".format(projectName, ctcPeriod))
    addOnValues = c.fetchall()

    for j in range(len(addOnValues)):
        bonusAddOn = bonusAddOn + float(addOnValues[j][4])
        costAddOn = costAddOn + float(addOnValues[j][7])
        earnedAddOn = earnedAddOn + float(addOnValues[j][8])
        totalOUAddOn = totalOUAddOn + float(addOnValues[j][9])
        basePFDeltaAddOn = basePFDeltaAddOn + float(addOnValues[j][10])

    #=============================================================================================================
    #Incorporating "Add On" values calculated above into our values to be included in the bonus summary table:
    totalBonus = float(values[7])+bonusAddOn
    totalCost = float(values[1])+costAddOn
    totalEarned = float(values[2])+earnedAddOn
    totalOU = float(values[3])+totalOUAddOn
    totalBasePFDelta = float(values[5])+basePFDeltaAddOn

    #Recalculating our total PF to accommodate add ons:
    if totalCost!=0:
        totalPF = round(totalEarned/totalCost,2)
    else:
        totalPF = 1

    #=============================================================================================================
    #Updating our database
    c.execute("INSERT INTO Project_Bonus_Summary_Table VALUES(:id, :projectName, :projectNumber, :totalCost, :totalEarned, :totalOUbudget, :totalPF, :basePFdelta, :baseCost, :tradePoolContribution, :ctcPeriod, :bonusPeriod, :costAddOns, :earnedAddOns, :totalOUbudgetAddOns, :tradePoolAddOns, :basePFDeltaAddOns)",
            {
            'id':rowcount,
            'projectName':values[0],
            'projectNumber':key[0],
            'totalCost':totalCost,
            'totalEarned':totalEarned,
            'totalOUbudget':totalOU,
            'totalPF':totalPF,
            'basePFdelta':totalBasePFDelta,
            'baseCost':values[6],
            'tradePoolContribution':totalBonus,
            'ctcPeriod':key[1],
            'bonusPeriod':values[8],
            'costAddOns':costAddOn,
            'earnedAddOns':earnedAddOn,
            'totalOUbudgetAddOns':totalOUAddOn,
            'tradePoolAddOns':bonusAddOn, 
            'basePFDeltaAddOns':basePFDeltaAddOn
            })

    rowcount=rowcount+1
    conn.commit()



#endregion


#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #5: CALCULATING OUR TRADE SUPERINTENDENT BONUS SUMMARY VALUES')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION


#=====================================================================================================================================================================================
#Creating a dictionary of all cost related values for each trade super/CC type/CTC period:
#region

#tradeSuperBonusValueDict[(tradeSuperName, ccType, ctcPeriod)] = [trade, totalCost, totalEarned, manualAdjustCost, manualAdjustEarned]
tradeSuperCostValueDict = {}

#Querying our "Master_CostCode_Data" database for the values to be used in calculating our superintendent bonus values:
costCodeBonusQuery = c.execute("SELECT * FROM Master_CostCode_Data")
costCodeBonusValues = c.fetchall()

#Iterating through the values and performing our calculations: 
for i in range(len(costCodeBonusValues)):
    trade = costCodeBonusValues[i][12]
    
    #Our "Master_CostCode_Data" contains non-trade cost codes, so let's filter those here!
    if trade in ['Concrete', 'Earthwork', 'Utilities']:
        #==============================================================================================
        #Defining our initial variable values: 
        ccType = costCodeBonusValues[i][14]
        ctcPeriod = costCodeBonusValues[i][2]
        
        totalCost = float(costCodeBonusValues[i][10])
        totalEarned = float(costCodeBonusValues[i][9])

        manualAdjustCost = float(costCodeBonusValues[i][26])
        manualAdjustEarned = float(costCodeBonusValues[i][27])

        #==============================================================================================
        #Pulling our trade super name from our "Users" database: 
        userQuery = c.execute("SELECT * FROM Users WHERE position='{}' and craft='{}'".format('Craft Superintendent', trade))
        userValues = c.fetchall()

        tradeSuperName = userValues[0][2]

        #==============================================================================================
        #Lastly, updating our dictionary: 
        key = (tradeSuperName, ccType, ctcPeriod)

        #If this key is already in our dictionary, then we will add to the existing cost values: 
        if key in tradeSuperCostValueDict:
            updatedTotalCost = tradeSuperCostValueDict[key][1] + totalCost
            updatedTotalEarned = tradeSuperCostValueDict[key][2] + totalEarned
            updatedManualAdjustCost = tradeSuperCostValueDict[key][3] + manualAdjustCost
            updatedManualAdjustEarned = tradeSuperCostValueDict[key][4] + manualAdjustEarned

            tradeSuperCostValueDict[key]=[trade, updatedTotalCost, updatedTotalEarned, updatedManualAdjustCost, updatedManualAdjustEarned]
        #If not, then we will set the cost values for this key
        else:
            tradeSuperCostValueDict[key]=[trade, totalCost, totalEarned, manualAdjustCost, manualAdjustEarned]


#endregion


#=====================================================================================================================================================================================
#Creating a dictionary of values to update our bonus summary table with by iterating through our dictionary created above and adding in the base PF values, performance bonus, paperwork, safety, bonus pool, and total bonus values:
#region

#tradeSuperBonusValueDict[(tradeSuperName, ccType, ctcPeriod)] = [trade, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, basePF, baeCost, performanceBonus, paperworkDeduct, safetyDeduct, poolShare, totalBonus, ctcPeriod, bonusPeriod, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget]
tradeSuperBonusValueDict = {}

for key,values in tradeSuperCostValueDict.items():
    #=============================================================================================================
    #Defining our initial variable values: 
    #region

    tradeSuperName=key[0]
    ccType=key[1]
    ctcPeriod=key[2]

    trade = values[0]


    #Cost values
    totalCost = values[1]
    totalEarned = values[2]
    totalOUbudget = totalEarned-totalCost

    if totalCost>0:
        totalPF = totalEarned/totalCost
    else:
        totalPF = 1

    #Manual Adjust Values
    manualAdjustCost = values[3]
    manualAdjustEarned = values[4]
    manualAdjustOUbudget = manualAdjustEarned-manualAdjustCost

    #endregion

    #=============================================================================================================
    #Using our "bonusPeriodDictionary" defined in step #1 to pull the bonus period using the ctc period: 
    bonusPeriod=bonusPeriodDictionary[ctcPeriod]

    #=============================================================================================================
    #Calculating our base PF values, and performance bonus: 
    #region


    #===========================================
    #Using our "tradeSuperBasePFdictionary" from step #1 to pull our base PF value based on trade/PF:
    
    #tradeSuperBasePFdictionary[('Concrete', 'Production')] = [.97, .95]
    basePFkey = (trade, ccType)
    basePFvalues = tradeSuperBasePFdictionary[basePFkey]


    #===========================================
    #When determining our base PF, we want to use the total PF FOR THE ENTIRE BONUS PERIOD to calculate the PF value that will be used to determine if we are going to use the ceiling/floor PF.
    #If you just evaluate each individual month, you can get differing values for the base PF month-month
    totalBPcost = 0
    totalBPearned = 0

    for key2,values2 in tradeSuperCostValueDict.items():
        entryTradeSuperName = key2[0]
        entryCCtype = key2[1]
        entryCTCperiod = key2[2]
        
        entryTrade = values2[0]
        entryCost = values2[1]
        entryEarned = values2[2]

        entryBonusPeriod = bonusPeriodDictionary[entryCTCperiod]

        #If this iterration's entry bonus period is equal to the bonus period for this overall dictionary update:
        if entryBonusPeriod==bonusPeriod:
            #AND this is for the same trade super/cc type:
            if (entryTradeSuperName, entryCCtype)==(tradeSuperName, ccType):
                totalBPcost = totalBPcost+entryCost
                totalBPearned = totalBPearned+entryEarned

    #Finally, calculating what the overall PF is of this trade super/cost code type this period:
    if totalBPcost!=0:
        totalBPPF = totalBPearned/totalBPcost
    else:
        totalBPPF = 1


    #===========================================
    #Determining our base PF/ base cost: 
    #If our PF is greater than the ceiling base PF value, then we will use the ceiling base PF value: 
    if totalBPPF>basePFvalues[0]:
        basePF = basePFvalues[0]
        basePFcost = totalCost*basePF
    #If our PF is less than the ceiling base PF value, then we will use the ceiling base PF value: 
    elif totalBPPF<basePFvalues[1]:
        basePF = basePFvalues[1]
        basePFcost = totalCost*basePF
    #If our PF is between the ceiling/floor values, then we will set our basePFcost=totalEarned so that the basePFdelta=0: 
    else:
        basePF = 0
        basePFcost = totalEarned

    #===========================================
    basePFdelta = totalEarned-basePFcost

    #===========================================
    #Calculating our performance bonus value using our base PF calculated above and our "tradeSuperPerformanceBonusEarnRate" variable defined in step #1:
    performanceBonus = tradeSuperPerformanceBonusEarnRate*basePFdelta

    #endregion

    #=============================================================================================================
    #Calculating our total bonus pool amount: 
    #region

    #===========================================
    #Adding up the total bonus pool value for this period: 
    projectBonusQuery = c.execute("SELECT * FROM Project_Bonus_Summary_Table WHERE ctcPeriod='{}'".format(ctcPeriod))
    projectBonusValues = c.fetchall()

    totalTradePool = 0

    for i in range(len(projectBonusValues)):
        totalTradePool = totalTradePool+float(projectBonusValues[i][9])

    #===========================================
    #Counting the number of trade supers employed this period: 
    tradeSuperCount=3

    #===========================================
    #Calculating our total trade pool share using our "tradeSuperBonusPoolPercent" defined in section #1: 
    tradePoolShare = totalTradePool*tradeSuperBonusPoolPercent/tradeSuperCount

    #Dividing our trade pool share amount by 4, because we are updating the bonus period for each CC type: 
    tradePoolShare = tradePoolShare/4

    #endregion

    #=============================================================================================================
    #Calculating our paperwork values:
    #region

    #===========================================
    #Adding up our paperwork totals:
    paperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE trade='{}' and ctcPeriod='{}'".format(trade, ctcPeriod))
    paperworkValues = c.fetchall()

    totalPaperwork = 0
    totalOnTime = 0
    totalLate = 0

    for i in range(len(paperworkValues)):
        check = paperworkValues[i][4]
        totalPaperwork = totalPaperwork+1

        if check=='YES':
            totalOnTime = totalOnTime+1
        else:
            totalLate = totalLate+1

    #===========================================
    #Using our totals above to calculate the paperwork % and deduction amount
    if totalPaperwork!=0:
        paperworkPercent = totalOnTime/totalPaperwork
    else:
        paperworkPercent = 0

    paperwork = str(totalOnTime)+'/'+str(totalPaperwork)+str(" (")+str(round(paperworkPercent*100,2))+'%)'

    #Calculating a base bonus total to use in calculating our paperwork deduction amount
    baseTotalBonus = tradePoolShare+performanceBonus

    #Calculating the paperwork deduction amount: 
    paperworkDeduct=-.2*baseTotalBonus*(1-paperworkPercent)

    #endregion

    #=============================================================================================================
    #Calculating our safety values
    #region

    safetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE trade='{}' and ctcPeriod='{}'".format(trade, ctcPeriod))
    safetyValues = c.fetchall()

    safetyIncidents=len(safetyValues)

    safetyDeduct=-.3*tradePoolShare*safetyIncidents

    #endregion

    #=============================================================================================================
    #Calculating our total bonus value: 
    totalBonus=performanceBonus+tradePoolShare+paperworkDeduct+safetyDeduct

    #=============================================================================================================
    #Finally, updating our "tradeSuperBonusValueDict" dictionary:
    key = (tradeSuperName, ccType, ctcPeriod)

    tradeSuperBonusValueDict[key] = [trade, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, basePF, basePFcost, performanceBonus, paperworkDeduct, safetyDeduct, tradePoolShare, totalBonus, ctcPeriod, bonusPeriod, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget]

#=============================================================================================================
#MANUALLY ADDING ADRIAN MOSQUEDA TO THIS LIST 

tradeSuperBonusValueDict[('Jesus Mosqueda', 'Production', 'November-2024')] = ['Utilities', 231283.77, 236634.00, 5350.23, 1.023, '195/412 (47.33%)', 0, 8350.90, 0.98, 229108.10, 9555.41, -1269.96, 0, 2500.41, 10785.86, 'November-2024', 'Q3&4: 2024', 0, 0, 0]
tradeSuperBonusValueDict[('Jesus Mosqueda', 'Material', 'November-2024')] = ['Utilities', 0, 0, 0, 1, '195/412 (47.33%)', 0, 0, 0, 0, 0, 0, 0, 0, 0, 'November-2024', 'Q3&4: 2024', 0, 0, 0]
tradeSuperBonusValueDict[('Jesus Mosqueda', 'COR', 'November-2024')] = ['Utilities', 0, 0, 0, 1, '195/412 (47.33%)', 0, 0, 0, 0, 0, 0, 0, 0, 0, 'November-2024', 'Q3&4: 2024', 0, 0, 0]
tradeSuperBonusValueDict[('Jesus Mosqueda', 'Rework', 'November-2024')] = ['Utilities', 0, 0, 0, 1, '195/412 (47.33%)', 0, 0, 0, 0, 0, 0, 0, 0, 0, 'November-2024', 'Q3&4: 2024', 0, 0, 0]

#endregion





#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #6: UPDATING OUR "Trade_Superintendent_Bonus_Summary" DATABASE TABLE WITH THE VALUES FROM STEP #5')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION

#=============================================================================================================
#First let's delete all previous entries in the database as they will be rewritten by this script:
def deleteMultipleRecords():
    c.execute("DELETE from Trade_Superintendent_Bonus_Summary")
    conn.commit()

deleteMultipleRecords()

#=============================================================================================================
#Updating our database table: 
#tradeSuperBonusValueDict[(tradeSuperName, ccType, ctcPeriod)] = [trade, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, basePF, basePFcost, performanceBonus, paperworkDeduct, safetyDeduct, tradePoolShare, totalBonus, ctcPeriod, bonusPeriod, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget]

rowcount=1

for key,values in tradeSuperBonusValueDict.items():
    #=============================================================================================================
    #Including any "Add Ons" to the trade super bonuses for this period: 
    tradeSuper = key[0]
    ctcPeriod = key[2]

    bonusAddOn = 0

    addOnQuery = c.execute("SELECT * FROM Master_Bonus_Add_On_Summary WHERE employeeName='{}' and ctcPeriod='{}'".format(tradeSuper, ctcPeriod))
    addOnValues = c.fetchall()

    for j in range(len(addOnValues)):
        addOnAmt = float(addOnValues[j][4])
        bonusAddOn = bonusAddOn + addOnAmt

    #Dividing our bonus add on amount by 4 to accommodate the fact that the superintendent will have 4 entries, one for each CC type:
    bonusAddOn = round(bonusAddOn/4,2)

    #=============================================================================================================
    #Adding the "Add Ons" to our total bonus amount:
    totalBonus = float(values[14])+bonusAddOn

    #=============================================================================================================
    #Defining our initial variable values: 
    tradeSuperName=key[0]
    ccType=key[1]
    ctcPeriod=key[2]

    trade = values[0]

    #=============================================================================================================
    #Updating our database:
    c.execute("INSERT INTO Trade_Superintendent_Bonus_Summary VALUES(:id, :trade, :superintendentName, :ccType, :totalCost, :totalEarned, :totalOUbudget, :tradePF, :paperwork, :safetyIncidents, :basePFdelta, :basePF, :baseCost, :performanceBonus, :paperworkDeduct, :safetyDeduct, :poolShare, :totalBonus, :ctcPeriod, :bonusPeriod, :manualAdjustCost, :manualAdjustEarned, :manualAdjustOUbudget, :bonusAddOns)",
            {
            'id':rowcount,
            'trade':values[0],
            'superintendentName':key[0],
            'ccType':key[1],
            'totalCost':values[1],
            'totalEarned':values[2],
            'totalOUbudget':values[3],
            'tradePF':values[4],
            'paperwork':values[5],
            'safetyIncidents':values[6],
            'basePFdelta':values[7],
            'basePF':values[8],
            'baseCost':values[9],
            'performanceBonus':values[10],
            'paperworkDeduct':values[11],
            'safetyDeduct':values[12],
            'poolShare':values[13], 
            'totalBonus':totalBonus, 
            'ctcPeriod':key[2], 
            'bonusPeriod':values[16], 
            'manualAdjustCost':values[17], 
            'manualAdjustEarned':values[18], 
            'manualAdjustOUbudget':values[19],
            'bonusAddOns':bonusAddOn
            })

    rowcount=rowcount+1
    conn.commit()

#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #7: CALCULATING OUR FOREMAN BONUS SUMMARY VALUES')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION


#=====================================================================================================================================================================================
#Creating a dictionary of all cost related values for each foreman/ctc period:
#region


#=====================================================================================================
#Querying our "Master_Foreman_Data" database for the values to be used in calculating our foreman values:
foremanBonusQuery = c.execute("SELECT * FROM Master_Foreman_Data")
foremanBonusValues = c.fetchall()

#=====================================================================================================
#Iterating through the values, performing our calculations, and updating our dictionary: 
foremanBonusValueDict = {}


for i in range(len(foremanBonusValues)):

    #IMPORTANTE!!! WE DON'T WANT TO INCLUDE ANY "OMITTED" COST CODE VALUES IN OUR FOREMAN BONUS TOTALS:
    ccStatus = foremanBonusValues[i][12]

    if ccStatus=='Included':
        #===============================================================
        #Defining some initial variable values: 
        foreman = foremanBonusValues[i][13]
        ctcPeriod = foremanBonusValues[i][2]
        totalCost = float(foremanBonusValues[i][16])
        totalEarned = float(foremanBonusValues[i][17])
        totalOUbudget = totalEarned-totalCost
        bonusPeriod = foremanBonusValues[i][31]

        #====================
        #Converting any "None" type values to be 0:
        def zeroFixer(input):
            if input==None:
                return 0
            else:
                return float(input)

        trueUpCost = zeroFixer(foremanBonusValues[i][32])
        trueUpEarned = zeroFixer(foremanBonusValues[i][33])
        trueUpOUbudget = zeroFixer(foremanBonusValues[i][34])
        omittedCost = zeroFixer(foremanBonusValues[i][35])
        omittedEarned = zeroFixer(foremanBonusValues[i][36])
        omittedOUbudget = zeroFixer(foremanBonusValues[i][37])
        manualAdjustCost = zeroFixer(foremanBonusValues[i][38])
        manualAdjustEarned = zeroFixer(foremanBonusValues[i][39])
        manualAdjustOUbudget = zeroFixer(foremanBonusValues[i][40])
        retainageWithheld = zeroFixer(foremanBonusValues[i][41])
        
        #====================
        #Calcualting our total PF
        if totalCost!=0:
            totalPF=totalEarned/totalCost
        else:
            totalPF=1

        #===============================================================
        #Querying our "Users" database to get our trade value:
        userQuery = c.execute("SELECT * FROM Users WHERE employeeName='{}'".format(foreman))
        userValues = c.fetchall()

        if userValues!=[]:
            trade = userValues[0][5]
        else:
            trade = 'None'


        #===============================================================
        #Updating our dictionary: 
        key = (foreman, ctcPeriod)

        #If this key is already in our dictionary, we will add this entry's values to the existing values and update our dictionary: 
        if key in foremanBonusValueDict:
            newCost = totalCost + foremanBonusValueDict[key][1]
            newEarned = totalEarned + foremanBonusValueDict[key][2]
            newOUbudget = newEarned-newCost
            if newCost!=0:
                newTotalPF=newEarned/newCost
            else:
                newTotalPF=1

            newTrueUpCost = trueUpCost + foremanBonusValueDict[key][6]
            newTrueUpEarned = trueUpEarned + foremanBonusValueDict[key][7]
            newTrueUpOUbudget = trueUpOUbudget + foremanBonusValueDict[key][8]
            newOmittedCost = omittedCost + foremanBonusValueDict[key][9]
            newOmittedEarned = omittedEarned + foremanBonusValueDict[key][10]
            newOmittedOUbudget = omittedOUbudget + foremanBonusValueDict[key][11]
            newManualAdjustCost = manualAdjustCost + foremanBonusValueDict[key][12]
            newManualAdjustEarned = manualAdjustEarned + foremanBonusValueDict[key][13]
            newManualAdjustOUbudget = manualAdjustOUbudget  + foremanBonusValueDict[key][14]
            newRetainageWithheld = retainageWithheld  + foremanBonusValueDict[key][15]

            foremanBonusValueDict[(foreman, ctcPeriod)] = [trade, newCost, newEarned, newOUbudget, newTotalPF, bonusPeriod, newTrueUpCost, newTrueUpEarned, newTrueUpOUbudget, newOmittedCost, newOmittedEarned, newOmittedOUbudget, newManualAdjustCost, newManualAdjustEarned, newManualAdjustOUbudget, newRetainageWithheld]
        #If not, then we will add these values to our dictionary: 
        else:
            foremanBonusValueDict[(foreman, ctcPeriod)] = [trade, totalCost, totalEarned, totalOUbudget, totalPF, bonusPeriod, trueUpCost, trueUpEarned, trueUpOUbudget, omittedCost, omittedEarned, omittedOUbudget, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget, retainageWithheld]


#endregion


#=====================================================================================================================================================================================
#Creating a list of values to update our foreman bonus summary table with by iterating through our dictionary created above and adding in the base PF values, performance bonus, paperwork, safety, bonus pool, and total bonus values:
#region


foremanBonusDatabaseValueList = []

#foremanBonusValueDict[(foreman, ctcPeriod)] = [trade, totalCost, totalEarned, totalOUbudget, totalPF, bonusPeriod, trueUpCost, trueUpEarned, trueUpOUbudget, omittedCost, omittedEarned, omittedOUbudget, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget, retainageWithheld]
for key,values in foremanBonusValueDict.items():
    #=============================================================================================================
    #Defining our initial variable values: 
    foreman=key[0]
    ctcPeriod=key[1]

    trade = values[0]
    totalCost = values[1]
    totalEarned = values[2]
    totalOUbudget = values[3]
    totalPF = values[4]
    bonusPeriod = values[5]
    trueUpCost = values[6]
    trueUpEarned = values[7]
    trueUpOUbudget = values[8]
    omittedCost = values[9]
    omittedEarned = values[10]
    omittedOUbudget = values[11]
    manualAdjustCost = values[12]
    manualAdjustEarned = values[13]
    manualAdjustOUbudget = values[14]
    retainageWithheld = values[15]


    #=============================================================================================================
    #Calculating our base PF values, and performance bonus: 
    #region

    #===========================================
    #When determining our base PF, we want to use the total PF FOR THE ENTIRE BONUS PERIOD to calculate the PF value that will be used to determine if we are going to use the ceiling/floor PF.
    #If you just evaluate each individual month, you can get differing values for the base PF month-month
    totalBPcost = 0
    totalBPearned = 0

    for key2,values2 in foremanBonusValueDict.items():
        entryForeman = key2[0]
        entryCTCperiod = key2[1]
        
        entryCost = values2[1]
        entryEarned = values2[2]

        entryBonusPeriod = bonusPeriodDictionary[entryCTCperiod]

        #If this iterration's entry bonus period is equal to the bonus period for this overall dictionary update:
        if entryBonusPeriod==bonusPeriod:
            #AND this is for the same foreman:
            if entryForeman==foreman:
                totalBPcost = totalBPcost+entryCost
                totalBPearned = totalBPearned+entryEarned

    #Finally, calculating what the overall PF is of this foreman this period:
    if totalBPcost!=0:
        totalBPPF = totalBPearned/totalBPcost
    else:
        totalBPPF = 1


    #===========================================
    #Using our "foremanBasePFdictionary" from step #1 to pull our base PF value based on trade/PF:
    
    #foremanBasePFdictionary['Concrete'] = [.97, .95]
    basePFvalues = foremanBasePFdictionary[trade]

    #If our PF is greater than the ceiling base PF value, then we will use the ceiling base PF value: 
    if totalBPPF>basePFvalues[0]:
        basePF = basePFvalues[0]
        basePFcost = totalCost*basePF
    #If our PF is less than the ceiling base PF value, then we will use the ceiling base PF value: 
    elif totalBPPF<basePFvalues[1]:
        basePF = basePFvalues[1]
        basePFcost = totalCost*basePF
    #If our PF is between the ceiling/floor values, then we will set our basePFcost=totalEarned so that the basePFdelta=0: 
    else:
        basePF = 0
        basePFcost = totalEarned

    #===========================================
    basePFdelta = totalEarned-basePFcost

    #===========================================
    #Calculating our performance bonus value using our base PF calculated above and our "foremanPerformanceBonusEarnRate" variable defined in step #1:
    performanceBonus = foremanPerformanceBonusEarnRate*basePFdelta

    #endregion


    #=============================================================================================================
    #Calculating our total trade pool amount: 
    #region 


    #===========================================
    #Adding up the total bonus pool value for this period: 
    projectBonusQuery = c.execute("SELECT * FROM Project_Bonus_Summary_Table WHERE bonusPeriod='{}'".format(bonusPeriod))
    projectBonusValues = c.fetchall()

    totalTradePool = 0

    for i in range(len(projectBonusValues)):
        totalTradePool = totalTradePool+float(projectBonusValues[i][9])

    #===========================================
    #Counting the number of foremen employed this period: 

    #First, let's define the start date for this CTC period by using our "CTCcutoffDictionary" defined in step #0:
    #bonusPeriodDateRangeDictionary[periodName]=[startDateDT, endDateDT]
    bonusPeriodStartDate = bonusPeriodDateRangeDictionary[bonusPeriod][0]
    bonusPeriodEndDate = bonusPeriodDateRangeDictionary[bonusPeriod][1]

    #Next, let's pull a list of foreman from our "Users" database, and itterate through each entry keeping in mind hire/fire dates:
    userQuery = c.execute("SELECT * FROM Users WHERE position='{}'".format('Foreman'))
    userValues = c.fetchall()

    foremanCount = 2.25 #IMPORTANT! STARTING THE FOREMAN COUNT AT 2.25 BECAUSE OF THE 3 EMPLOYEES THAT EACH GET .75!

    for i in range(len(userValues)):
        #Pulling our hire/fire date values and saving them as datetime.datetime variables: 
        hireDate = userValues[i][8]
        fireDate = userValues[i][9]

        hireDateDT = datetime.datetime(int(hireDate[0:4]),int(hireDate[5:7]),int(hireDate[8:10]))

        if fireDate=='':
            fireDateDT = datetime.datetime.today()
        else:
            fireDateDT = datetime.datetime(int(fireDate[0:4]),int(fireDate[5:7]),int(fireDate[8:10]))

        #If the hire date is PRIOR to the bonus period start date, and the bonus period start date is BEFORE the fire date, we will add them to our foreman count:
        if hireDateDT<=bonusPeriodStartDate and fireDateDT>=bonusPeriodStartDate:
            foremanCount=foremanCount+1
        
        #If the hire date is AFTER to the bonus period start date and BEFORE the bonus period end date, we will add them to our foreman count:
        elif hireDateDT>bonusPeriodStartDate and fireDateDT>bonusPeriodEndDate:
            foremanCount=foremanCount+1

    #===========================================
    #Calcuating the % of the foreman trade pool that this foreman will get based on the amount of time that they have been at the company:

    #Calculating the total bonus pool duration in days:
    bonusPeriodStartDate = str(bonusPeriodDateRangeDictionary[bonusPeriod][0])
    bonusPeriodStartDateDT = datetime.datetime(int(bonusPeriodStartDate[0:4]),int(bonusPeriodStartDate[5:7]),int(bonusPeriodStartDate[8:10]))

    bonusPeriodEndDate = str(bonusPeriodDateRangeDictionary[bonusPeriod][1])
    bonusPeriodEndDateDT = datetime.datetime(int(bonusPeriodEndDate[0:4]),int(bonusPeriodEndDate[5:7]),int(bonusPeriodEndDate[8:10]))

    bonusPeriodDurationDT = bonusPeriodEndDateDT-bonusPeriodStartDateDT
    bonusPeriodDurationString = str(bonusPeriodDurationDT)
    bonusPeriodDurationDayCount = float(bonusPeriodDurationString[0:bonusPeriodDurationString.index(' ')])

    #Calculating the number of days that this foreman has been employed during this bonus period:
    userQuery = c.execute("SELECT * FROM Users WHERE employeeName='{}'".format(foreman))
    userValues = c.fetchall()

    hireDate = userValues[0][8]
    fireDate = userValues[0][9]

    hireDateDT = datetime.datetime(int(hireDate[0:4]),int(hireDate[5:7]),int(hireDate[8:10]))

    if fireDate=='':
        fireDateDT = datetime.datetime.today()
    else:
        fireDateDT = datetime.datetime(int(fireDate[0:4]),int(fireDate[5:7]),int(fireDate[8:10]))

    if hireDateDT>bonusPeriodStartDateDT:
        employedDayCountDT = bonusPeriodEndDateDT-hireDateDT
        employedDayCountString = str(employedDayCountDT)
        employedDayCount = float(employedDayCountString[0:employedDayCountString.index(' ')])
    else:
        employedDayCount = bonusPeriodDurationDayCount

    #Finally, saving a ratio of the # days employed/# days in bonus period to be used to calculate our total trade pool share for this foreman:
    if bonusPeriodDurationDayCount!=0:
        bonusPeriodEmployedPercent = employedDayCount/bonusPeriodDurationDayCount
    else:
        bonusPeriodEmployedPercent = 0


    #===========================================
    #Calculating our total trade pool share using our "foremanBonusPoolPercent" defined in section #1 and the "bonusPeriodEmployedPercent" defined above:

    #The "PreJan 2024" ctc period has a start date of 2000 and will cause the foreman count to return a 0 value, so if the foreman value is 0 let's just estimate 14 foremen for the Pre Jan 2024 period:
    if foremanCount!=0:
        tradePoolShare = totalTradePool*foremanBonusPoolPercent*bonusPeriodEmployedPercent/foremanCount
    else:
        tradePoolShare = totalTradePool*foremanBonusPoolPercent*bonusPeriodEmployedPercent/14

    #===========================================
    #Finally, becuase this will be shown for each month of the bonus period, let's divide the value by the number of months that the foreman worked in this bonus period:
    ccQuery = c.execute("SELECT * FROM Master_Foreman_Data WHERE foreman='{}' and bonusPeriod='{}'".format(foreman, bonusPeriod))
    ccValues = c.fetchall()

    ctcPeriodList = []

    for j in range(len(ccValues)):
        estaCTCperiod = ccValues[j][2]

        if estaCTCperiod not in ctcPeriodList:
            ctcPeriodList.append(estaCTCperiod)

    monthsWorkedCount = len(ctcPeriodList)

    if monthsWorkedCount!=0:
        tradePoolShare = tradePoolShare/monthsWorkedCount
    else:
        tradePoolShare = 0

    #endregion


    #=============================================================================================================
    #Calculating our paperwork values:
    #region 

    #===========================================
    #Adding up our paperwork totals:
    paperworkQuery = c.execute("SELECT * FROM Master_Paperwork_Data WHERE employeeName='{}' and ctcPeriod='{}'".format(foreman, ctcPeriod))
    paperworkValues = c.fetchall()

    totalPaperwork = 0
    totalOnTime = 0
    totalLate = 0

    for i in range(len(paperworkValues)):
        check = paperworkValues[i][4]
        totalPaperwork = totalPaperwork+1

        if check=='YES':
            totalOnTime = totalOnTime+1
        else:
            totalLate = totalLate+1

    #===========================================
    #Using our totals above to calculate the paperwork % and deduction amount
    if totalPaperwork!=0:
        paperworkPercent = totalOnTime/totalPaperwork
    else:
        paperworkPercent = 0

    paperwork = str(totalOnTime)+'/'+str(totalPaperwork)+str(" (")+str(round(paperworkPercent*100,2))+'%)'

    #Calculating a base bonus total to use in calculating our paperwork deduction amount
    baseTotalBonus = tradePoolShare+performanceBonus

    #Calculating the paperwork deduction amount: 
    paperworkDeduct=-.2*baseTotalBonus*(1-paperworkPercent)

    #endregion


    #=============================================================================================================
    #Calculating our safety values
    #region

    safetyQuery = c.execute("SELECT * FROM Master_Safety_Incident_Data WHERE employeeName='{}' and ctcPeriod='{}'".format(foreman, ctcPeriod))
    safetyValues = c.fetchall()

    safetyIncidents=len(safetyValues)

    safetyDeduct=-.3*tradePoolShare*safetyIncidents

    #endregion


    #=============================================================================================================
    #Calculating our total bonus value: 
    #region

    totalBonus=performanceBonus+tradePoolShare+paperworkDeduct+safetyDeduct

    #endregion


    #=============================================================================================================
    #Finally, updating our "foremanBonusDatabaseValueList" list:
    foremanBonusDatabaseValueList.append([trade, foreman, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, basePF, basePFcost, performanceBonus, paperworkDeduct, safetyDeduct, tradePoolShare, totalBonus, ctcPeriod, bonusPeriod, trueUpCost, trueUpEarned, trueUpOUbudget, omittedCost, omittedEarned, omittedOUbudget, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget, retainageWithheld])

    #endregion

#endregion


#=====================================================================================================================================================================================================================================
#=====================================================================================================================================================================================================================================
print('<========================================================================================================================>')
print('STEP #8: UPDATING OUR "Foreman_Bonus_Summary_Table" DATABASE TABLE WITH THE VALUES FROM STEP #7')
print('<========================================================================================================================>')
#region CLICK HERE TO EXPAND CODE FOR THIS SECTION

#=============================================================================================================
#First let's delete all previous entries in the database as they will be rewritten by this script:
def deleteMultipleRecords():
    c.execute("DELETE from Foreman_Bonus_Summary_Table ")
    conn.commit()

deleteMultipleRecords()

#=============================================================================================================
#Updating our database table: 
#foremanBonusDatabaseValueList.append([trade, foreman, totalCost, totalEarned, totalOUbudget, totalPF, paperwork, safetyIncidents, basePFdelta, basePF, basePFcost, performanceBonus, paperworkDeduct, safetyDeduct, tradePoolShare, totalBonus, ctcPeriod, bonusPeriod, trueUpCost, trueUpEarned, trueUpOUbudget, omittedCost, omittedEarned, omittedOUbudget, manualAdjustCost, manualAdjustEarned, manualAdjustOUbudget, retainageWithheld])

rowcount=1

for i in range(len(foremanBonusDatabaseValueList)):
    #=============================================================================================================
    #Including any "Add Ons" to the foreman bonuses for this period: 
    foreman = foremanBonusDatabaseValueList[i][1]
    ctcPeriod = foremanBonusDatabaseValueList[i][16]

    bonusAddOn = 0

    addOnQuery = c.execute("SELECT * FROM Master_Bonus_Add_On_Summary WHERE employeeName='{}' and ctcPeriod='{}'".format(foreman, ctcPeriod))
    addOnValues = c.fetchall()

    for j in range(len(addOnValues)):
        addOnAmt = float(addOnValues[j][4])
        bonusAddOn = bonusAddOn + addOnAmt

    #Incorporating the "Add Ons" value into our total bonus amount: 
    totalBonus = foremanBonusDatabaseValueList[i][15]+bonusAddOn


    #=============================================================================================================
    #Updating our database: 
    c.execute("INSERT INTO Foreman_Bonus_Summary_Table VALUES(:id, :trade, :foremanName, :totalCost, :totalEarned, :totalOUbudget, :totalPF, :paperwork, :safetyIncidents, :basePFdelta, :basePF, :baseCost, :performanceBonus, :paperworkDeduct, :safetyDeduct, :poolShare, :totalBonus, :ctcPeriod, :bonusPeriod, :trueUpCost, :trueUpEarned, :trueUpOUbudget, :omittedCost, :omittedEarned, :omittedOUbudget, :manualAdjustCost, :manualAdjustEarned, :manualAdjustOUbudget, :retainageWithheld, :bonusAddOns)",
            {
            'id':rowcount,
            'trade':foremanBonusDatabaseValueList[i][0],
            'foremanName':foremanBonusDatabaseValueList[i][1],
            'totalCost':str(foremanBonusDatabaseValueList[i][2]),
            'totalEarned':str(foremanBonusDatabaseValueList[i][3]),
            'totalOUbudget':str(foremanBonusDatabaseValueList[i][4]),
            'totalPF':str(foremanBonusDatabaseValueList[i][5]),
            'paperwork':foremanBonusDatabaseValueList[i][6],
            'safetyIncidents':str(foremanBonusDatabaseValueList[i][7]),
            'basePFdelta':str(foremanBonusDatabaseValueList[i][8]),
            'basePF':str(foremanBonusDatabaseValueList[i][9]),
            'baseCost':str(foremanBonusDatabaseValueList[i][10]),
            'performanceBonus':str(foremanBonusDatabaseValueList[i][11]),
            'paperworkDeduct':str(foremanBonusDatabaseValueList[i][12]),
            'safetyDeduct':str(foremanBonusDatabaseValueList[i][13]),
            'poolShare':str(foremanBonusDatabaseValueList[i][14]),
            'totalBonus':str(totalBonus), 
            'ctcPeriod':foremanBonusDatabaseValueList[i][16], 
            'bonusPeriod':foremanBonusDatabaseValueList[i][17], 
            'trueUpCost':str(foremanBonusDatabaseValueList[i][18]), 
            'trueUpEarned':str(foremanBonusDatabaseValueList[i][19]), 
            'trueUpOUbudget':str(foremanBonusDatabaseValueList[i][20]), 
            'omittedCost':str(foremanBonusDatabaseValueList[i][21]),
            'omittedEarned':str(foremanBonusDatabaseValueList[i][22]), 
            'omittedOUbudget':str(foremanBonusDatabaseValueList[i][23]), 
            'manualAdjustCost':str(foremanBonusDatabaseValueList[i][24]), 
            'manualAdjustEarned':str(foremanBonusDatabaseValueList[i][25]), 
            'manualAdjustOUbudget':str(foremanBonusDatabaseValueList[i][26]), 
            'retainageWithheld':str(foremanBonusDatabaseValueList[i][27]),
            'bonusAddOns': str(bonusAddOn)
            })

    rowcount=rowcount+1
    conn.commit()








#endregion


