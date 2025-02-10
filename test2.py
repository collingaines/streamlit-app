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
projectLat = 33.0087803
projectLong = -96.7059305


coordinateMaxMins = get_lat_lng_bounds(projectLat, projectLong, radius_miles=2)

min_lat = coordinateMaxMins.get('min_lat')
max_lat = coordinateMaxMins.get('max_lat')
min_lng = coordinateMaxMins.get('min_lng')
max_lng = coordinateMaxMins.get('max_lng')


gpsCoordList = [['32.983532', '-96.729679'], ['32.983473', '-96.729611'], ['32.983473', '-96.729611'], ['32.983473', '-96.729611'], ['32.983473', '-96.729611'], ['32.983473', '-96.729611'], ['32.983473', '-96.729611'], ['32.983434', '-96.729627'], ['32.983692', '-96.729486'], ['32.986644', '-96.728297']]


equipmentProjectList = []

for i in range(len(gpsCoordList)):
    entryLat = float(gpsCoordList[i][0])
    entryLong = float(gpsCoordList[i][1])
    if entryLat>=min_lat and entryLat<=max_lat:
        if entryLong>=min_lng and entryLong<=max_lng:
            equipmentProjectList.append('Plano')
        else:
            equipmentProjectList.append('Ohter')
