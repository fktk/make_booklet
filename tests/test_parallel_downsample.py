import fitz
import pytest
from make_booklet.pdf_processor import parallel_downsample_images, _scan_images

def test_scan_images(tmp_path):
    # Create a dummy PDF with an image
    doc = fitz.open()
    page = doc.new_page()
    
    # Create a simple red image (1000x1000)
    pix = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 1000, 1000), False)
    pix.clear_with(0)
    
    # Insert 1: displayed as 100x100 points -> (1000/100)*72 = 720 DPI
    page.insert_image(fitz.Rect(0, 0, 100, 100), pixmap=pix)
    
    # Insert 2 on another page: displayed as 200x200 points -> (1000/200)*72 = 360 DPI
    page2 = doc.new_page()
    page2.insert_image(fitz.Rect(0, 0, 200, 200), pixmap=pix)
    
    # Save and reload to ensure full PDF structure
    input_path = tmp_path / "test_scan.pdf"
    doc.save(input_path)
    doc.close()
    
    doc = fitz.open(input_path)
    # Target 150 DPI. Max DPI is 720.
    # Scale = 150 / 720 = 0.208333...
    # target_w = int(1000 * 0.208333...) = 208
    results = _scan_images(doc, 150)
    
    assert len(results) == 1
    xref, target_w, target_h = results[0]
    assert target_w == 208
    assert target_h == 208
    doc.close()

def test_scan_images_multiple(tmp_path):
    # Create a dummy PDF with multiple images
    doc = fitz.open()
    page = doc.new_page()
    
    # Image 1 (1000x1000), insert as 100x100 points -> (1000/100)*72 = 720 DPI
    pix1 = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 1000, 1000), False)
    pix1.clear_with(0)
    page.insert_image(fitz.Rect(0, 0, 100, 100), pixmap=pix1)
    
    # Image 2 (200x200), insert as 100x100 points -> (200/100)*72 = 144 DPI
    pix2 = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 200, 200), False)
    pix2.clear_with(0)
    page.insert_image(fitz.Rect(110, 0, 210, 100), pixmap=pix2)
    
    # Save and reload to ensure full PDF structure
    input_path = tmp_path / "test_scan_multiple.pdf"
    doc.save(input_path)
    doc.close()
    
    doc = fitz.open(input_path)
    # Target 150 DPI. Only Image 1 should be returned.
    results = _scan_images(doc, 150)
    
    assert len(results) == 1
    xref, target_w, target_h = results[0]
    
    # Verify it's Image 1
    base_image = doc.extract_image(xref)
    assert base_image["width"] == 1000
    doc.close()

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
