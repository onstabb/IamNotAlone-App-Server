from vincenty import vincenty

from geodata.geopoint import GeoPoint


def calculate_distance(first_point: GeoPoint, second_point: GeoPoint) -> float:

    """
    :param first_point: longitude, latitude,
    :param second_point: longitude, latitude
    :return: float distance in km
    """
    return vincenty(first_point, second_point, miles=False)



def calculate_distance_(longitude_1: float, latitude_1: float, longitude_2: float, latitude_2: float) -> float:
    return calculate_distance((longitude_1, latitude_1), (longitude_2, latitude_2))
