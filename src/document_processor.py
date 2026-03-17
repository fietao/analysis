# document_processor.py
import requests
import pandas as pd
from pathlib import Path
from src.config import SEC_EDGAR_BASE_URL

def get_cik_from_ticker(ticker):
    """
    Fetches CIK (Central Index Key) for a ticker from SEC API.
    CIK is needed to access company filings.
    """
    try:
        # SEC provides a JSON mapping of tickers to CIKs
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for entry in data.values():
                if entry.get('ticker', '').upper() == ticker.upper():
                    cik = str(entry['cik_str']).zfill(10)  # Pad with zeros to 10 digits
                    return cik
    except Exception as e:
        print(f"Error fetching CIK for {ticker}: {e}")
    
    return None

def get_sec_filings(ticker):
    """
    Fetches company filings from SEC EDGAR API using CIK.
    Returns structured filing data.
    """
    cik = get_cik_from_ticker(ticker)
    if not cik:
        print(f"Could not find CIK for {ticker}")
        return None
    
    try:
        # Get company submission filings
        url = f"{SEC_EDGAR_BASE_URL}/CIK{cik}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Extract latest 10-K filing metadata
        filings = data.get('filings', {}).get('recent', {})
        
        # Find most recent 10-K
        for form, dates, accessions, urls in zip(
            filings.get('form', []),
            filings.get('filingDate', []),
            filings.get('accessionNumber', []),
            filings.get('primaryDocument', [])
        ):
            if form in ['10-K', '10-Q']:
                # Return filing metadata
                return {
                    'ticker': ticker,
                    'form_type': form,
                    'filing_date': dates,
                    'accession_number': accessions,
                    'document': urls,
                    'cik': cik
                }
        
        return None
        
    except Exception as e:
        print(f"Error fetching SEC filings for {ticker}: {e}")
        return None

def extract_filing_facts(ticker):
    """
    Extracts key facts from SEC EDGAR filings using XBRL data.
    Returns risk factors and management discussion insights.
    """
    cik = get_cik_from_ticker(ticker)
    if not cik:
        return None
    
    try:
        # Get company facts (XBRL data)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Extract key financial and narrative data
        facts = {
            'ticker': ticker,
            'company_name': data.get('entityName'),
            'risk_factors': [],
            'management_discussion': []
        }
        
        # Parse XBRL facts for key metrics
        entity_data = data.get('facts', {})
        
        # These are structured XBRL tags for risk and MD&A
        if 'us-gaap' in entity_data:
            us_gaap = entity_data['us-gaap']
            
            # Try to extract relevant sections
            for key, value in us_gaap.items():
                if 'Risk' in key or 'risk' in key:
                    facts['risk_factors'].append(f"{key}: Available in 10-K filing")
                if 'Management' in key or 'management' in key:
                    facts['management_discussion'].append(f"{key}: Available in 10-K filing")
        
        return facts
        
    except Exception as e:
        print(f"Error extracting filing facts for {ticker}: {e}")
        return None

def process_filing(ticker, input_dir="input/filings"):
    """
    Main entry point for SEC filing analysis.
    Uses SEC EDGAR API instead of PDF parsing.
    Supports local PDF uploads as fallback.
    """
    
    # First try SEC EDGAR API
    sec_data = get_sec_filings(ticker)
    if sec_data:
        return {
            "filename": f"SEC EDGAR - {sec_data['form_type']} ({sec_data['filing_date']})",
            "sections": {
                "Filing Type": sec_data['form_type'],
                "Date": sec_data['filing_date'],
                "Status": "✅ Retrieved from SEC EDGAR API",
                "Document": sec_data.get('document', 'N/A')
            }
        }
    
    # Fallback to local PDF uploads if available
    input_path = Path(input_dir)
    pdf_files = list(input_path.glob(f"{ticker}*.pdf"))
    
    if pdf_files:
        print(f"  Processing local filing: {pdf_files[0].name}...")
        return {
            "filename": pdf_files[0].name,
            "sections": {
                "Status": "Local PDF uploaded",
                "Notes": "Consider using SEC EDGAR API for automated extraction"
            }
        }
    
    return None
