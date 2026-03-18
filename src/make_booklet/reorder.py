"""Page reordering logic for booklet PDF creation."""

def get_booklet_sequence(page_count: int) -> list[int]:
    """Calculates the sequence of page indices for a booklet of a given size.

    Args:
        page_count: The total number of pages in the PDF. Must be a multiple of 4 and > 0.

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
        sequence.append(page_count - 1 - 2 * i)
        sequence.append(2 * i)
        # Back
        sequence.append(2 * i + 1)
        sequence.append(page_count - 2 - 2 * i)
    return sequence
