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
