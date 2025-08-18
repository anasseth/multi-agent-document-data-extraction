import os
import requests
import pandas as pd  
from io import BytesIO
from docx import Document  # For Word# For Excel
from pypdf import PdfReader  # Existing for PDF
from agents import function_tool, RunContextWrapper
from ..models.data_models import AnalysisContext

def fetch_document(ctx: RunContextWrapper[AnalysisContext]) -> str:
    # GET endpoint with file_url query parameter
    file_url = "https://inbox-mails-files-storage.s3.amazonaws.com/attached-files/6853c64130388c569013f7a7/2151094325_15082025101707.pdf"
    url = f"https://dev.encodrix.com/api/folders/stream_file/?file_url={file_url}"
    
    # Headers with bearer token
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1NTk0Njg5LCJpYXQiOjE3NTU1MDgyODksImp0aSI6Ijk0M2E0NjhkMzJmZDQ5ZDBhNjVjOWNjZDFhMjYzYzhiIiwiX2lkIjoiNjgyYjY3NDBkODJkODliYWJjNTBiNzY3Iiwicm9sZSI6ImNsaWVudCIsInBlcm1pc3Npb25zIjpbInZpZXdfZG9jdW1lbnRzIiwiTWFuYWdlIFVzZXJzIiwiYXBwcm92ZV9yZXF1ZXN0Il19.BYNtFv003a4lGaPEy48SFqq0dAEdVRkkC836cxSsAKs",  # Replace with actual token
        # "Accept": "application/pdf"
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get("Content-Type", "").lower()
        file_ext = os.path.splitext(file_url)[1].lower()  # Detect from URL if needed
        
        content = BytesIO(response.content)
        
        if "pdf" in content_type or file_ext == ".pdf":
            ctx.context.file_type = "pdf"
            reader = PdfReader(content)
            ctx.context.content_sections = [{"section_id": i+1, "content": page.extract_text() or ""} for i, page in enumerate(reader.pages)]
        
        elif "word" in content_type or file_ext in (".doc", ".docx"):
            ctx.context.file_type = "docx"
            doc = Document(content)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            # Split into "sections" (e.g., paragraphs as pseudo-pages)
            sections = full_text.split("\n\n")  # Simple split; improve if needed
            ctx.context.content_sections = [{"section_id": i+1, "content": sec} for i, sec in enumerate(sections) if sec.strip()]
        
        elif "excel" in content_type or file_ext in (".xls", ".xlsx"):
            ctx.context.file_type = "xlsx"
            xls = pd.ExcelFile(content)
            ctx.context.content_sections = []
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                ctx.context.content_sections.append({"section_id": sheet_name, "content": df.to_csv(index=False)})  # Convert to CSV string for text analysis
        
        elif "text" in content_type or file_ext == ".txt":
            ctx.context.file_type = "txt"
            text_content = content.read().decode("utf-8")
            ctx.context.content_sections = [{"section_id": 1, "content": text_content}]
        
        else:
            return "Unsupported file type."
        
        ctx.context.total_sections = len(ctx.context.content_sections)
        return f"Document fetched as {ctx.context.file_type} with {ctx.context.total_sections} sections."

    except Exception as e:
        return f"Error fetching/parsing document: {str(e)}"