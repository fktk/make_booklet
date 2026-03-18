"""
Functions for splitting and refining PDF pages for booklet creation.
"""
import fitz

def split_pdf_pages(input_path: str, direction: str = 'ltr'):
    """
    Split each page of a 2-up PDF into two logical pages.

    Args:
        input_path: Path to the input PDF file.
        direction: 'ltr' (Left-to-Right) or 'rtl' (Right-to-Left).

    Returns:
        A tuple (doc, logical_pages) where doc is the fitz.Document
        and logical_pages is a list of (page_number, source_rect) tuples.
    """
    doc = fitz.open(input_path)
    logical_pages = []
    
    for page in doc:
        rect = page.rect
        width = rect.width
        height = rect.height
        mid_x = width / 2
        
        # Define left and right rectangles
        left_rect = fitz.Rect(0, 0, mid_x, height)
        right_rect = fitz.Rect(mid_x, 0, width, height)
        
        if direction == 'ltr':
            logical_pages.append((page.number, left_rect))
            logical_pages.append((page.number, right_rect))
        else: # rtl
            logical_pages.append((page.number, right_rect))
            logical_pages.append((page.number, left_rect))
            
    return doc, logical_pages

def refine_pages(logical_pages, exclude_indices=None, blank_pos=None):
    """
    Remove excluded pages and add blanks to pad to a multiple of 4.

    Args:
        logical_pages: List of (page_number, source_rect) tuples.
        exclude_indices: List of 0-based indices to remove.
        blank_pos: List of 0-based indices to insert blanks at.

    Returns:
        Refined list of logical pages.
    """
    # exclude_indices: list of 0-based indices
    if exclude_indices:
        # Filter by original index
        logical_pages = [p for i, p in enumerate(logical_pages) if i not in exclude_indices]
    
    # Insert blanks (None represents a blank page)
    if blank_pos:
        for pos in sorted(blank_pos, reverse=True):
            # pos is relative to the current state after exclusions
            if pos < 0:
                continue
            if pos >= len(logical_pages):
                logical_pages.append(None)
            else:
                logical_pages.insert(pos, None)
            
    # Pad to multiple of 4
    while len(logical_pages) % 4 != 0:
        logical_pages.append(None)
        
    return logical_pages
