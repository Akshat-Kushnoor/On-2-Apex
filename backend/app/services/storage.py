import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, status
from app.core.config import ROOT_DIR
from app.core.errors import AppException

STORAGE_DIR = ROOT_DIR / "storage" / "resumes"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf"}


class StorageService:
    def __init__(self):
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadFile, user_id: str) -> Tuple[str, str, int]:
        original_name = file.filename or "unknown.pdf"
        ext = Path(original_name).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise AppException(
                message="Only PDF documents are supported.",
                code="INVALID_FILE_TYPE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        content = file.file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise AppException(
                message="File size exceeds maximum limit of 10MB.",
                code="FILE_TOO_LARGE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if file_size == 0:
            raise AppException(
                message="Uploaded file is empty.",
                code="EMPTY_FILE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        stored_filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
        destination = STORAGE_DIR / stored_filename

        with open(destination, "wb") as f:
            f.write(content)

        return stored_filename, str(destination.resolve()), file_size

    def get_file_path(self, stored_filename: str) -> Path:
        target = STORAGE_DIR / stored_filename
        if not target.exists():
            raise AppException(
                message="File not found in storage.",
                code="FILE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return target

    def delete_file(self, stored_filename: str) -> bool:
        target = STORAGE_DIR / stored_filename
        if target.exists():
            try:
                target.unlink()
                return True
            except OSError:
                return False
        return False


storage_service = StorageService()
