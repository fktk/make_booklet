"""
Functions for splitting and refining PDF pages for booklet creation.
"""
import fitz
import io
import concurrent.futures
from make_booklet.reorder import get_booklet_sequence
from make_booklet.creep import calculate_gutter

def _scan_images(doc: fitz.Document, target_dpi: int):
    """
    Scan for images needing downsampling and return their target dimensions.
    
    Args:
        doc: The fitz.Document to scan.
        target_dpi: The target DPI for images.
        
    Returns:
        A list of tuples (xref, target_width, target_height).
    """
    xref_max_dpi = {}
    xref_orig_dims = {}

    for page in doc:
        seen_on_page = set()
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen_on_page:
                continue
            seen_on_page.add(xref)
            
            if xref not in xref_orig_dims:
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue
                xref_orig_dims[xref] = (base_image["width"], base_image["height"])
            
            orig_width, orig_height = xref_orig_dims[xref]
            rects = page.get_image_rects(xref)
            for rect in rects:
                # Effective DPI = (pixels / points) * 72
                eff_dpi_w = (orig_width / rect.width) * 72
                eff_dpi_h = (orig_height / rect.height) * 72
                eff_dpi = max(eff_dpi_w, eff_dpi_h)
                
                if xref not in xref_max_dpi or eff_dpi > xref_max_dpi[xref]:
                    xref_max_dpi[xref] = eff_dpi

    results = []
    for xref, max_dpi in sorted(xref_max_dpi.items()):
        if max_dpi > target_dpi:
            orig_width, orig_height = xref_orig_dims[xref]
            scale = target_dpi / max_dpi
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            if new_width > 0 and new_height > 0:
                results.append((xref, new_width, new_height))
    
    return results

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

def create_booklet(doc_in, logical_pages, output_path, max_gutter=0.0, direction='ltr', dpi: float = None):
    """
    Assemble the final booklet PDF with imposition and creep compensation.

    Args:
        doc_in: Input fitz.Document.
        logical_pages: Refined list of (page_number, source_rect) or None.
        output_path: Path for the output PDF file.
        max_gutter: Maximum gutter adjustment for outermost pages.
        direction: 'ltr' (Left-to-Right) or 'rtl' (Right-to-Left).
        dpi: Target DPI for downsampling images.
    """
    doc_out = fitz.open()
    num_pages = len(logical_pages)
    sequence = get_booklet_sequence(num_pages, direction=direction)
    
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
            
    if dpi is not None and dpi > 0:
        parallel_downsample_images(doc_out, dpi)

    doc_out.save(output_path, garbage=1, deflate=True)
    doc_out.close()

def convert_to_a4(input_path: str, output_path: str, orientation: str = 'auto', align: str = 'center'):
    """
    Convert a PDF to A4 size by scaling and positioning each page.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path to the output PDF file.
        orientation: 'auto' (match input), 'portrait', or 'landscape'.
        align: 'center', 'left', 'right', 'top', or 'bottom'.
    """
    doc = fitz.open(input_path)
    doc_out = fitz.open()
    
    # A4 dimensions in points
    A4_P_W, A4_P_H = 595.28, 841.89
    A4_L_W, A4_L_H = 841.89, 595.28
    
    for page in doc:
        # Determine target A4 size
        if orientation == 'auto':
            if page.rect.width > page.rect.height:
                target_w, target_h = A4_L_W, A4_L_H
            else:
                target_w, target_h = A4_P_W, A4_P_H
        elif orientation == 'landscape':
            target_w, target_h = A4_L_W, A4_L_H
        else: # portrait
            target_w, target_h = A4_P_W, A4_P_H
            
        new_page = doc_out.new_page(width=target_w, height=target_h)
        
        # Calculate scaling to fit while preserving aspect ratio
        scale_w = target_w / page.rect.width
        scale_h = target_h / page.rect.height
        scale = min(scale_w, scale_h)
        
        new_w = page.rect.width * scale
        new_h = page.rect.height * scale
        
        # Calculate positioning based on alignment
        if align == 'left':
            x = 0
            y = (target_h - new_h) / 2
        elif align == 'right':
            x = target_w - new_w
            y = (target_h - new_h) / 2
        elif align == 'top':
            x = (target_w - new_w) / 2
            y = 0
        elif align == 'bottom':
            x = (target_w - new_w) / 2
            y = target_h - new_h
        else: # center
            x = (target_w - new_w) / 2
            y = (target_h - new_h) / 2
            
        target_rect = fitz.Rect(x, y, x + new_w, y + new_h)
        new_page.show_pdf_page(target_rect, doc, page.number)
        
    doc_out.save(output_path)
    doc_out.close()
    doc.close()

def _resize_pixmap_task(pix: fitz.Pixmap, width: int, height: int) -> fitz.Pixmap:
    """
    Rescale a Pixmap to target dimensions.
    This constructor performs the resizing and releases the GIL.
    """
    return fitz.Pixmap(pix, width, height)

def parallel_downsample_images(doc: fitz.Document, target_dpi: int = 150):
    """
    Downsample images in the PDF in parallel using multiple CPU threads.
    
    Args:
        doc: The fitz.Document to process.
        target_dpi: The target dots per inch for images.
    """
    # 1. Scan for images that need downsampling
    tasks = _scan_images(doc, target_dpi)
    if not tasks:
        return

    # 2. Parallel resize using ThreadPoolExecutor
    # PyMuPDF releases the GIL for Pixmap resizing.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_xref = {}
        for xref, target_w, target_h in tasks:
            try:
                # Create the initial Pixmap in the main thread (accesses document objects)
                pix = fitz.Pixmap(doc, xref)
                # Submit resizing to thread pool
                future = executor.submit(_resize_pixmap_task, pix, target_w, target_h)
                future_to_xref[future] = xref
            except Exception as e:
                print(f"Error preparing image xref {xref} for downsampling: {e}")

        # 3. Collect results and update the document in the main thread
        for future in concurrent.futures.as_completed(future_to_xref):
            xref = future_to_xref[future]
            try:
                scaled_pix = future.result()
                # Update the image in the PDF.
                # Use doc.update_image if available (PyMuPDF 1.25+), otherwise use page.replace_image.
                if hasattr(doc, "update_image"):
                    doc.update_image(xref, pixmap=scaled_pix)
                elif len(doc) > 0:
                    doc[0].replace_image(xref, pixmap=scaled_pix)
            except Exception as e:
                print(f"Error downsampling image xref {xref}: {e}")
