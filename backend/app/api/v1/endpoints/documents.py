from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.db.session import get_db
from app.models.document import Document, ParsedDocument
from app.models.profile import (
    Certification,
    Education,
    Experience,
    Project,
    Skill,
)
from app.models.user import User
from app.schemas.document import ApprovalPayload, DocumentOut, ParsedDocumentOut
from app.services.document_engine import document_engine
from app.services.storage import storage_service

router = APIRouter()


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stored_name, file_path, file_size = storage_service.save_file(file, current_user.id)

    document = Document(
        user_id=current_user.id,
        original_filename=file.filename or "uploaded.pdf",
        stored_filename=stored_name,
        file_path=file_path,
        file_size=file_size,
        mime_type="application/pdf",
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        markdown, structured_data = document_engine.parse_pdf(file_path)
        parsed_doc = ParsedDocument(
            document_id=document.id,
            user_id=current_user.id,
            markdown_content=markdown,
            extracted_data=structured_data,
            status="proposed",
        )
        document.status = "processed"
        db.add(parsed_doc)
        db.commit()
        db.refresh(document)
    except Exception as exc:
        document.status = "failed"
        document.error_message = str(exc)
        db.commit()
        raise AppException(
            message=f"Failed to process uploaded resume: {str(exc)}",
            code="PROCESSING_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return document


@router.get("", response_model=List[DocumentOut])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise AppException(
            message="Document not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return doc


@router.get("/{document_id}/markdown")
def get_document_markdown(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parsed = (
        db.query(ParsedDocument)
        .filter(ParsedDocument.document_id == document_id, ParsedDocument.user_id == current_user.id)
        .first()
    )
    if not parsed:
        raise AppException(
            message="Parsed document not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return {
        "document_id": document_id,
        "markdown": parsed.markdown_content,
    }


@router.get("/{document_id}/extraction", response_model=ParsedDocumentOut)
def get_document_extraction(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parsed = (
        db.query(ParsedDocument)
        .filter(ParsedDocument.document_id == document_id, ParsedDocument.user_id == current_user.id)
        .first()
    )
    if not parsed:
        raise AppException(
            message="Parsed document extraction not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return parsed


@router.post("/{document_id}/approve", status_code=status.HTTP_200_OK)
def approve_document_extraction(
    document_id: str,
    payload: ApprovalPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parsed = (
        db.query(ParsedDocument)
        .filter(ParsedDocument.document_id == document_id, ParsedDocument.user_id == current_user.id)
        .first()
    )
    if not parsed:
        raise AppException(
            message="Extraction not found or access denied.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    data = parsed.extracted_data

    if payload.approve_skills:
        existing_skills = {
            s.name.lower() for s in db.query(Skill.name).filter(Skill.user_id == current_user.id).all()
        }
        items = payload.custom_skills if payload.custom_skills is not None else data.get("skills", [])
        for item in items:
            name = item.get("name", "").strip()
            if name and name.lower() not in existing_skills:
                db.add(
                    Skill(
                        user_id=current_user.id,
                        name=name,
                        category=item.get("category", "General"),
                        proficiency=item.get("proficiency", "Intermediate"),
                        evidence=item.get("evidence", "Extracted from resume"),
                    )
                )
                existing_skills.add(name.lower())

    if payload.approve_education:
        items = payload.custom_education if payload.custom_education is not None else data.get("education", [])
        for item in items:
            inst = item.get("institution", "").strip()
            deg = item.get("degree", "").strip()
            if inst and deg:
                db.add(
                    Education(
                        user_id=current_user.id,
                        institution=inst,
                        degree=deg,
                        branch=item.get("branch"),
                        start_year=item.get("start_year"),
                        end_year=item.get("end_year"),
                        cgpa=str(item.get("cgpa")) if item.get("cgpa") else None,
                    )
                )

    if payload.approve_projects:
        items = payload.custom_projects if payload.custom_projects is not None else data.get("projects", [])
        for item in items:
            title = item.get("title", "").strip()
            if title:
                db.add(
                    Project(
                        user_id=current_user.id,
                        title=title,
                        description=item.get("description"),
                        technologies=item.get("technologies", []),
                        role=item.get("role"),
                    )
                )

    if payload.approve_experience:
        items = payload.custom_experience if payload.custom_experience is not None else data.get("experience", [])
        for item in items:
            comp = item.get("company", "").strip()
            role = item.get("role", "").strip()
            if comp and role:
                db.add(
                    Experience(
                        user_id=current_user.id,
                        company=comp,
                        role=role,
                        start_date=item.get("start_date"),
                        end_date=item.get("end_date"),
                        description=item.get("description"),
                        technologies=item.get("technologies", []),
                    )
                )

    if payload.approve_certifications:
        items = payload.custom_certifications if payload.custom_certifications is not None else data.get("certifications", [])
        for item in items:
            name = item.get("name", "").strip()
            if name:
                db.add(
                    Certification(
                        user_id=current_user.id,
                        name=name,
                        issuing_organization=item.get("issuing_organization"),
                        issue_date=item.get("issue_date"),
                    )
                )

    parsed.status = "approved"
    parsed.approved_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "status": "ok",
        "message": "Approved resume entities successfully merged into student profile.",
    }
