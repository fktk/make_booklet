import fitz
import pytest
from make_booklet.pdf_processor import parallel_downsample_images

def test_parallel_downsample_images(tmp_path):
    # Create a dummy PDF with an image
    doc = fitz.open()
    page = doc.new_page()
    
    # Create a simple red image (1000x1000)
    pix = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 1000, 1000), False)
    pix.clear_with(0)
    
    # Insert into page (displayed as 100x100 points -> 720 DPI)
    page.insert_image(fitz.Rect(0, 0, 100, 100), pixmap=pix)
    
    # Save to temp file to ensure it's a real PDF structure
    input_path = tmp_path / "test_input.pdf"
    doc.save(input_path)
    doc.close()
    
    # Open and process
    doc_to_process = fitz.open(input_path)
    # Target 72 DPI (should downsample 10x)
    parallel_downsample_images(doc_to_process, target_dpi=72)
    
    # Verify
    img_list = doc_to_process.get_page_images(0)
    xref = img_list[0][0]
    processed_pix = fitz.Pixmap(doc_to_process, xref)
    
    # Should be close to 100x100 pixels
    assert 90 <= processed_pix.width <= 110
    assert 90 <= processed_pix.height <= 110
    doc_to_process.close()
