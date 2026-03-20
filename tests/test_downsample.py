import fitz
import pytest
from make_booklet.pdf_processor import downsample_images, create_booklet

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
    
    # Create a 1000x1000 RGB image (black)
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 1000, 1000))
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

def test_create_booklet_with_dpi(high_res_pdf, tmp_path):
    """
    Test that create_booklet correctly calls downsample_images and produces a smaller PDF.
    """
    output_path = str(tmp_path / "booklet_downsampled.pdf")
    doc_in = fitz.open(high_res_pdf)
    
    # Mock logical_pages for a 4-page booklet (all using the same high-res page)
    # create_booklet expects [(page_num, source_rect), ...]
    logical_pages = [(0, doc_in[0].rect)] * 4
    
    # Call create_booklet with target DPI
    create_booklet(doc_in, logical_pages, output_path, dpi=72.0)
    doc_in.close()
    
    # Verify the output PDF
    doc_out = fitz.open(output_path)
    assert len(doc_out) == 2  # 4 logical pages = 2 physical sheets (front/back)
    
    # Check if images in the output are downsampled
    downsampled_found = False
    for page in doc_out:
        img_list = page.get_images()
        for img_info in img_list:
            xref = img_info[0]
            img = doc_out.extract_image(xref)
            # Original image was 1000x1000 on 100x100 page.
            # In booklet, it's placed on a 50x100 (half) page.
            # Target DPI 72 on a 50pt width should be around 50 pixels.
            if 40 <= img["width"] <= 150:
                downsampled_found = True
                break
        if downsampled_found:
            break
            
    assert downsampled_found, "No downsampled image found in the booklet output"
    doc_out.close()
