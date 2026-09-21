from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    id: str
    user_id: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParsedDocumentOut(BaseModel):
    id: str
    document_id: str
    user_id: str
    markdown_content: str
    extracted_data: Dict[str, Any]
    status: str
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalPayload(BaseModel):
    approve_skills: bool = True
    approve_education: bool = True
    approve_projects: bool = True
    approve_experience: bool = True
    approve_certifications: bool = True
    custom_skills: Optional[List[Dict[str, Any]]] = None
    custom_projects: Optional[List[Dict[str, Any]]] = None
    custom_education: Optional[List[Dict[str, Any]]] = None
    custom_experience: Optional[List[Dict[str, Any]]] = None
    custom_certifications: Optional[List[Dict[str, Any]]] = None
