import math 
from locations.models import Location

def calculate_distance(job_locations: list, talent_locations: list) -> list[tuple[str, str, int]]:
    """
    Calculate the distance between all combinations of talent locations and job locations using the Haversine formula.

    Parameters:
        job_locations: 
             A list of job location objects, each containing "formatted_address", "latitude" and "longtitude"
        talent_locations: 
             A list of talent location objects, each containing "formatted_address", "latitude" and "longtitude" 

    Returns:
         A list of tuples where each tuple contains (talent location, job location, distance).
    """

    distances = []

    for talent_location in talent_locations:
        talent_address = talent_location.display_name
        talent_latitude, talent_longitude = talent_location.details.latitude, talent_location.details.longitude

        for job_location in job_locations:
            job_address = job_location.display_name
            job_latitude, job_longitude = job_location.details.latitude, job_location.details.longitude

            dist = haversine(job_latitude, job_longitude, talent_latitude, talent_longitude)
            distances.append((talent_address, job_address, dist))

    # if talent location/job location unknown
    if not distances:
        return [("No Talent Location", "No Job Location", float('inf'))]

    return distances


# https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Calculate the great-circle distance between two points on the Earth using the Haversine formula.

    Parameters:
        lat1: float 
            Latitude of the first point in degrees.
        lon1: float 
            Longitude of the first point in degrees.
        lat2: float 
            Latitude of the second point in degrees.
        lon2: float 
            Longitude of the second point in degrees.

    Returns:
        int: 
           The distance between the two points in kilometers, rounded to the nearest int.
    """
    
     # distance between latitudes and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
    
    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2  = (lat2) * math.pi / 180.0

    a = (pow(math.sin(dLat / 2), 2) + pow(math.sin(dLon / 2), 2) * math.cos(lat1) * math.cos(lat2))
    c = 2 * math.asin(math.sqrt(a))
    R = 6371    #earths radius (KM)
    distance = R * c

    # round to nearest int
    return round(distance) 



# currently not being used 
def process_location_update(user_input: str, job_locations: list) -> tuple[str, float]:
    """
    Processes user's location response update during interview

    Inputs:
        user_input (str): location provided by user
        job_locations (list): list of job location objects

    Returns:
        tuple:
            - (str) Updated location or "Invalid" if ignored
            - (float) Updated min distance or set to float("inf") if unknown
    """

    user_input = user_input.strip().lower()

    # ignore invalid location responses
    INVALID_RESPONSES = {"no", "not sure", "maybe", "i don't know", "n/a"}

    if user_input in INVALID_RESPONSES:
        return "Invalid", None 

    matching_location = Location.objects.filter(label__iexact=user_input).first()
    
    if matching_location and matching_location.details:
        updated_lat = matching_location.details.latitude
        updated_lon = matching_location.details.longitude
        print(f"found existing location in database: {matching_location.display_name} ({updated_lat}, {updated_lon})") # remove later
    
        updated_distances = calculate_distance(job_locations, [matching_location])
        print("TESTING: UPDATED DISTANCE= ", updated_distances)

        if updated_distances: 
            min_dist = min(updated_distances, key=lambda x: x[2])[2]  
            print(f"updated min_dist to {min_dist}") # remove later
        else:
            min_dist = float("inf")

        return matching_location.display_name, min_dist

    else:
        print(f"{user_input} not found in database, defaulting to unknown location")
        return "Unknown", float("inf")
