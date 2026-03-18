import pytest
from make_booklet.reorder import get_booklet_sequence

def test_get_booklet_sequence_4():
    # 4 pages -> 1 sheet (front: 3,0; back: 1,2)
    assert get_booklet_sequence(4) == [3, 0, 1, 2]

def test_get_booklet_sequence_8():
    # 8 pages -> 2 sheets
    # Sheet 0 front: 7,0; back: 1,6
    # Sheet 1 front: 5,2; back: 3,4
    assert get_booklet_sequence(8) == [7, 0, 1, 6, 5, 2, 3, 4]

def test_get_booklet_sequence_invalid_not_multiple_of_4():
    with pytest.raises(ValueError, match="Page count must be a multiple of 4"):
        get_booklet_sequence(2)
    with pytest.raises(ValueError, match="Page count must be a multiple of 4"):
        get_booklet_sequence(6)

def test_get_booklet_sequence_invalid_zero():
    with pytest.raises(ValueError, match="Page count must be positive"):
        get_booklet_sequence(0)

def test_get_booklet_sequence_invalid_negative():
    with pytest.raises(ValueError, match="Page count must be positive"):
        get_booklet_sequence(-4)
