import math

from src.geodata.basetypes import GeoPoint


def calculate_distance(first_point: GeoPoint, second_point: GeoPoint) -> float:

    """
    Nathan A. Rooy
    2016-SEP-30
    Solve the inverse Vincenty's formulae
    https://en.wikipedia.org/wiki/Vincenty%27s_formulae
    :param first_point: longitude, latitude,
    :param second_point: longitude, latitude
    :return: float distance in meters
    """

    if first_point == second_point:
        return 0.0

    radius_m: float = 6378137.0  # radius at equator in meters (WGS-84)
    ellipsoid_flattening: float = 1 / 298.257223563  # flattening of the ellipsoid (WGS-84)
    b: float = (1 - ellipsoid_flattening) * radius_m
    tolerance: int = 10 ** -12

    l_1, phi_1 = first_point
    l_2, phi_2 = second_point

    u_1: float = math.atan((1 - ellipsoid_flattening) * math.tan(math.radians(phi_1)))
    u_2: float = math.atan((1 - ellipsoid_flattening) * math.tan(math.radians(phi_2)))

    l_: float = math.radians(l_2 - l_1)

    lambda_: float = l_

    sin_u1: float = math.sin(u_1)
    cos_u1: float = math.cos(u_1)
    sin_u2: float = math.sin(u_2)
    cos_u2: float = math.cos(u_2)

    while True:
        cos_lambda: float = math.cos(lambda_)
        sin_lambda: float = math.sin(lambda_)
        sin_sigma: float = math.sqrt(
            (cos_u2 * math.sin(lambda_)) ** 2 + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) ** 2
        )
        cos_sigma: float = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma: float = math.atan2(sin_sigma, cos_sigma)
        sin_alpha: float = (cos_u1 * cos_u2 * sin_lambda) / sin_sigma
        cos_sq_alpha: float = 1 - sin_alpha ** 2
        cos2_sigma_m: float = cos_sigma - ((2 * sin_u1 * sin_u2) / cos_sq_alpha)
        c_: float = (ellipsoid_flattening / 16) * cos_sq_alpha * (4 + ellipsoid_flattening * (4 - 3 * cos_sq_alpha))
        lambda_prev: float = lambda_
        lambda_ = l_ + (1 - c_) * ellipsoid_flattening * sin_alpha * (
                    sigma + c_ * sin_sigma * (cos2_sigma_m + c_ * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2)))

        # successful convergence
        diff: float = abs(lambda_prev - lambda_)
        if diff <= tolerance:
            break

    u_sq: float = cos_sq_alpha * ((radius_m ** 2 - b ** 2) / b ** 2)
    a_: float = 1 + (u_sq / 16384) * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    b_: float = (u_sq / 1024) * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
    delta_sig: float = b_ * sin_sigma * (cos2_sigma_m + 0.25 * b_ * (
                cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) - (1 / 6) * b_ * cos2_sigma_m * (
                    -3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)))

    meters: float = b * a_ * (sigma - delta_sig)  # output distance in meters
    return meters


def calculate_distance_(longitude_1: float, latitude_1: float, longitude_2: float, latitude_2: float) -> float:
    return calculate_distance((longitude_1, latitude_1), (longitude_2, latitude_2))


if __name__ == '__main__':
    print(calculate_distance([115.24941, -2.41773], [90, -90]))