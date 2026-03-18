# PDF Booklet Creator

A tool to create booklets from PDF files.

## Installation

Ensure you have [uv](https://github.com/astral-sh/uv) installed.

Clone the repository:
```bash
git clone https://github.com/your-username/make-booklet.git
cd make-booklet
```

Install dependencies:
```bash
uv sync
```

## Usage

Run the tool to create a booklet from a PDF:
```bash
uv run python -m make_booklet <input_pdf_path> <output_pdf_path>
```

## Running Tests

```bash
uv run pytest
```
