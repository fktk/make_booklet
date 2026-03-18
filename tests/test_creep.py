import pytest
from make_booklet.creep import calculate_gutter

def test_calculate_gutter_outer_sheet():
    """Test the gutter calculation for the outermost sheet."""
    assert calculate_gutter(sheet_index=0, total_sheets=2, max_gutter=10.0) == 10.0

def test_calculate_gutter_inner_sheet():
    """Test the gutter calculation for the innermost sheet."""
    assert calculate_gutter(sheet_index=1, total_sheets=2, max_gutter=10.0) == 0.0

def test_calculate_gutter_single_sheet():
    """Test the gutter calculation for a single-sheet booklet."""
    assert calculate_gutter(sheet_index=0, total_sheets=1, max_gutter=10.0) == 0.0

def test_calculate_gutter_invalid_sheet_index_negative():
    """Test that a negative sheet index raises a ValueError."""
    with pytest.raises(ValueError, match="sheet_index -1 must be between 0 and 1"):
        calculate_gutter(sheet_index=-1, total_sheets=2, max_gutter=10.0)

def test_calculate_gutter_invalid_sheet_index_out_of_bounds():
    """Test that a sheet index exceeding the total number of sheets raises a ValueError."""
    with pytest.raises(ValueError, match="sheet_index 2 must be between 0 and 1"):
        calculate_gutter(sheet_index=2, total_sheets=2, max_gutter=10.0)
