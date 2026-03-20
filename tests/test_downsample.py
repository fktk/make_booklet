import fitz
import pytest
import os
from make_booklet.pdf_processor import downsample_images

@pytest.fixture
def high_res_pdf(tmp_path):
    """
    Creates a PDF with a high-resolution image.
    Page size: 100x100 pts.
    Image size: 1000x1000 pixels.
    Effective DPI: (1000 / 100) * 72 = 720 DPI.
    """
    pdf_path = str(tmp_path / "high_res.pdf")
    doc = fitz.open()
    page = doc.new_page(width=100, height=100)
    
    # Create a 1000x1000 RGB image (red)
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 1000, 1000))
    pix.clear_with(255) # Red in RGB if we use first channel? 
    # Actually, clear_with(value) clears all channels with the same value.
    # To get a specific color, we can use pix.set_rect() or just fill it.
    # Or just use 0 (black) for simplicity.
    pix.clear_with(0) 
    img_data = pix.tobytes("png")
    
    # Insert image into the full page
    page.insert_image(page.rect, stream=img_data)
    doc.save(pdf_path)
    doc.close()
    return pdf_path

def test_downsample_images(high_res_pdf):
    """
    Test that downsample_images reduces the resolution of a high-DPI image.
    Target DPI: 72.
    Expected width/height should be around 100 pixels (100pt @ 72DPI).
    """
    doc = fitz.open(high_res_pdf)
    
    # Before downsampling, verify image size
    page = doc[0]
    img_list = page.get_images()
    assert len(img_list) == 1
    xref = img_list[0][0]
    img = doc.extract_image(xref)
    assert img["width"] == 1000
    assert img["height"] == 1000
    
    # Apply downsampling
    downsample_images(doc, target_dpi=72)
    
    # After downsampling, verify image size
    img_list_after = page.get_images()
    # page.replace_image might keep old xref and add new one depending on version/doc state
    assert len(img_list_after) >= 1
    
    downsampled_found = False
    for img_info in img_list_after:
        xref_after = img_info[0]
        img_after = doc.extract_image(xref_after)
        if 70 <= img_after["width"] <= 150:
            downsampled_found = True
            break
            
    assert downsampled_found, "No downsampled image found on page"
    
    doc.close()
