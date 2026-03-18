def calculate_gutter(sheet_index, total_sheets, max_gutter):
    if total_sheets <= 1:
        return 0.0
    return max_gutter * (1 - sheet_index / (total_sheets - 1))
