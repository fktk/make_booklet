import pytest
import fitz
import os
from make_booklet.pdf_processor import convert_to_a4

def test_convert_to_a4(tmp_path):
    """Test converting a non-A4 PDF to A4 size."""
    # 1. Create non-A4 PDF (e.g. 500x500)
    pdf_path = tmp_path / "non_a4.pdf"
    output_path = tmp_path / "a4.pdf"
    
    doc = fitz.open()
    doc.new_page(width=500, height=500)
    doc.save(str(pdf_path))
    doc.close()
    
    # 2. Call convert_to_a4
    convert_to_a4(str(pdf_path), str(output_path))
    
    # 3. Verify
    assert os.path.exists(output_path)
    doc_out = fitz.open(str(output_path))
    assert len(doc_out) == 1
    page = doc_out[0]
    
    # A4 size is approx 595.28 x 841.89 (points)
    # Allow some tolerance for rounding
    assert abs(page.rect.width - 595.28) < 1
    assert abs(page.rect.height - 841.89) < 1
    
    doc_out.close()
