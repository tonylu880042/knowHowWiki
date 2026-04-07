#!/usr/bin/env python3
import sys
import os
import argparse

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF (fitz) is not installed.", file=sys.stderr)
    print("Please install it using: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)

def parse_pdf(file_path, max_pages=None):
    try:
        doc = fitz.open(file_path)
        text = ""
        limit = min(max_pages, len(doc)) if max_pages else len(doc)
        
        for i in range(limit): 
            text += doc[i].get_text()
            
        header = f"=== Extracted from {os.path.basename(file_path)}"
        if max_pages and len(doc) > max_pages:
            header += f" (First {max_pages} pages of {len(doc)} total)"
        header += " ===\n"
        
        return header + text + "\n---\n"
    except Exception as e:
        return f"Error reading {os.path.basename(file_path)}: {e}\n---\n"

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF files using PyMuPDF.")
    parser.add_argument("target", help="Path to PDF file or a directory containing PDF files.")
    parser.add_argument("-o", "--output", help="Output file path. If not provided, prints to stdout.", default=None)
    parser.add_argument("-m", "--max-pages", type=int, help="Maximum number of pages to extract per PDF (default: 20 to prevent overload).", default=20)
    
    args = parser.parse_args()
    target = args.target
    
    all_text = ""
    target_pdfs = []
    
    if os.path.isdir(target):
        for f in os.listdir(target):
            if f.lower().endswith(".pdf"):
                target_pdfs.append(os.path.join(target, f))
        target_pdfs.sort()
    elif os.path.isfile(target):
        if target.lower().endswith(".pdf"):
            target_pdfs.append(target)
        else:
            print("Error: Target file is not a .pdf file.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: Target path '{target}' not found.", file=sys.stderr)
        sys.exit(1)
        
    if not target_pdfs:
        print(f"No PDF files found at '{target}'.", file=sys.stderr)
        sys.exit(0)
        
    for pdf_file in target_pdfs:
        all_text += parse_pdf(pdf_file, max_pages=args.max_pages)
        
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(all_text)
            print(f"Success: Extracted {len(all_text)} characters to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(all_text)

if __name__ == "__main__":
    main()
