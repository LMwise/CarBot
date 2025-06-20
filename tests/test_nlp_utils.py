from unittest.mock import patch
import nlp_utils


@patch('nlp_utils.get_city_coordinates', return_value=(52.0, 21.0))
def test_calculate_delivery_cost(mock_get_coords):
    info, cost = nlp_utils.calculate_delivery_cost("Warsaw")
    assert "км" in info
    assert cost > 0
