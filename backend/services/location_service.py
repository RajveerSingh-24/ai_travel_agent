class LocationService:
    """Resolve common city names and IATA airport/city codes."""

    _LOCATIONS = {
        "delhi": "DEL",
        "new delhi": "DEL",
        "paris": "PAR",
        "new york": "NYC",
        "london": "LON",
        "mumbai": "BOM",
        "bangalore": "BLR",
        "bengaluru": "BLR",
        "dubai": "DXB",
        "singapore": "SIN",
    }

    def resolve(self, location: str) -> str:
        """Resolve a city name or preserve an existing IATA code."""
        if not location or not location.strip():
            raise ValueError("Location cannot be empty")

        normalized = location.strip()

        # Already an IATA-style code.
        if len(normalized) == 3 and normalized.isalpha():
            return normalized.upper()

        code = self._LOCATIONS.get(normalized.lower())

        if code is None:
            raise ValueError(f"Unknown location: {location}")

        return code