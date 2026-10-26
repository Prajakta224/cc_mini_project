"""
Script to build report docx, convert to PDF via Word COM, and verify exact page count.
"""
import os
import sys
import win32com.client
import fitz

from build_full_report import create_report, DOCX_NAME, PDF_NAME

print("=== STEP 1: Building DOCX Report ===")
create_report()
docx_path = os.path.abspath(DOCX_NAME)
pdf_path = os.path.abspath(PDF_NAME)

print(f"DOCX created: {docx_path} ({os.path.getsize(docx_path)} bytes)")

print("\n=== STEP 2: Converting DOCX to PDF via MS Word COM ===")
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = False
try:
    doc = word.Documents.Open(docx_path)
    doc.SaveAs(pdf_path, FileFormat=17) # 17 = wdFormatPDF
    doc.Close()
    print(f"PDF created successfully: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
except Exception as e:
    print(f"Error during Word COM conversion: {e}")
    sys.exit(1)
finally:
    word.Quit()

print("\n=== STEP 3: Verifying PDF with PyMuPDF ===")
pdf_doc = fitz.open(pdf_path)
page_count = len(pdf_doc)
print(f"Total Page Count: {page_count} pages")

if 20 <= page_count <= 25:
    print(f"SUCCESS: Page count {page_count} is within the required range (20–25 pages)!")
else:
    print(f"WARNING: Page count {page_count} is OUTSIDE the required range (20–25 pages)!")

print("\n=== Page-by-Page Overview ===")
for p_idx in range(page_count):
    p = pdf_doc[p_idx]
    txt = p.get_text().splitlines()
    first_line = txt[0] if txt else "(empty)"
    # find chapter or section title
    headings = [l.strip() for l in txt if l.strip().startswith("CHAPTER") or l.strip().startswith("ABSTRACT") or l.strip().startswith("TABLE OF CONTENTS") or l.strip().startswith("LIST OF") or l.strip().startswith("CERTIFICATE") or l.strip().startswith("ACKNOWLEDGEMENT") or l.strip().startswith("REFERENCES")]
    h_str = " | ".join(headings) if headings else ""
    print(f"  Page {p_idx + 1:02d}: {first_line[:40]:<40} {h_str}")
