from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class Language(BaseModel):
    __tablename__ = "languages"
    
    code = Column(String(10), unique=True, nullable=False, index=True)  # en, es, fr, de, zh
    name = Column(String(100), nullable=False)  # English, Spanish, French, etc.
    native_name = Column(String(100), nullable=False)  # English, Español, Français, etc.
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    is_rtl = Column(Boolean, default=False)  # Right-to-left languages
    
    completion_percentage = Column(Float, default=0.0)  # Translation completion
    
    # Relationships
    translations = relationship("Translation", back_populates="language")


class Translation(BaseModel):
    __tablename__ = "translations"
    
    language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=False)
    
    translation_key = Column(String(500), nullable=False, index=True)  # Dot notation key
    translation_value = Column(Text, nullable=False)
    
    context = Column(String(100), nullable=True)  # UI, course_content, email, etc.
    namespace = Column(String(100), nullable=True)  # Group related translations
    
    # Metadata
    is_pluralized = Column(Boolean, default=False)
    plural_forms = Column(JSON, nullable=True)  # For languages with complex pluralization
    
    # Quality control
    is_reviewed = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    needs_update = Column(Boolean, default=False)
    
    # Source information
    source_text = Column(Text, nullable=True)  # Original text for reference
    translator_notes = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    translated_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    language = relationship("Language", back_populates="translations")