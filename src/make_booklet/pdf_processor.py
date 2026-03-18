"""
Functions for splitting and refining PDF pages for booklet creation.
"""
import fitz
from make_booklet.reorder import get_booklet_sequence
from make_booklet.creep import calculate_gutter

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

def create_booklet(doc_in, logical_pages, output_path, max_gutter=0.0):
    """
    Assemble the final booklet PDF with imposition and creep compensation.

    Args:
        doc_in: Input fitz.Document.
        logical_pages: Refined list of (page_number, source_rect) or None.
        output_path: Path for the output PDF file.
        max_gutter: Maximum gutter adjustment for outermost pages.
    """
    doc_out = fitz.open()
    num_pages = len(logical_pages)
    sequence = get_booklet_sequence(num_pages)
    
    total_sheets = num_pages // 4
    
    # Get original page size (assume all same)
    ref_page = doc_in[0]
    orig_w, orig_h = ref_page.rect.width, ref_page.rect.height
    
    for i in range(total_sheets * 2): # 2 physical pages per sheet (front and back)
        sheet_idx = i // 2
        # i: 0 (Sheet 0 Front), 1 (Sheet 0 Back), 2 (Sheet 1 Front), 3 (Sheet 1 Back)
        
        new_page = doc_out.new_page(width=orig_w, height=orig_h)
        
        gutter = calculate_gutter(sheet_idx, total_sheets, max_gutter)
        
        # Sequence for this physical page
        page_indices = sequence[i*2 : i*2+2]
        
        for side_idx, log_idx in enumerate(page_indices):
            # log_idx is index into logical_pages
            if log_idx is None or log_idx >= len(logical_pages) or logical_pages[log_idx] is None:
                continue
                
            src_page_num, src_rect = logical_pages[log_idx]
            
            # Destination half width
            dest_half_w = orig_w / 2
            
            if side_idx == 0: # Left side of physical sheet
                # Fold is on the RIGHT of this half
                # Apply gutter to the RIGHT side (inner)
                inner_rect = fitz.Rect(0, 0, dest_half_w - gutter, orig_h)
            else: # Right side of physical sheet
                # Fold is on the LEFT of this half
                # Apply gutter to the LEFT side (inner)
                inner_rect = fitz.Rect(dest_half_w + gutter, 0, orig_w, orig_h)

            # Draw page content into inner_rect with scaling
            new_page.show_pdf_page(inner_rect, doc_in, src_page_num, clip=src_rect)
            
    doc_out.save(output_path)
    doc_out.close()
