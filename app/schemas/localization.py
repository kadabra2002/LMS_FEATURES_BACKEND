from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class LanguageBase(BaseModel):
    code: str = Field(max_length=10, pattern="^[a-z]{2}(-[A-Z]{2})?$")
    name: str = Field(max_length=100)
    native_name: str = Field(max_length=100)
    is_active: bool = True
    is_default: bool = False
    is_rtl: bool = False


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    native_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    is_rtl: Optional[bool] = None


class LanguageResponse(LanguageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    completion_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None


# Translation Schemas
class TranslationBase(BaseModel):
    language_id: UUID
    translation_key: str = Field(max_length=500)
    translation_value: str
    context: Optional[str] = Field(None, max_length=100)
    namespace: Optional[str] = Field(None, max_length=100)
    is_pluralized: bool = False
    plural_forms: Optional[Dict[str, str]] = None
    source_text: Optional[str] = None
    translator_notes: Optional[str] = None
    reviewer_notes: Optional[str] = None


class TranslationCreate(TranslationBase):
    translated_by: Optional[UUID] = None


class TranslationUpdate(BaseModel):
    translation_value: Optional[str] = None
    context: Optional[str] = Field(None, max_length=100)
    namespace: Optional[str] = Field(None, max_length=100)
    is_pluralized: Optional[bool] = None
    plural_forms: Optional[Dict[str, str]] = None
    source_text: Optional[str] = None
    translator_notes: Optional[str] = None
    reviewer_notes: Optional[str] = None
    is_reviewed: Optional[bool] = None
    is_approved: Optional[bool] = None
    needs_update: Optional[bool] = None
    reviewed_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None


class TranslationResponse(TranslationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_reviewed: bool
    is_approved: bool
    needs_update: bool
    translated_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Bulk translation operations
class BulkTranslationCreate(BaseModel):
    language_id: UUID
    translations: List[Dict[str, str]]  # key-value pairs
    context: Optional[str] = None
    namespace: Optional[str] = None
    translated_by: Optional[UUID] = None


class TranslationExport(BaseModel):
    language_code: str
    format: str = Field(pattern="^(json|csv|po|xliff)$")
    namespace: Optional[str] = None
    include_metadata: bool = False