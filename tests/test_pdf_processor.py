import os
import fitz
import pytest
from make_booklet.pdf_processor import split_pdf_pages

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample 2-up landscape PDF for testing."""
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    # Landscape A4: approx 842 x 595
    width, height = 842, 595
    for i in range(2):
        page = doc.new_page(width=width, height=height)
        # Draw some text or lines to distinguish
        page.insert_text((10, 20), f"Page {i+1} Left", fontsize=12)
        page.insert_text((width/2 + 10, 20), f"Page {i+1} Right", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_split_pdf_pages_ltr(sample_pdf):
    """Test splitting a 2-up PDF with Left-to-Right direction."""
    doc, logical_pages = split_pdf_pages(sample_pdf, direction='ltr')
    
    # 2 physical pages -> 4 logical pages
    assert len(logical_pages) == 4
    
    # Check rects for first page
    p0_num, p0_rect = logical_pages[0]
    p1_num, p1_rect = logical_pages[1]
    
    assert p0_num == 0
    assert p1_num == 0
    assert p0_rect == fitz.Rect(0, 0, 421, 595)
    assert p1_rect == fitz.Rect(421, 0, 842, 595)
    
    doc.close()

def test_split_pdf_pages_rtl(sample_pdf):
    """Test splitting a 2-up PDF with Right-to-Left direction."""
    doc, logical_pages = split_pdf_pages(sample_pdf, direction='rtl')
    
    # 2 physical pages -> 4 logical pages
    assert len(logical_pages) == 4
    
    # Check rects for first page - RTL should swap left and right
    p0_num, p0_rect = logical_pages[0]
    p1_num, p1_rect = logical_pages[1]
    
    assert p0_num == 0
    assert p1_num == 0
    # Right half first
    assert p0_rect == fitz.Rect(421, 0, 842, 595)
    # Left half second
    assert p1_rect == fitz.Rect(0, 0, 421, 595)
    
    doc.close()

def test_refine_pages():
    from make_booklet.pdf_processor import refine_pages
    
    # 5 pages
    logical_pages = [(0, None), (1, None), (2, None), (3, None), (4, None)]
    
    # Exclude page 1 (index 0) and page 3 (index 2)
    # Remaining: (1, None), (3, None), (4, None)
    refined = refine_pages(logical_pages, exclude_indices=[0, 2])
    assert len(refined) == 4 # 3 remaining + 1 pad
    assert refined[0] == (1, None)
    assert refined[1] == (3, None)
    assert refined[2] == (4, None)
    assert refined[3] is None
    
def test_refine_pages_exclusion_and_padding():
    from make_booklet.pdf_processor import refine_pages
    logical_pages = ["A", "B", "C", "D", "E"]
    
    # Exclude "A" (0) and "C" (2). Remaining: ["B", "D", "E"]
    # Pad to 4: ["B", "D", "E", None]
    refined = refine_pages(logical_pages, exclude_indices=[0, 2])
    assert refined == ["B", "D", "E", None]

def test_refine_pages_blank_insertion():
    from make_booklet.pdf_processor import refine_pages
    logical_pages = ["A", "B", "C"]
    
    # Insert blank at index 1 (between A and B)
    # Result before padding: ["A", None, "B", "C"]
    # No padding needed as it's already multiple of 4
    refined = refine_pages(logical_pages, blank_pos=[1])
    assert refined == ["A", None, "B", "C"]

def test_refine_pages_complex():
    from make_booklet.pdf_processor import refine_pages
    logical_pages = ["A", "B", "C", "D", "E"]
    # 1. Exclude 0(A), 2(C). Remaining: ["B", "D", "E"]
    # 2. Insert blank at index 1 (between B and D). Result: ["B", None, "D", "E"]
    # 3. No padding needed.
    refined = refine_pages(logical_pages, exclude_indices=[0, 2], blank_pos=[1])
    assert refined == ["B", None, "D", "E"]
