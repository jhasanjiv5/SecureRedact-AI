import io
from pypdf import PdfReader
from fpdf import FPDF
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200, 
    separators=["\n\n", "\n", " ", "", "Chapter", "Section"]
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file stream.
    """
    try:
        # Load the document from bytes (equivalent to arrayBuffer)
        # pypdf can read directly from a BytesIO stream
        pdf_stream = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)
        
        full_text = []
        num_pages = len(reader.pages)

        # Iterate through pages (Python is 0-indexed, unlike PDF definition)
        for i in range(num_pages):
            page = reader.pages[i]
            
            # extract_text() is the equivalent of getting text items and joining them
            # pypdf handles the layout extraction automatically
            page_text = page.extract_text() or ""
            
            # Mimicking the output format of the TS function
            full_text.append(f"--- Page {i + 1} ---\n{page_text}\n\n")

        return "".join(full_text)

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        # Mimicking the fallback error throw
        raise ValueError("Failed to extract text from PDF file. Please try a text or JSON file if this persists.")
    
def create_context(documents):
    """Chunks text and adds metadata headers for context."""
    chunks = []
    for doc in documents:
        doc_chunks = text_splitter.split_text(doc['content'])
        # We attach Document ID and Title to every single chunk so the LLM knows the source
        chunks.extend([
            f"Document ID: {doc['id']}\nTitle: {doc['title']}\nContent: {chunk}\n\n" 
            for chunk in doc_chunks
        ])
    return chunks

def process_pdf_to_context(pdf_bytes: bytes, file_title: str):
    
    raw_text = extract_text_from_pdf(pdf_bytes)
    doc_chunks = text_splitter.split_text(raw_text)
    
    return [
        Document(
            page_content=chunk, 
            metadata={"title": file_title}
        ) for chunk in doc_chunks
    ]

def generate_redacted_pdf(content: str) -> bytes:
    """
    Generates a PDF with the given text content.
    """
    # Setup PDF (A4 is default in FPDF)
    # unit='mm' is default
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    
    # Add a page (required before writing)
    pdf.add_page()
    
    # Set font (Courier, equivalent to 'normal' style, size 10)
    pdf.set_font("Courier", style="", size=10)
    
    # Formatting constants
    line_height = 5
    # FPDF handles margins automatically via set_margins or simply by x/y positioning.
    # We set strict margins to match the JS 'margin = 15' logic
    pdf.set_margins(left=15, top=15, right=15)
    
    # In jsPDF, you manually calculated page breaks and split text.
    # In FPDF, 'multi_cell' handles text wrapping and auto-pagination automatically.
    # w=0 means "width of the page starting from current margin"
    pdf.multi_cell(w=0, h=line_height, txt=content)
    
    # Return bytes (equivalent to Blob)
    return bytes(pdf.output())
