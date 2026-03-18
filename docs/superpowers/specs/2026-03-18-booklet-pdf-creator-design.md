# Booklet PDF Creator Design Specification

This document outlines the design for a Python-based CLI tool that transforms a PDF (containing 2-up landscape pages) into a printable booklet format. It includes features for splitting pages, excluding specific pages, and applying adaptive creep compensation (gutter adjustment).

## 1. Overview

The tool will process a PDF where each physical page contains two logical pages side-by-side. It will split these, allow for page exclusion, reorder them for booklet printing (4 pages per sheet, front and back), and apply dynamic gutter adjustments to compensate for paper thickness (creep).

## 2. Requirements

- **Input**: A PDF file with 2-up landscape pages.
- **Output**: A PDF file formatted for booklet printing.
- **Features**:
    - **Environment**: Managed by `uv`.
    - **Library**: `pymupdf` (fitz) for PDF manipulation.
    - **Binding Direction**: Support for both Left-to-Right (LTR) and Right-to-Left (RTL).
    - **Page Splitting**: Vertical split of each input page into two logical pages.
    - **Page Exclusion**: Ability to remove specific logical pages after splitting.
    - **Blank Page Insertion**: User-specified positions to ensure the total page count is a multiple of 4.
    - **Booklet Reordering**: Standard imposition for saddle-stitch binding.
    - **Adaptive Gutter (Creep Compensation)**:
        - Gutter = 0 at the innermost fold (middle pages).
        - Gutter = `max_gutter` at the outermost pages (first and last).
        - Linear interpolation of gutter size for intermediate pages.
        - Scaling of content to maintain aspect ratio within the remaining space.
        - Distribution of remaining space to outer margins.

## 3. Architecture & Components

### 3.1 CLI Interface
- `input`: Path to the input PDF.
- `output`: Path for the output PDF.
- `direction`: `ltr` (default) or `rtl`.
- `exclude`: List of page numbers/ranges to exclude (e.g., "1, 3-5").
- `blank_pos`: Indices where blank pages should be inserted.
- `max_gutter`: Maximum gutter width (in points) for the outermost pages.

### 3.2 Processing Pipeline

1. **Extraction (Splitter)**:
    - Iterate through input pages.
    - Calculate the midpoint.
    - Extract left and right halves as separate `fitz.Page` objects or PDF byte streams.
    - Order them based on `direction`.

2. **Refinement (Excluder & Padder)**:
    - Remove pages specified in `exclude`.
    - Insert blank pages at `blank_pos`.
    - If `total_pages % 4 != 0`, append blank pages to the end until it is.

3. **Imposition (Organizer)**:
    - Reorder the list of logical pages into the sequence required for booklet printing.
    - Sequence for $N$ pages (indices $0$ to $N-1$):
        - Sheet $i$ Front: `(N-1-2i, 2i)`
        - Sheet $i$ Back: `(2i+1, N-2-2i)`

4. **Composition (Booklet Imposer with Creep Compensation)**:
    - For each pair of logical pages on a physical sheet:
        - Calculate the current "distance from center" to determine the `current_gutter`.
        - Define two destination rectangles on a new landscape page (same size as input).
        - Apply `current_gutter` to the "inner" edge of each rectangle.
        - Scale the source logical page content to fit the remaining rectangle while preserving aspect ratio.
        - Distribute unused horizontal space to the "outer" edge.

## 4. Technical Details

### 4.1 Creep Calculation
Let $N$ be the total number of logical pages (multiple of 4).
Let $S = N/4$ be the total number of sheets.
For sheet $i$ (where $i=0$ is the outermost sheet, $i=S-1$ is the innermost):
- `gutter_factor = (S - 1 - i) / (S - 1)` (if $S > 1$, else 0).
- `current_gutter = max_gutter * gutter_factor`.

*Correction based on user requirement: "Innermost = 0, Outermost = max_gutter".*
- Sheet $i$ (0 to $S-1$):
    - Inner sheet ($i = S-1$): `current_gutter = 0`.
    - Outer sheet ($i = 0$): `current_gutter = max_gutter`.
    - `current_gutter(i) = max_gutter * (1 - i / (S - 1))` if $S > 1$.

### 4.2 Page Placement (PyMuPDF)
```python
# Create new page
new_page = doc_out.new_page(width=original_width, height=original_height)

# Calculate rects for left and right side
# For a landscape page of width W, height H:
# Left Half: (0, 0, W/2, H)
# Right Half: (W/2, 0, W, H)

# Apply gutter to the 'inner' side (W/2)
# Apply scaling and centering/outer-alignment for the logical page content
```

## 5. Error Handling
- Invalid PDF format.
- `exclude` range out of bounds.
- File permission issues.

## 6. Testing Strategy
- **Unit Tests**:
    - Creep calculation logic.
    - Page reordering logic for various page counts (4, 8, 12).
    - Page exclusion logic.
- **Integration Tests**:
    - End-to-end processing of a sample 2-up PDF.
    - Verification of output PDF page count and dimensions.
