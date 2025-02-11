#=========================================
#Writing our function for pulling the lat/long range for each project
import math

def get_lat_lng_bounds(lat, lng, radius_miles=1.5):
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



#=============================================================================================================
#Event center coordinates
projectLat = 33.0541
projectLong = -96.6847


coordinateMaxMins = get_lat_lng_bounds(projectLat, projectLong, radius_miles=1.5)

min_lat = coordinateMaxMins.get('min_lat')
max_lat = coordinateMaxMins.get('max_lat')
min_lng = coordinateMaxMins.get('min_lng')
max_lng = coordinateMaxMins.get('max_lng')


gpsCoordList = [
    ['33.055357', '-96.68572'],
    ['33.055357', '-96.68572'],
    ['33.055357', '-96.68572'],
    ['33.055328', '-96.685714'],
    ['33.055328', '-96.685714'],
    ['33.055328', '-96.685714'],
    ['33.055328', '-96.685714'],
    ['33.055328', '-96.685714'],
    ['33.055328', '-96.685714'],
    ['33.055342', '-96.685713'],
    ['33.055342', '-96.685713'],
    ['33.055342', '-96.685713'],
    ['33.055342', '-96.685713'],
    ['33.055342', '-96.685713'],
    ['33.055342', '-96.685713'],
    ['33.055349', '-96.685733'],
    ['33.055349', '-96.685733'],
    ['33.055349', '-96.685733'],
    ]


equipmentProjectList = []

for i in range(len(gpsCoordList)):
    entryLat = float(gpsCoordList[i][0])
    entryLong = float(gpsCoordList[i][1])
    
    if entryLat>=min_lat and entryLat<=max_lat:
        if entryLong>=min_lng and entryLong<=max_lng:
            equipmentProjectList.append('Event Center')
        else:
            equipmentProjectList.append('Ohter')

print(equipmentProjectList)

print(most_frequent(equipmentProjectList))






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
HCSS_API_ENDPOINT = "https://api.hcssapps.com/telematics/api/v1/equipment"

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
















