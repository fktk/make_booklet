"""Page reordering logic for booklet PDF creation."""

def get_booklet_sequence(page_count: int, direction: str = 'ltr') -> list[int]:
    """Calculates the sequence of page indices for a booklet of a given size.

    Args:
        page_count: The total number of pages in the PDF. Must be a multiple of 4 and > 0.
        direction: 'ltr' (Left-to-Right) or 'rtl' (Right-to-Left).

    Returns:
        A list of page indices in the order they should appear in the booklet.

    Raises:
        ValueError: If page_count is not a multiple of 4 or is not positive.
    """
    if page_count <= 0:
        raise ValueError("Page count must be positive")
    if page_count % 4 != 0:
        raise ValueError("Page count must be a multiple of 4")

    sequence = []
    num_sheets = page_count // 4
    for i in range(num_sheets):
        # Front
        left_f = page_count - 1 - 2 * i
        right_f = 2 * i
        # Back
        left_b = 2 * i + 1
        right_b = page_count - 2 - 2 * i
        
        if direction == 'ltr':
            sequence.extend([left_f, right_f, left_b, right_b])
        else: # rtl
            sequence.extend([right_f, left_f, right_b, left_b])
    return sequence
