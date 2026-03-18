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
