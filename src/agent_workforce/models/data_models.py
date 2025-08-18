# Data models and classes

from dataclasses import dataclass, field
from typing import Dict, Any, List, Literal
from pydantic import BaseModel

@dataclass
class AnalysisContext:
    document_id: str
    pages: List[str] = field(default_factory=list)
    total_pages: int = 0
    document_type: str = ""
    high_level_type: str = ""
    file_type: str = ""

class Classification(BaseModel):
    document_type: Literal["Invoice", "Bank_Statement", "Agreement", "Deed", "Contract", "Receipt", "Form", "Report"]
    document_high_level_type: Literal["Finance", "Legal", "Human Resources", "Healthcare", "Education", "Electricity", "Gas", "Water", "Internet", "Telecommunications", "Insurance", "Real Estate", "Transportation", "Retail", "Manufacturing", "Government", "Non-Profit", "Other"]
    total_pages: int

class DocumentMeta(BaseModel):
    document_type: str
    document_high_level_type: str
    total_pages: int

class Page(BaseModel):
    page_number: int
    sections: Dict[str, Any]

class DocumentAnalysis(BaseModel):
    document_meta: DocumentMeta
    pages: List[Page]
