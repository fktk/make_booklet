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
    
    # 2. Call convert_to_a4 (default auto, center)
    convert_to_a4(str(pdf_path), str(output_path))
    
    # 3. Verify
    assert os.path.exists(output_path)
    doc_out = fitz.open(str(output_path))
    assert len(doc_out) == 1
    page = doc_out[0]
    
    # A4 size is approx 595.28 x 841.89 (points)
    # 500x500 fits in 595.28x595.28 (scaled by 595.28/500 = 1.19056)
    # Rect should be Portrait.
    assert abs(page.rect.width - 595.28) < 1
    assert abs(page.rect.height - 841.89) < 1
    
    doc_out.close()

def test_convert_to_a4_orientation_landscape(tmp_path):
    """Test forcing landscape orientation."""
    pdf_path = tmp_path / "portrait.pdf"
    output_path = tmp_path / "a4_landscape.pdf"
    
    doc = fitz.open()
    doc.new_page(width=500, height=800)
    doc.save(str(pdf_path))
    doc.close()
    
    # Forced landscape
    convert_to_a4(str(pdf_path), str(output_path), orientation='landscape')
    
    doc_out = fitz.open(str(output_path))
    page = doc_out[0]
    assert abs(page.rect.width - 841.89) < 1
    assert abs(page.rect.height - 595.28) < 1
    doc_out.close()

def test_convert_to_a4_auto_orientation(tmp_path):
    """Test auto orientation selection."""
    pdf_path = tmp_path / "mixed.pdf"
    output_path = tmp_path / "a4_mixed.pdf"
    
    doc = fitz.open()
    doc.new_page(width=800, height=500) # Landscape input
    doc.new_page(width=500, height=800) # Portrait input
    doc.save(str(pdf_path))
    doc.close()
    
    convert_to_a4(str(pdf_path), str(output_path), orientation='auto')
    
    doc_out = fitz.open(str(output_path))
    assert len(doc_out) == 2
    
    # Page 1 should be A4 landscape
    assert abs(doc_out[0].rect.width - 841.89) < 1
    assert abs(doc_out[0].rect.height - 595.28) < 1
    
    # Page 2 should be A4 portrait
    assert abs(doc_out[1].rect.width - 595.28) < 1
    assert abs(doc_out[1].rect.height - 841.89) < 1
    
    doc_out.close()

def test_convert_to_a4_align(tmp_path):
    """
    Test alignment options. 
    Verifying alignment in output PDF is hard, 
    but we can at least check that it doesn't crash.
    """
    pdf_path = tmp_path / "square.pdf"
    
    doc = fitz.open()
    doc.new_page(width=500, height=500)
    doc.save(str(pdf_path))
    doc.close()
    
    for align in ['center', 'left', 'right', 'top', 'bottom']:
        output_path = tmp_path / f"a4_{align}.pdf"
        convert_to_a4(str(pdf_path), str(output_path), align=align)
        assert os.path.exists(output_path)
        # We could potentially check the display list or Form XObject matrix 
        # to verify placement, but that's complex.
