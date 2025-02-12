


#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
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




#==========================================================================================================================
#Creating a list of timecard values for use later in calculating the timecard values for each foreman:
#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/heavyjob/api/v1/hours/equipment"

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
        # "limit": "1000000"
}

#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

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

twoWeeksAgoUTC = current_utc_time - timedelta(weeks=8)

startDate = str(twoWeeksAgoUTC)[0:10]+'T00:00:00'


#Defining our "payload" which will be the filter information that we send to the HCSS API:
payload = {
    
    "startDate": startDate,
    "endDate": endDate,
    }

#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.post(HCSS_API_ENDPOINT, headers=HEADERS, json=payload)

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


            #Finally, updating our list. Let's keep it inside of this loop so that a new row of our databse is added for each cost code entry for this equipment:
            
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


dateList = []

for i in range(len(equipmentHourInfoList)):
    if equipmentHourInfoList[i][20]!=None:
        print(equipmentHourInfoList[i])









#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
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




#==========================================================================================================================
#Creating a list of timecard values for use later in calculating the timecard values for each foreman:
#============================================
#Connecting to the timecard endpoint of the HCSS API:
HCSS_API_ENDPOINT = "https://api.hcssapps.com/heavyjob/api/v1/hours/employees"

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
        # "limit": "1000000"
}

#Passing our token value generated above to our "HEADERS" variable:
HEADERS = {
"Authorization": "Bearer {}".format(token)
}

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
    "includeInactiveEmployees": True,
    "startDate": startDate,
    "endDate": endDate,
    }

#Finally, let's generate store our response which includes all of our raw data to a variable:
response = requests.post(HCSS_API_ENDPOINT, headers=HEADERS, json=payload)

#A 200 response status code means that the request was successful! Thusly if this repsonse is returned, we will run our script:
if response.status_code == 200:
    data2 = response.json()

    results2 = data.get('results')

    

    #for i in range(len(results)):
        #equipmentHCSSAPIid = results[i].get('equipment').get('equipmentId')
        















