import pytest
from make_booklet.creep import calculate_gutter

def test_calculate_gutter_outer_sheet():
    """Test the gutter calculation for the outermost sheet."""
    assert calculate_gutter(sheet_index=0, total_sheets=2, max_gutter=10.0) == pytest.approx(10.0)

def test_calculate_gutter_inner_sheet():
    """Test the gutter calculation for the innermost sheet."""
    assert calculate_gutter(sheet_index=1, total_sheets=2, max_gutter=10.0) == pytest.approx(0.0)

def test_calculate_gutter_middle_sheet():
    """Test the gutter calculation for a middle sheet in a 3-sheet booklet."""
    # 3 sheets -> indices 0, 1, 2
    # i=0 (outer): 10.0
    # i=1 (middle): 10.0 * (1 - 1/2) = 5.0
    # i=2 (inner): 0.0
    assert calculate_gutter(sheet_index=1, total_sheets=3, max_gutter=10.0) == pytest.approx(5.0)

def test_calculate_gutter_single_sheet():
    """Test the gutter calculation for a single-sheet booklet."""
    assert calculate_gutter(sheet_index=0, total_sheets=1, max_gutter=10.0) == pytest.approx(0.0)

def test_calculate_gutter_invalid_sheet_index_negative():
    """Test that a negative sheet index raises a ValueError."""
    with pytest.raises(ValueError, match="sheet_index -1 must be between 0 and 1"):
        calculate_gutter(sheet_index=-1, total_sheets=2, max_gutter=10.0)

def test_calculate_gutter_invalid_sheet_index_out_of_bounds():
    """Test that a sheet index exceeding the total number of sheets raises a ValueError."""
    with pytest.raises(ValueError, match="sheet_index 2 must be between 0 and 1"):
        calculate_gutter(sheet_index=2, total_sheets=2, max_gutter=10.0)

def test_calculate_gutter_invalid_total_sheets():
    """Test that non-positive total_sheets raises a ValueError."""
    with pytest.raises(ValueError, match="total_sheets 0 must be greater than 0"):
        calculate_gutter(sheet_index=0, total_sheets=0, max_gutter=10.0)

def test_calculate_gutter_invalid_max_gutter():
    """Test that negative max_gutter raises a ValueError."""
    with pytest.raises(ValueError, match="max_gutter -1.0 must be greater than or equal to 0"):
        calculate_gutter(sheet_index=0, total_sheets=1, max_gutter=-1.0)
