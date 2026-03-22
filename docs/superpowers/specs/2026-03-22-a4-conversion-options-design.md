# A4 Conversion Options Design

## Problem
The current `convert_to_a4` function is hardcoded to A4 portrait orientation and centers the content. Users want more control over the output orientation and margin alignment.

## Proposed Solution

### 1. Orientation Options
Add an `orientation` parameter to `convert_to_a4` and a corresponding CLI argument `--a4-orientation`.

- **auto** (default): Choose portrait or landscape for each page individually based on its aspect ratio.
- **portrait**: All pages will be A4 portrait (595.28 x 841.89 points).
- **landscape**: All pages will be A4 landscape (841.89 x 595.28 points).

### 2. Alignment Options
Add an `align` parameter to `convert_to_a4` and a corresponding CLI argument `--a4-align`.

- **center** (default): Center the content both horizontally and vertically.
- **left**: Align to the left (horizontal margin on the right). Vertical alignment is centered.
- **right**: Align to the right (horizontal margin on the left). Vertical alignment is centered.
- **top**: Align to the top (vertical margin at the bottom). Horizontal alignment is centered.
- **bottom**: Align to the bottom (vertical margin at the top). Horizontal alignment is centered.

### 3. CLI Interface
Update `src/make_booklet/cli.py` to include:

- `--a4-orientation`: Choices are `auto`, `portrait`, `landscape`. Default is `auto`.
- `--a4-align`: Choices are `center`, `left`, `right`, `top`, `bottom`. Default is `center`.

### 4. Implementation Details

#### `convert_to_a4` Refactoring
Update `convert_to_a4` in `src/make_booklet/pdf_processor.py`:

```python
def convert_to_a4(input_path: str, output_path: str, orientation: str = 'auto', align: str = 'center'):
    doc = fitz.open(input_path)
    doc_out = fitz.open()
    
    for page in doc:
        # Determine target size
        if orientation == 'auto':
            if page.rect.width > page.rect.height:
                target_w, target_h = 841.89, 595.28 # Landscape
            else:
                target_w, target_h = 595.28, 841.89 # Portrait
        elif orientation == 'landscape':
            target_w, target_h = 841.89, 595.28
        else: # portrait
            target_w, target_h = 595.28, 841.89
            
        new_page = doc_out.new_page(width=target_w, height=target_h)
        
        # Calculate scaling (fit while preserving aspect ratio)
        scale = min(target_w / page.rect.width, target_h / page.rect.height)
        new_w = page.rect.width * scale
        new_h = page.rect.height * scale
        
        # Calculate alignment
        if align == 'left':
            x = 0
            y = (target_h - new_h) / 2
        elif align == 'right':
            x = target_w - new_w
            y = (target_h - new_h) / 2
        elif align == 'top':
            x = (target_w - new_w) / 2
            y = 0
        elif align == 'bottom':
            x = (target_w - new_w) / 2
            y = target_h - new_h
        else: # center
            x = (target_w - new_w) / 2
            y = (target_h - new_h) / 2
            
        target_rect = fitz.Rect(x, y, x + new_w, y + new_h)
        new_page.show_pdf_page(target_rect, doc, page.number)
    
    doc_out.save(output_path)
    doc_out.close()
    doc.close()
```

## Verification Plan
1. **Unit Tests**:
    - Verify `orientation='auto'` picks the right A4 orientation.
    - Verify `orientation='portrait'` / `'landscape'` forces orientation.
    - Verify `align` options (`left`, `right`, `top`, `bottom`) correctly position the content.
2. **Integration Test**:
    - Run the CLI with various combinations of `--to-a4`, `--a4-orientation`, and `--a4-align`.
    - Check the output PDF dimensions and positioning using `fitz` (PyMuPDF).
