from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.schemas.localization import (
    LanguageCreate, LanguageUpdate, LanguageResponse,
    TranslationCreate, TranslationUpdate, TranslationResponse,
    BulkTranslationCreate, TranslationExport
)
from app.services.localization import LocalizationService

router = APIRouter()


# Language Endpoints
@router.post("/languages", response_model=LanguageResponse)
async def create_language(
    language_data: LanguageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new language."""
    service = LocalizationService(db)
    return await service.create_language(language_data)


@router.get("/languages/{language_id}", response_model=LanguageResponse)
async def get_language(
    language_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get language by ID."""
    service = LocalizationService(db)
    language = await service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    return language


@router.get("/languages/code/{code}", response_model=LanguageResponse)
async def get_language_by_code(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get language by code."""
    service = LocalizationService(db)
    language = await service.get_language_by_code(code)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    return language


@router.get("/languages", response_model=List[LanguageResponse])
async def get_languages(
    is_active: Optional[bool] = Query(None),
    is_default: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get languages with optional filters."""
    service = LocalizationService(db)
    return await service.get_languages(
        is_active=is_active,
        is_default=is_default,
        skip=skip,
        limit=limit
    )


@router.put("/languages/{language_id}", response_model=LanguageResponse)
async def update_language(
    language_id: UUID,
    language_data: LanguageUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update language."""
    service = LocalizationService(db)
    language = await service.update_language(language_id, language_data)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    return language


@router.delete("/languages/{language_id}")
async def delete_language(
    language_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete language."""
    service = LocalizationService(db)
    success = await service.delete_language(language_id)
    if not success:
        raise HTTPException(status_code=404, detail="Language not found")
    return {"message": "Language deleted successfully"}


@router.get("/languages/default", response_model=LanguageResponse)
async def get_default_language(
    db: AsyncSession = Depends(get_db)
):
    """Get the default language."""
    service = LocalizationService(db)
    language = await service.get_default_language()
    if not language:
        raise HTTPException(status_code=404, detail="No default language set")
    return language


# Translation Endpoints
@router.post("/translations", response_model=TranslationResponse)
async def create_translation(
    translation_data: TranslationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new translation."""
    service = LocalizationService(db)
    return await service.create_translation(translation_data)


@router.get("/translations/{translation_id}", response_model=TranslationResponse)
async def get_translation(
    translation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get translation by ID."""
    service = LocalizationService(db)
    translation = await service.get_translation(translation_id)
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translation


@router.get("/translations", response_model=List[TranslationResponse])
async def get_translations(
    language_id: Optional[UUID] = Query(None),
    context: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    is_approved: Optional[bool] = Query(None),
    needs_update: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get translations with optional filters."""
    service = LocalizationService(db)
    return await service.get_translations(
        language_id=language_id,
        context=context,
        namespace=namespace,
        is_approved=is_approved,
        needs_update=needs_update,
        search=search,
        skip=skip,
        limit=limit
    )


@router.put("/translations/{translation_id}", response_model=TranslationResponse)
async def update_translation(
    translation_id: UUID,
    translation_data: TranslationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update translation."""
    service = LocalizationService(db)
    translation = await service.update_translation(translation_id, translation_data)
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translation


@router.delete("/translations/{translation_id}")
async def delete_translation(
    translation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete translation."""
    service = LocalizationService(db)
    success = await service.delete_translation(translation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Translation not found")
    return {"message": "Translation deleted successfully"}


@router.post("/translations/bulk", response_model=List[TranslationResponse])
async def bulk_create_translations(
    bulk_data: BulkTranslationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create multiple translations at once."""
    service = LocalizationService(db)
    return await service.bulk_create_translations(bulk_data)


@router.post("/translations/{translation_id}/approve")
async def approve_translation(
    translation_id: UUID,
    approved_by: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Approve a translation."""
    service = LocalizationService(db)
    success = await service.approve_translation(translation_id, approved_by)
    if not success:
        raise HTTPException(status_code=404, detail="Translation not found")
    return {"message": "Translation approved"}


@router.post("/translations/{translation_id}/mark-for-update")
async def mark_translation_for_update(
    translation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Mark translation as needing update."""
    service = LocalizationService(db)
    success = await service.mark_translation_for_update(translation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Translation not found")
    return {"message": "Translation marked for update"}


# Utility Endpoints
@router.get("/languages/{language_code}/translations")
async def get_translation_keys_for_language(
    language_code: str,
    namespace: Optional[str] = Query(None),
    context: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all translation key-value pairs for a language."""
    service = LocalizationService(db)
    return await service.get_translation_keys_for_language(
        language_code=language_code,
        namespace=namespace,
        context=context
    )


@router.get("/missing-translations")
async def get_missing_translations(
    source_language_code: str = Query(...),
    target_language_code: str = Query(...),
    namespace: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get translation keys that exist in source language but not in target."""
    service = LocalizationService(db)
    return await service.get_missing_translations(
        source_language_code=source_language_code,
        target_language_code=target_language_code,
        namespace=namespace
    )


@router.get("/analytics")
async def get_localization_analytics(
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive localization analytics."""
    service = LocalizationService(db)
    return await service.get_localization_analytics()