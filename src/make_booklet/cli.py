"""
CLI interface for the PDF Booklet Creator.
"""
import argparse
import sys
from make_booklet.pdf_processor import split_pdf_pages, refine_pages, create_booklet

def parse_range(s):
    """
    Parse a range string like "1,3-5" into a list of 0-based indices.
    """
    if not s:
        return []
    indices = []
    for part in s.split(','):
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                indices.extend(range(start-1, end))
            except ValueError:
                print(f"Error: Invalid range format '{part}'", file=sys.stderr)
                sys.exit(1)
        else:
            try:
                indices.append(int(part)-1)
            except ValueError:
                print(f"Error: Invalid page number '{part}'", file=sys.stderr)
                sys.exit(1)
    return indices

def main():
    parser = argparse.ArgumentParser(description="Split 2-up PDFs and create booklets.")
    parser.add_argument("input", help="Path to the input PDF file.")
    parser.add_argument("output", help="Path for the output PDF file.")
    parser.add_argument("--direction", choices=['ltr', 'rtl'], default='ltr',
                        help="Binding direction: 'ltr' (Left-to-Right) or 'rtl' (Right-to-Left). Default is 'ltr'.")
    parser.add_argument("--exclude", help="Logical pages to exclude (e.g., '1,3-5').")
    parser.add_argument("--blank-pos", help="Positions to insert blanks (e.g., '2,4').")
    parser.add_argument("--max-gutter", type=float, default=0.0,
                        help="Maximum gutter width (in points) for the outermost pages.")
    parser.add_argument("--dpi", type=float, help="Target DPI for image downsampling (e.g., 150). Images exceeding this resolution will be downsampled.")
    
    args = parser.parse_args()
    
    # 1. Split
    try:
        doc_in, logical_pages = split_pdf_pages(args.input, direction=args.direction)
    except Exception as e:
        print(f"Error: Failed to open or split input PDF: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 2. Refine
    exclude_indices = parse_range(args.exclude)
    blank_pos = parse_range(args.blank_pos)
    refined_pages = refine_pages(logical_pages, exclude_indices=exclude_indices, blank_pos=blank_pos)
    
    # 3. Create Booklet
    try:
        create_booklet(doc_in, refined_pages, args.output, max_gutter=args.max_gutter, direction=args.direction, dpi=args.dpi)
    except Exception as e:
        print(f"Error: Failed to create booklet PDF: {e}", file=sys.stderr)
        doc_in.close()
        sys.exit(1)
        
    doc_in.close()
    print(f"Successfully created booklet: {args.output}")

if __name__ == "__main__":
    main()
