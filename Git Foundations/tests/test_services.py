from app.services import calculate_premium, is_valid_email


def test_young_non_smoker_pays_base():
    assert calculate_premium(200, 25, False) == 200


def test_smoker_loading_applies():
    assert calculate_premium(200, 25, True) == 260


def test_older_age_band_costs_more():
    assert calculate_premium(200, 65, False) > calculate_premium(200, 35, False)


def test_email_validation():
    assert is_valid_email("a@b.co")
    assert not is_valid_email("not-an-email")
