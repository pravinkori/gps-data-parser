def is_valid_latitude(lat):
    """Validate if a given value is a valid latitude."""
    return -90 <= lat <= 90

def is_valid_longitude(lon):
    """Validate if a given value is a valid longitude."""
    return -180 <= lon <= 180
