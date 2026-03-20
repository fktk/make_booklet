import os
import fitz
import pytest
from unittest.mock import patch
from make_booklet.cli import main

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    width, height = 842, 595
    for i in range(2): # 2 physical pages -> 4 logical
        page = doc.new_page(width=width, height=height)
        page.insert_text((10, 20), f"P{i+1}L", fontsize=12)
        page.insert_text((width/2 + 10, 20), f"P{i+1}R", fontsize=12)
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_full_integration(sample_pdf, tmp_path):
    output_pdf = tmp_path / "final_booklet.pdf"
    
    # Simulate: uv run src/make_booklet/cli.py input.pdf output.pdf --max-gutter 5
    test_args = [
        "make_booklet", 
        sample_pdf, 
        str(output_pdf), 
        "--max-gutter", "5.0",
        "--direction", "ltr"
    ]
    
    with patch("sys.argv", test_args):
        main()
    
    assert os.path.exists(output_pdf)
    doc = fitz.open(str(output_pdf))
    # 4 logical -> 1 sheet -> 2 physical pages
    assert len(doc) == 2
    doc.close()

def test_full_integration_with_exclude(sample_pdf, tmp_path):
    output_pdf = tmp_path / "exclude_booklet.pdf"
    
    # 4 logical pages. Exclude 1. Remaining 3. Pad to 4.
    test_args = [
        "make_booklet",
        sample_pdf,
        str(output_pdf),
        "--exclude", "1"
    ]
    
    with patch("sys.argv", test_args):
        main()
        
    assert os.path.exists(output_pdf)
    doc = fitz.open(str(output_pdf))
    assert len(doc) == 2 # 4 logical -> 2 physical
    doc.close()

def test_full_integration_with_dpi(sample_pdf, tmp_path):
    output_pdf = tmp_path / "dpi_booklet.pdf"
    
    # 4 logical pages.
    test_args = [
        "make_booklet",
        sample_pdf,
        str(output_pdf),
        "--dpi", "150"
    ]
    
    with patch("sys.argv", test_args):
        main()
        
    assert os.path.exists(output_pdf)
    doc = fitz.open(str(output_pdf))
    assert len(doc) == 2 # 4 logical -> 2 physical
    doc.close()
