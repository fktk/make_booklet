# PDF Booklet Creator Optimization Design

## Problem
The current implementation of PDF booklet creation is slow for large files (e.g., 1GB, hundreds of pages) due to:
1. **Inefficient Image Processing:** Images are processed sequentially after the entire booklet is assembled in memory.
2. **Aggressive Garbage Collection:** The output file is saved with `garbage=3` (deduplication), which is extremely slow for large documents.
3. **Sequential Execution:** Image resizing is CPU-bound but runs in a single thread.

## Proposed Solution

### 1. Parallel Image Processing
Refactor `downsample_images` to use parallel processing for image resizing.

**Strategy:**
1. **Scan Phase:** Iterate through all pages in the document *once* to identify unique images (by XREF) and calculate their required target dimensions based on usage (max rect size).
2. **Process Phase:** Use a `ThreadPoolExecutor` to resize images in parallel.
   - Process images in chunks to manage memory usage.
   - Extract image data (bytes) in the main thread.
   - Resize images in worker threads using `fitz.Pixmap`.
   - Replace images in the document sequentially in the main thread after processing.
3. **Memory Management:** Use a generator or chunked processing to avoid loading all image data into memory at once.

### 2. Optimized Save
Optimize the `doc.save()` parameters for better performance.

**Changes:**
- Change `garbage` level from `3` (deduplicate objects) to `1` (remove unused objects).
- Keep `deflate=True` to maintain reasonable file sizes, as uncompressed 1GB inputs would result in massive outputs.

### 3. Implementation Details

**New Dependencies:**
- `concurrent.futures` (Standard Library)
- `tqdm` (Optional: for progress bars, if desired later, but user didn't select it. We will implement basic logging/print if needed, or keep it silent as per CLI standards).

**Function Signature Changes:**
- `downsample_images(doc, target_dpi)` will be updated to use the new parallel strategy.
- `create_booklet` will be updated to use the optimized `save` parameters.

## Verification Plan
1. **Unit Tests:** Verify that `downsample_images` correctly resizes images and respects `target_dpi`.
2. **Integration Test:** Verify that `create_booklet` produces a valid PDF with downsampled images.
3. **Performance Test:** Measure execution time on a large sample file (if available) or a synthesized large PDF to confirm speedup.
