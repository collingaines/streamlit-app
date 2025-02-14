from geopy.geocoders import Nominatim

def get_city_from_coordinates(latitude, longitude):
    """
    Returns the city name for the given latitude and longitude coordinates.

    :param latitude: float, Latitude of the location
    :param longitude: float, Longitude of the location
    :return: str, City name or 'Unknown location' if not found
    """
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    
    if location and 'address' in location.raw:
        address = location.raw['address']
        city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
        return city if city else "Unknown location"
    
    return "Unknown location"

# Example usage:
latitude = 40.7128
longitude = -74.0060
print(get_city_from_coordinates(latitude, longitude))  # Expected output: New York



