# Booklet PDF Creator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a CLI tool to split 2-up landscape PDFs, exclude pages, reorder for booklet printing, and apply adaptive creep compensation.

**Architecture:** A Python CLI tool using `pymupdf` (fitz). Processing is divided into splitting, refining (exclude/pad), reordering, and final composition with creep adjustment.

**Tech Stack:** Python 3.12+, `uv`, `pymupdf`, `pytest`.

---

### Task 1: Project Setup and Environment

**Files:**
- Create: `pyproject.toml`
- Create: `README.md` (Update)

- [ ] **Step 1: Initialize uv project**

Run: `uv init`
Expected: `pyproject.toml` and `hello.py` created.

- [ ] **Step 2: Add dependencies**

Run: `uv add pymupdf pytest`
Expected: Dependencies added to `pyproject.toml`.

- [ ] **Step 3: Setup project structure**

Run: `mkdir -p src/make_booklet tests`
Expected: Directories created.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml README.md
git commit -m "chore: initial project setup with uv and pymupdf"
```

---

### Task 2: Core Logic - Page Reordering for Booklet

**Files:**
- Create: `src/make_booklet/reorder.py`
- Test: `tests/test_reorder.py`

- [ ] **Step 1: Write failing test for reordering**

```python
from make_booklet.reorder import get_booklet_sequence

def test_get_booklet_sequence_4():
    # 4 pages -> 1 sheet (front: 3,0; back: 1,2)
    assert get_booklet_sequence(4) == [3, 0, 1, 2]

def test_get_booklet_sequence_8():
    # 8 pages -> 2 sheets
    # Sheet 0 front: 7,0; back: 1,6
    # Sheet 1 front: 5,2; back: 3,4
    assert get_booklet_sequence(8) == [7, 0, 1, 6, 5, 2, 3, 4]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_reorder.py`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement reordering logic**

```python
def get_booklet_sequence(n):
    if n % 4 != 0:
        raise ValueError("Page count must be a multiple of 4")
    sequence = []
    num_sheets = n // 4
    for i in range(num_sheets):
        # Front
        sequence.append(n - 1 - 2 * i)
        sequence.append(2 * i)
        # Back
        sequence.append(2 * i + 1)
        sequence.append(n - 2 - 2 * i)
    return sequence
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_reorder.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/make_booklet/reorder.py tests/test_reorder.py
git commit -m "feat: implement booklet page reordering logic"
```

---

### Task 3: Core Logic - Creep (Gutter) Calculation

**Files:**
- Create: `src/make_booklet/creep.py`
- Test: `tests/test_creep.py`

- [ ] **Step 1: Write failing test for creep calculation**

```python
from make_booklet.creep import calculate_gutter

def test_calculate_gutter():
    # 8 pages -> 2 sheets (i=0, i=1)
    # i=0 (outer): max_gutter
    # i=1 (inner): 0
    assert calculate_gutter(sheet_index=0, total_sheets=2, max_gutter=10) == 10
    assert calculate_gutter(sheet_index=1, total_sheets=2, max_gutter=10) == 0

def test_calculate_gutter_single_sheet():
    assert calculate_gutter(0, 1, 10) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_creep.py`
Expected: FAIL

- [ ] **Step 3: Implement creep calculation**

```python
def calculate_gutter(sheet_index, total_sheets, max_gutter):
    if total_sheets <= 1:
        return 0.0
    return max_gutter * (1 - sheet_index / (total_sheets - 1))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_creep.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/make_booklet/creep.py tests/test_creep.py
git commit -m "feat: implement adaptive creep (gutter) calculation"
```

---

### Task 4: PDF Splitting and Extraction

**Files:**
- Create: `src/make_booklet/pdf_processor.py`

- [ ] **Step 1: Implement splitting and extraction**

```python
import fitz

def split_pdf_pages(input_path, direction='ltr'):
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
        
        # Create a new temporary PDF to hold split pages to avoid cropbox issues
        # Actually, PyMuPDF can use show_pdf_page with source rect
        # We will store (page_index, source_rect)
        if direction == 'ltr':
            logical_pages.append((page.number, left_rect))
            logical_pages.append((page.number, right_rect))
        else: # rtl
            logical_pages.append((page.number, right_rect))
            logical_pages.append((page.number, left_rect))
            
    return doc, logical_pages
