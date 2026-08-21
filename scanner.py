import requests
import PyPDF2
import io
from bs4 import BeautifulSoup
import urllib.parse
import time

search_terms = [
    "White", 
    "Irish Traveller", 
    "Mixed ethnic",
    "Multiple ethnic groups",
    "Asian", 
    "Asian British", 
    "Indian", 
    "Pakistani", 
    "Bangladeshi",
    "Chinese", 
    "Any other Asian background",
    "Black",
    "African",
    "Caribbean",
    "Black British",
    "Arab",
    "Any other ethnic group"
]

def get_guideline_urls(base_url):
    print(f"Fetching guidelines from {base_url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pdf_links = []
        # Find all links that end in .pdf on the SIGN guidelines page
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf'):
                full_url = urllib.parse.urljoin(base_url, href)
                if full_url not in pdf_links:
                    pdf_links.append(full_url)
        
        print(f"Found {len(pdf_links)} PDF guidelines to scan.")
        return pdf_links
    except Exception as e:
        print(f"Failed to fetch URLs: {e}")
        return []

def scan_pdf_for_terms(pdf_url):
    print(f"\nScanning: {pdf_url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        found_terms = {term: [] for term in search_terms}
        
        for page_num in range(len(reader.pages)):
            page_text = reader.pages[page_num].extract_text()
            if page_text:
                for term in search_terms:
                    if term.lower() in page_text.lower():
                        found_terms[term].append(page_num + 1)
                        
        found_any = False
        for term, pages in found_terms.items():
            if pages:
                print(f" Found '{term}' on pages: {pages}")
                found_any = True
                
        if not found_any:
            print(" No ethnic group terms found in this guideline.")
                
    except Exception as e:
        print(f" Failed to scan {pdf_url}: {e}")

def main():
    # The official SIGN guidelines page URL
    guidelines_page_url = "https://www.sign.ac.uk/guidelines/"
    pdf_urls = get_guideline_urls(guidelines_page_url)
    
    # Process each PDF found
    for url in pdf_urls:
        scan_pdf_for_terms(url)
        time.sleep(1) # Add a delay to be polite to the server

if __name__ == "__main__":
    main()
