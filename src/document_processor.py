import PyPDF2
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF file.
    """
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def identify_key_sections(text):
    """
    Identifies and extracts key financial report sections using regex.
    Focuses on 'Risk Factors' and 'Management's Discussion'.
    """
    sections = {}
    
    # Common SEC Filings Patterns
    patterns = {
        "Risk Factors": r"(Item\s*1A\.?\s*Risk\s*Factors.*?)(?=Item\s*1B|$)",
        "Management Discussion": r"(Item\s*7\.?\s*Management.*?Discussion.*?)(?=Item\s*7A|$)"
    }
    
    for section_name, pattern in patterns.items():
        # Using S flag to make . match newlines
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            # Clean up and limit to first ~1000 chars for summary visibility
            content = match.group(1).strip()
            # Remove excessive whitespace
            content = re.sub(r'\s+', ' ', content)
            sections[section_name] = content[:1500] + "..." if len(content) > 1500 else content
            
    return sections

def process_filing(ticker, input_dir="input/filings"):
    """
    Main entry point for Phase 7.
    Searches for a PDF for the given ticker and extracts insights.
    """
    input_path = Path(input_dir)
    # Support both AAPL.pdf and AAPL_10K.pdf
    pdf_files = list(input_path.glob(f"{ticker}*.pdf"))
    
    if not pdf_files:
        return None
        
    print(f"  Analysing filing: {pdf_files[0].name}...")
    text = extract_text_from_pdf(pdf_files[0])
    
    if not text:
        return None
        
    sections = identify_key_sections(text)
    return {
        "filename": pdf_files[0].name,
        "sections": sections
    }
