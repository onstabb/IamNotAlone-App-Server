import pytest

from geodata import helpers


@pytest.mark.parametrize(
    "coordinates_1, coordinates_2, expected_distance_km",
    [
        ([11.0, 12.0], [3.0, 54.0], 4712),
        ([0.0, 0.0], [0, 0.0], 0)
    ]
)
def test_calculate_distance(coordinates_1, coordinates_2, expected_distance_km):
    assert round(helpers.calculate_distance(coordinates_1, coordinates_2) / 1000) == expected_distance_km
