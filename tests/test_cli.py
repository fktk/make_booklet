import pytest
from make_booklet.cli import parse_range

def test_parse_range_simple():
    assert parse_range("1,3,5") == [0, 2, 4]

def test_parse_range_dash():
    assert parse_range("1-3,5") == [0, 1, 2, 4]

def test_parse_range_empty():
    assert parse_range("") == []
    assert parse_range(None) == []

def test_parse_range_invalid():
    with pytest.raises(SystemExit):
        parse_range("abc")
    with pytest.raises(SystemExit):
        parse_range("1-x")
