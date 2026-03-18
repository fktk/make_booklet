# PDF Booklet Creator

A command-line tool to transform 2-up landscape PDFs into printable booklet format with adaptive creep compensation.

## Features

- **Split 2-up Pages**: Automatically splits each landscape page into two logical pages.
- **LTR/RTL Support**: Supports both Left-to-Right and Right-to-Left binding directions.
- **Page Exclusion**: Remove specific pages before booklet creation.
- **Blank Page Insertion**: Add blanks at specified positions to adjust layout.
- **Adaptive Creep Compensation**: Dynamically adjusts the gutter (inner margin) to compensate for paper thickness when folded.
- **Automatic Padding**: Ensures the total page count is a multiple of 4.

## Installation

Ensure you have [uv](https://github.com/astral-sh/uv) installed.

```bash
git clone <repository-url>
cd make_booklet
uv sync
```

## Usage

Run the tool using `uv run`:

```bash
uv run python -m make_booklet.cli input.pdf output.pdf [options]
```

### Options

- `input`: Path to the input PDF file (2-up landscape).
- `output`: Path for the output booklet PDF.
- `--direction {ltr,rtl}`: Binding direction. Default is `ltr`.
- `--exclude "1,3-5"`: Specify logical page numbers to exclude (1-based).
- `--blank-pos "2,4"`: Specify positions to insert blank pages.
- `--max-gutter <float>`: Maximum gutter adjustment (in points) for the outermost pages.

### Example

```bash
# Create a right-to-left booklet with 10pt maximum creep compensation
uv run python -m make_booklet.cli manga.pdf booklet.pdf --direction rtl --max-gutter 10.0
```

## Development

Run tests with `pytest`:

```bash
uv run pytest
```

## License

MIT
