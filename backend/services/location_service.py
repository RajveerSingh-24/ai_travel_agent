class LocationService:
    """Resolve common city names, IATA codes, and hotel search coordinates."""

    _LOCATIONS = {
        "delhi": "DEL",
        "new delhi": "DEL",
        "paris": "PAR",
        "new york": "NYC",
        "london": "LON",
        "mumbai": "BOM",
        "bombay": "BOM",
        "bangalore": "BLR",
        "bengaluru": "BLR",
        "dubai": "DXB",
        "singapore": "SIN",
        "tokyo": "TYO",
        "amsterdam": "AMS",
        "frankfurt": "FRA",
        "berlin": "BER",
        "rome": "ROM",
        "madrid": "MAD",
        "barcelona": "BCN",
        "zurich": "ZRH",
        "doha": "DOH",
        "abu dhabi": "AUH",
        "istanbul": "IST",
        "bangkok": "BKK",
        "hong kong": "HKG",
        "toronto": "YTO",
        "vancouver": "YVR",
        "los angeles": "LAX",
        "san francisco": "SFO",
        "chicago": "CHI",
        "boston": "BOS",
        "seattle": "SEA",
    }

    _COORDINATES = {
        "delhi": {"latitude": 28.6139, "longitude": 77.2090},
        "new delhi": {"latitude": 28.6139, "longitude": 77.2090},
        "paris": {"latitude": 48.8566, "longitude": 2.3522},
        "new york": {"latitude": 40.7128, "longitude": -74.0060},
        "london": {"latitude": 51.5074, "longitude": -0.1278},
        "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
        "bombay": {"latitude": 19.0760, "longitude": 72.8777},
        "bangalore": {"latitude": 12.9716, "longitude": 77.5946},
        "bengaluru": {"latitude": 12.9716, "longitude": 77.5946},
        "dubai": {"latitude": 25.2048, "longitude": 55.2708},
        "singapore": {"latitude": 1.3521, "longitude": 103.8198},
        "tokyo": {"latitude": 35.6762, "longitude": 139.6503},
        "amsterdam": {"latitude": 52.3676, "longitude": 4.9041},
        "frankfurt": {"latitude": 50.1109, "longitude": 8.6821},
        "berlin": {"latitude": 52.5200, "longitude": 13.4050},
        "rome": {"latitude": 41.9028, "longitude": 12.4964},
        "madrid": {"latitude": 40.4168, "longitude": -3.7038},
        "barcelona": {"latitude": 41.3874, "longitude": 2.1686},
        "zurich": {"latitude": 47.3769, "longitude": 8.5417},
        "doha": {"latitude": 25.2854, "longitude": 51.5310},
        "abu dhabi": {"latitude": 24.4539, "longitude": 54.3773},
        "istanbul": {"latitude": 41.0082, "longitude": 28.9784},
        "bangkok": {"latitude": 13.7563, "longitude": 100.5018},
        "hong kong": {"latitude": 22.3193, "longitude": 114.1694},
        "toronto": {"latitude": 43.6532, "longitude": -79.3832},
        "vancouver": {"latitude": 49.2827, "longitude": -123.1207},
        "los angeles": {"latitude": 34.0522, "longitude": -118.2437},
        "san francisco": {"latitude": 37.7749, "longitude": -122.4194},
        "chicago": {"latitude": 41.8781, "longitude": -87.6298},
        "boston": {"latitude": 42.3601, "longitude": -71.0589},
        "seattle": {"latitude": 47.6062, "longitude": -122.3321},
    }

    def resolve(self, location: str) -> str:
        """Resolve a city name or preserve an existing IATA code."""

        if not location or not location.strip():
            raise ValueError("Location cannot be empty")

        normalized = location.strip()

        if len(normalized) == 3 and normalized.isalpha():
            return normalized.upper()

        code = self._LOCATIONS.get(normalized.lower())

        if code is None:
            raise ValueError(f"Unknown location: {location}")

        return code

    def resolve_coordinates(self, location: str) -> dict[str, float]:
        """Resolve a supported city to latitude and longitude."""

        if not location or not location.strip():
            raise ValueError("Location cannot be empty")

        normalized = location.strip().lower()

        coordinates = self._COORDINATES.get(normalized)

        if coordinates is None:
            raise ValueError(f"Unknown location coordinates: {location}")

        return coordinates