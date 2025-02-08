import pytest
import datetime
import pytz
from src.utils.helpers import (
    is_valid_latitude,
    is_valid_longitude,
    knots_to_kmh,
    decimal_degrees_to_dms,
    utc_to_timezone,
    format_gps_datetime,
    parse_gngga_sentence,
    parse_gnvtg_sentence
)

def test_is_valid_latitude():
    assert is_valid_latitude(45)
    assert not is_valid_latitude(-100)

def test_is_valid_longitude():
    assert is_valid_longitude(120)
    assert not is_valid_longitude(200)

def test_knots_to_kmh():
    assert knots_to_kmh(10) == 18.52

def test_decimal_degrees_to_dms():
    d, m, s = decimal_degrees_to_dms(12.3456)
    assert isinstance(d, int)
    assert isinstance(m, int)
    assert isinstance(s, float)

def test_utc_to_timezone():
    utc_time = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=pytz.utc)
    local_time = utc_to_timezone(utc_time, 'Asia/Kolkata')
    # Asia/Kolkata is UTC+5:30, so expect 17:30 (12:00 + 5:30)
    assert local_time.hour == 17 and local_time.minute == 30

def test_format_gps_datetime():
    date = "2024-01-01"
    time = "17:30:00"
    formatted = format_gps_datetime(date, time)
    assert formatted == "2024-01-01T17:30:00"

def test_parse_gngga_sentence_valid():
    sentence = "$GNGGA,123519.00,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    result = parse_gngga_sentence(sentence)
    assert result is not None
    assert 'latitude' in result
    assert 'longitude' in result

def test_parse_gnvtg_sentence_valid():
    sentence = "$GNVTG,054.7,T,034.4,M,005.5,N,010.2,K*48"
    result = parse_gnvtg_sentence(sentence)
    assert result is not None
    assert 'speed_kmh' in result
    assert 'bearing' in result

def test_parse_gngga_sentence_invalid():
    sentence = "Invalid Sentence"
    result = parse_gngga_sentence(sentence)
    assert result is None

def test_parse_gnvtg_sentence_invalid():
    sentence = "Invalid Sentence"
    result = parse_gnvtg_sentence(sentence)
    assert result is None
