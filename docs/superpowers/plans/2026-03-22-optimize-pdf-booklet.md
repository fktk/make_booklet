# Optimize PDF Booklet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize `make-booklet` performance for large files by implementing parallel image downsampling and tuning PDF save parameters.

**Architecture:** 
-   **Parallel Downsampling:** Offload CPU-intensive image resizing to a thread pool. The main thread scans for unique images and manages document updates, while worker threads resize raw image data.
-   **Save Optimization:** Reduce garbage collection overhead during file saving.

**Tech Stack:** Python, PyMuPDF (fitz), `concurrent.futures`

---

### Task 1: Create Parallel Downsampling Test Structure

**Files:**
- Create: `tests/test_parallel_downsample.py`
- Modify: `src/make_booklet/pdf_processor.py` (stub for new function)

**Steps:**

- [ ] **Step 1: Create test file with a failing test**
  - Create `tests/test_parallel_downsample.py`.
  - Add a test `test_parallel_downsample_images` that:
    - Creates a dummy PDF with a large image.
    - Calls `parallel_downsample_images` (which doesn't exist yet).
    - Verifies the image size is reduced in the output.

```python
import fitz
import pytest
from make_booklet.pdf_processor import parallel_downsample_images

def test_parallel_downsample_images(tmp_path):
    # Create a dummy PDF with an image
    doc = fitz.open()
    page = doc.new_page()
    
    # Create a simple red image (1000x1000)
    pix = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 1000, 1000), False)
    pix.clear_with(255, 0, 0)
    
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
```

- [ ] **Step 2: Add stub function to `pdf_processor.py`**
  - Add `def parallel_downsample_images(doc: fitz.Document, target_dpi: int = 150): pass` to `src/make_booklet/pdf_processor.py`.

- [ ] **Step 3: Run test to confirm failure (assertion error)**
  - `uv run pytest tests/test_parallel_downsample.py`

---

### Task 2: Implement Image Scanning Logic

**Files:**
- Modify: `src/make_booklet/pdf_processor.py`

**Steps:**

- [ ] **Step 1: Implement `scan_images_for_downsampling`**
  - Create a helper function `_scan_images(doc, target_dpi)` that returns a dictionary: `{xref: (width, height)}` of images that *need* resizing.
  - Logic:
    - Iterate all pages.
    - For each image, calculate effective DPI based on usage (max rect).
    - If effective DPI > target_dpi, calculate new dimensions.
    - Store result if it's the first time seeing the XREF or if this usage requires a *higher* resolution than previously thought? 
      - Wait, if an image is used twice, once at 100 DPI and once at 300 DPI, and target is 150 DPI.
      - Usage 1: 100 DPI < 150. No downsample needed? But if we downsample for usage 2...
      - Actually, we only downsample if the *source* is too large for *all* usages.
      - So we need the *maximum* effective DPI required by any usage.
      - If Max Effective DPI > Target DPI, then we downsample to Target DPI.
      - Wait, current implementation: `eff_dpi = max(eff_dpi_w, eff_dpi_h)` per usage.
      - We need to find the `max(eff_dpi)` across *all* usages of an XREF.
      - If *that* max effective DPI > target_dpi, we resize.
      - New dimensions should be calculated based on that max usage.
  
  - Revised Logic for `_scan_images`:
    - `xref_usages = {}`  # xref -> max_eff_dpi
    - Iterate all pages/images.
    - Calculate `eff_dpi` for each usage.
    - Update `xref_usages[xref] = max(xref_usages.get(xref, 0), eff_dpi)`
    - Return list of `(xref, target_width, target_height)` for those where `xref_usages[xref] > target_dpi`.

- [ ] **Step 2: Add unit test for scanner**
  - In `tests/test_parallel_downsample.py`, test the internal logic (or test it via the main function if private).

---

### Task 3: Implement Parallel Resizing and Orchestration

**Files:**
- Modify: `src/make_booklet/pdf_processor.py`

**Steps:**

- [ ] **Step 1: Implement `_resize_image_task`**
  - A standalone function (not method) to be picklable/usable by executor.
  - `def _resize_image_task(img_data: bytes, width: int, height: int) -> bytes:`
  - Use `fitz.Pixmap(img_data)` -> `fitz.Pixmap(pix, width, height)` -> `pix.tobytes()`.

- [ ] **Step 2: Implement `parallel_downsample_images`**
  - Use `_scan_images` to get tasks.
  - Use `concurrent.futures.ThreadPoolExecutor` to run `_resize_image_task`.
  - Iterate through results and `doc.update_stream(xref, new_data)`.
  - Note: `update_stream` is better than `replace_image` for just changing content if we keep the same type.
  - Actually, `replace_image` is high level. `update_stream` replaces raw data. We might need to handle compression/filters. `fitz` handles this if we use `doc.update_stream(xref, new_data)`.

- [ ] **Step 3: Run existing test**
  - `uv run pytest tests/test_parallel_downsample.py`
  - Ensure it passes.

---

### Task 4: Integrate and Optimize Save

**Files:**
- Modify: `src/make_booklet/pdf_processor.py` (`create_booklet`)
- Modify: `src/make_booklet/cli.py` (if necessary, but default change is enough)

**Steps:**

- [ ] **Step 1: Replace `downsample_images` call**
  - In `create_booklet`, replace `downsample_images(doc_out, dpi)` with `parallel_downsample_images(doc_out, dpi)`.

- [ ] **Step 2: Optimize Save**
  - Change `doc_out.save(output_path, garbage=3, deflate=True)` to `doc_out.save(output_path, garbage=1, deflate=True)`.

- [ ] **Step 3: Remove old `downsample_images`**
  - Delete the old function if no longer used.

- [ ] **Step 4: Verify Integration**
  - Run all tests: `uv run pytest`

---

### Task 5: Performance Verification (Optional but Recommended)

**Files:**
- Create: `scripts/benchmark.py` (optional)

**Steps:**
- [ ] **Step 1: Run manual check**
  - Use the existing `pao2_300.pdf` if available (180MB) or a generated one.
  - Measure time with `time make-booklet ...`.
  - (This is a manual verification step for the engineer).

