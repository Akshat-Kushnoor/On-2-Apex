from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.llm import LLMProviderConfig
from app.models.user import User
from app.schemas.llm import (
    LLMConfigOut,
    LLMConfigUpdate,
    LLMTestRequest,
    LLMTestResponse,
)
from app.services.llm_gateway import llm_gateway, mask_api_key

router = APIRouter()


@router.get("", response_model=LLMConfigOut)
def get_llm_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = db.query(LLMProviderConfig).filter(LLMProviderConfig.user_id == current_user.id).first()
    if not config:
        config = LLMProviderConfig(user_id=current_user.id)
        db.add(config)
        db.commit()
        db.refresh(config)

    return LLMConfigOut(
        id=config.id,
        user_id=config.user_id,
        primary_provider=config.primary_provider,
        primary_model=config.primary_model,
        primary_api_key_masked=mask_api_key(config.primary_api_key),
        primary_base_url=config.primary_base_url,
        backup_provider=config.backup_provider,
        backup_model=config.backup_model,
        backup_api_key_masked=mask_api_key(config.backup_api_key),
        backup_base_url=config.backup_base_url,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.put("", response_model=LLMConfigOut)
def update_llm_settings(
    payload: LLMConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = db.query(LLMProviderConfig).filter(LLMProviderConfig.user_id == current_user.id).first()
    if not config:
        config = LLMProviderConfig(user_id=current_user.id)
        db.add(config)

    config.primary_provider = payload.primary_provider
    config.primary_model = payload.primary_model.strip()
    if payload.primary_api_key is not None:
        config.primary_api_key = payload.primary_api_key.strip() or None
    if payload.primary_base_url is not None:
        config.primary_base_url = payload.primary_base_url.strip() or None

    config.backup_provider = payload.backup_provider
    config.backup_model = payload.backup_model.strip() if payload.backup_model else None
    if payload.backup_api_key is not None:
        config.backup_api_key = payload.backup_api_key.strip() or None
    if payload.backup_base_url is not None:
        config.backup_base_url = payload.backup_base_url.strip() or None

    db.commit()
    db.refresh(config)

    return LLMConfigOut(
        id=config.id,
        user_id=config.user_id,
        primary_provider=config.primary_provider,
        primary_model=config.primary_model,
        primary_api_key_masked=mask_api_key(config.primary_api_key),
        primary_base_url=config.primary_base_url,
        backup_provider=config.backup_provider,
        backup_model=config.backup_model,
        backup_api_key_masked=mask_api_key(config.backup_api_key),
        backup_base_url=config.backup_base_url,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.post("/test", response_model=LLMTestResponse)
def test_llm_provider(
    payload: LLMTestRequest,
    current_user: User = Depends(get_current_user),
):
    success, latency, resp, err = llm_gateway.test_connection(
        provider=payload.provider,
        model=payload.model,
        api_key=payload.api_key,
        base_url=payload.base_url,
    )
    return LLMTestResponse(
        success=success,
        provider=payload.provider,
        model=payload.model,
        latency_ms=round(latency, 2),
        response=resp,
        error=err,
    )
