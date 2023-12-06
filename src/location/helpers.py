from vincenty import vincenty

from location.geopoint import GeoPoint


def calculate_distance(first_point: GeoPoint, second_point: GeoPoint) -> float:
    """
    Calculate distance using Vincenty's formula

    :param first_point: longitude, latitude,
    :param second_point: longitude, latitude
    :return: float distance in km
    """
    return vincenty(first_point, second_point, miles=False)
