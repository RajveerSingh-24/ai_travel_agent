import pytest

from services.location_service import LocationService


@pytest.fixture
def location_service():
    return LocationService()


def test_resolves_delhi_to_iata_code(location_service):
    assert location_service.resolve("Delhi") == "DEL"


def test_resolves_paris_to_iata_code(location_service):
    assert location_service.resolve("Paris") == "PAR"


def test_resolves_new_york_to_iata_code(location_service):
    assert location_service.resolve("New York") == "NYC"


def test_accepts_existing_iata_code(location_service):
    assert location_service.resolve("DEL") == "DEL"


def test_is_case_insensitive(location_service):
    assert location_service.resolve("delhi") == "DEL"


def test_unknown_location_raises_error(location_service):
    with pytest.raises(ValueError, match="Unknown location"):
        location_service.resolve("Atlantis")

def test_resolves_bengaluru_to_iata_code(location_service):
    assert location_service.resolve("Bengaluru") == "BLR"


def test_resolves_bombay_to_mumbai_iata_code(location_service):
    assert location_service.resolve("Bombay") == "BOM"


def test_resolves_tokyo_to_iata_code(location_service):
    assert location_service.resolve("Tokyo") == "TYO"


def test_resolves_san_francisco_to_iata_code(location_service):
    assert location_service.resolve("San Francisco") == "SFO"


def test_preserves_lowercase_iata_code_as_uppercase(location_service):
    assert location_service.resolve("del") == "DEL"