import os
import requests
import pandas as pd  
from io import BytesIO
from docx import Document
from pypdf import PdfReader
from agents import function_tool, RunContextWrapper
from ..models.data_models import AnalysisContext

@function_tool
async def fetch_document(ctx: RunContextWrapper[AnalysisContext]) -> str:
    file_url = "https://inbox-mails-files-storage.s3.amazonaws.com/attached-files/6853c64130388c569013f7a7/basic-invoice_18082025091811.docx"
    url = f"https://dev.encodrix.com/api/folders/stream_file/?file_url={file_url}"
    
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1NTk0Njg5LCJpYXQiOjE3NTU1MDgyODksImp0aSI6Ijk0M2E0NjhkMzJmZDQ5ZDBhNjVjOWNjZDFhMjYzYzhiIiwiX2lkIjoiNjgyYjY3NDBkODJkODliYWJjNTBiNzY3Iiwicm9sZSI6ImNsaWVudCIsInBlcm1pc3Npb25zIjpbInZpZXdfZG9jdW1lbnRzIiwiTWFuYWdlIFVzZXJzIiwiYXBwcm92ZV9yZXF1ZXN0Il19.BYNtFv003a4lGaPEy48SFqq0dAEdVRkkC836cxSsAKs",
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        print("****************RESPONSE******************")
        print(response)
        print("*******************************************")
        response.raise_for_status()
        
        content_type = response.headers.get("Content-Type", "").lower()
        file_ext = os.path.splitext(file_url)[1].lower()  # Detect from URL if needed
        
        content = BytesIO(response.content)

        # Normalize storage
        ctx.context.pages = []

        if "pdf" in content_type or file_ext == ".pdf":
            ctx.context.file_type = "pdf"
            reader = PdfReader(content)
            for page in reader.pages:
                ctx.context.pages.append(page.extract_text() or "")

        elif ("word" in content_type or file_ext in (".docx",)):
            # Note: legacy .doc is not supported by python-docx
            if file_ext == ".doc":
                return "Unsupported file type: .doc (legacy Word). Please convert to .docx."
            ctx.context.file_type = "docx"
            doc = Document(content)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            # Heuristic: split on double newlines to create pseudo-pages
            sections = [sec.strip() for sec in full_text.split("\n\n") if sec.strip()]
            if not sections:
                sections = [full_text]
            ctx.context.pages.extend(sections)

        elif ("spreadsheetml" in content_type) or ("excel" in content_type) or (file_ext in (".xlsx",)):
            # Prefer robust .xlsx handling via openpyxl
            if file_ext == ".xls":
                return "Unsupported file type: .xls (legacy Excel). Please convert to .xlsx."
            ctx.context.file_type = "xlsx"
            xls = pd.ExcelFile(content, engine="openpyxl")
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str, engine="openpyxl")
                # Convert each sheet into a CSV-like string page
                csv_text = df.to_csv(index=False)
                ctx.context.pages.append(f"Sheet: {sheet_name}\n\n{csv_text}")

        elif "text" in content_type or file_ext == ".txt":
            ctx.context.file_type = "txt"
            text_content = content.read().decode("utf-8", errors="replace")
            ctx.context.pages.append(text_content)

        else:
            return f"Unsupported file type: content_type={content_type} ext={file_ext}"

        ctx.context.total_pages = len(ctx.context.pages)
        return f"Document fetched as {ctx.context.file_type} with {ctx.context.total_pages} pages."

    except Exception as e:
        return f"Error fetching/parsing document: {str(e)}"

@function_tool
def get_page_content(ctx: RunContextWrapper[AnalysisContext], page_number: int) -> str:
    if not 1 <= page_number <= ctx.context.total_pages:
        return "Invalid page number."
    return ctx.context.pages[page_number - 1]
