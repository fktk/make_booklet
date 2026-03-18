from make_booklet.creep import calculate_gutter

def test_calculate_gutter():
    # 8 pages -> 2 sheets (i=0, i=1)
    # i=0 (outer): max_gutter
    # i=1 (inner): 0
    assert calculate_gutter(sheet_index=0, total_sheets=2, max_gutter=10.0) == 10.0
    assert calculate_gutter(sheet_index=1, total_sheets=2, max_gutter=10.0) == 0.0

def test_calculate_gutter_single_sheet():
    assert calculate_gutter(0, 1, 10.0) == 0.0
