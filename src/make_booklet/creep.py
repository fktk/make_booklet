"""
Core logic for creep (gutter) calculation in booklet creation.
"""

def calculate_gutter(sheet_index: int, total_sheets: int, max_gutter: float) -> float:
    """
    Calculate the gutter (creep) adjustment for a given sheet index.

    Args:
        sheet_index: The 0-based index of the current sheet (0 is the outermost).
        total_sheets: The total number of physical sheets in the booklet (must be > 0).
        max_gutter: The maximum gutter adjustment for the outermost sheet (must be >= 0).

    Returns:
        The calculated gutter adjustment for the current sheet.

    Raises:
        ValueError: If sheet_index is outside the valid range [0, total_sheets),
                    if total_sheets <= 0, or if max_gutter < 0.
    """
    if total_sheets <= 0:
        raise ValueError(f"total_sheets {total_sheets} must be greater than 0")

    if max_gutter < 0:
        raise ValueError(f"max_gutter {max_gutter} must be greater than or equal to 0")

    if not (0 <= sheet_index < total_sheets):
        raise ValueError(f"sheet_index {sheet_index} must be between 0 and {total_sheets - 1}")

    if total_sheets <= 1:
        return 0.0

    return max_gutter * (1 - sheet_index / (total_sheets - 1))