```

- [ ] **Step 2: Test with a small dummy PDF (manual verification or automated if possible)**

---

### Task 5: Page Exclusion and Padding

**Files:**
- Modify: `src/make_booklet/pdf_processor.py`

- [ ] **Step 1: Add exclusion and padding logic**

```python
def refine_pages(logical_pages, exclude_indices=None, blank_pos=None):
    # exclude_indices: list of 0-based indices
    if exclude_indices:
        logical_pages = [p for i, p in enumerate(logical_pages) if i not in exclude_indices]
    
    # Insert blanks (None represents a blank page)
    if blank_pos:
        for pos in sorted(blank_pos, reverse=True):
            logical_pages.insert(pos, None)
            
    # Pad to multiple of 4
    while len(logical_pages) % 4 != 0:
        logical_pages.append(None)
        
    return logical_pages
```

---

### Task 6: Final Composition (Booklet Imposition)

**Files:**
- Modify: `src/make_booklet/pdf_processor.py`

- [ ] **Step 1: Implement create_booklet function**

```python
def create_booklet(doc_in, logical_pages, output_path, max_gutter=0):
    doc_out = fitz.open()
    num_pages = len(logical_pages)
    sequence = get_booklet_sequence(num_pages)
    
    total_sheets = num_pages // 4
    
    # Get original page size (assume all same)
    ref_page = doc_in[0]
    orig_w, orig_h = ref_page.rect.width, ref_page.rect.height
    
    for i in range(total_sheets * 2): # 2 physical pages per sheet (front and back)
        sheet_idx = i // 2
        is_front = (i % 2 == 0)
        
        new_page = doc_out.new_page(width=orig_w, height=orig_h)
        
        gutter = calculate_gutter(sheet_idx, total_sheets, max_gutter)
        
        # Sequence for this physical page
        page_indices = sequence[i*2 : i*2+2]
        
        for side_idx, log_idx in enumerate(page_indices):
            if log_idx >= len(logical_pages) or logical_pages[log_idx] is None:
                continue
                
            src_page_num, src_rect = logical_pages[log_idx]
            
            # Destination rect for this side (left or right half)
            dest_half_w = orig_w / 2
            if side_idx == 0: # Left side of physical sheet
                dest_rect = fitz.Rect(0, 0, dest_half_w, orig_h)
                # Apply gutter to the right side of this rect (the fold)
                inner_gutter_rect = fitz.Rect(0, 0, dest_half_w - gutter, orig_h)
            else: # Right side of physical sheet
                dest_rect = fitz.Rect(dest_half_w, 0, orig_w, orig_h)
                # Apply gutter to the left side of this rect (the fold)
                inner_gutter_rect = fitz.Rect(dest_half_w + gutter, 0, orig_w, orig_h)

            # Draw page content into inner_gutter_rect with scaling
            new_page.show_pdf_page(inner_gutter_rect, doc_in, src_page_num, clip=src_rect)
            
    doc_out.save(output_path)
    doc_out.close()
```

---

### Task 7: CLI Interface

**Files:**
- Create: `src/make_booklet/cli.py`

- [ ] **Step 1: Implement CLI using argparse**

```python
import argparse
import sys
from make_booklet.pdf_processor import split_pdf_pages, refine_pages, create_booklet

def parse_range(s):
    # Helper to parse "1,3-5" into [0, 2, 3, 4]
    indices = []
    for part in s.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices.extend(range(start-1, end))
        else:
            indices.append(int(part)-1)
    return indices

def main():
    parser = argparse.ArgumentParser(description="PDF Booklet Creator")
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument("--direction", choices=['ltr', 'rtl'], default='ltr')
    parser.add_argument("--exclude", help="Pages to exclude (e.g. 1,3-5)")
    parser.add_argument("--blank-pos", help="Positions to insert blanks (e.g. 2,4)")
    parser.add_argument("--max-gutter", type=float, default=0.0, help="Max gutter for outermost pages")
    
    args = parser.parse_args()
    
    # ... call processor functions ...
```

---

### Task 8: Integration and Verification

- [ ] **Step 1: Run end-to-end test with a sample file**
- [ ] **Step 2: Verify creep adjustment visually or via metadata if possible**
- [ ] **Step 3: Add documentation on usage in README.md**
