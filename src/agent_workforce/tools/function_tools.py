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
    file_url = ""
    url = f""
    
    headers = {
        "Authorization": "",
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get("Content-Type", "").lower()
        file_ext = os.path.splitext(file_url)[1].lower()  # Detect from URL if needed
        
        content = BytesIO(response.content)

        ctx.context.pages = []

        if "pdf" in content_type or file_ext == ".pdf":
            ctx.context.file_type = "pdf"
            reader = PdfReader(content)
            for page in reader.pages:
                ctx.context.pages.append(page.extract_text() or "")

        elif ("word" in content_type or file_ext in (".docx",)):
            if file_ext == ".doc":
                return "Unsupported file type: .doc (legacy Word). Please convert to .docx."
            ctx.context.file_type = "docx"
            doc = Document(content)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            sections = [sec.strip() for sec in full_text.split("\n\n") if sec.strip()]
            if not sections:
                sections = [full_text]
            ctx.context.pages.extend(sections)

        elif ("spreadsheetml" in content_type) or ("excel" in content_type) or (file_ext in (".xlsx",)):
            if file_ext == ".xls":
                return "Unsupported file type: .xls (legacy Excel). Please convert to .xlsx."
            ctx.context.file_type = "xlsx"
            xls = pd.ExcelFile(content, engine="openpyxl")
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str, engine="openpyxl")
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

@function_tool
def get_complete_analysis(ctx: RunContextWrapper[AnalysisContext]) -> str:
    """
    Get both the original extracted data and the UI-compatible format.
    Returns a JSON string with both formats.
    """
    if not hasattr(ctx.context, 'original_analysis') or not ctx.context.original_analysis:
        return "No analysis data found. Please run document extraction first."
    
    if not hasattr(ctx.context, 'ui_analysis') or not ctx.context.ui_analysis:
        return "No UI analysis data found. Please run UI transformation first."
    
    try:
        import json
        
        complete_analysis = {
            "original": ctx.context.original_analysis,
            "ui_compatible": ctx.context.ui_analysis
        }
        
        return json.dumps(complete_analysis, indent=2)
        
    except Exception as e:
        return f"Error creating complete analysis: {str(e)}"
