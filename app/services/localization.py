from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.localization import Language, Translation
from app.schemas.localization import (
    LanguageCreate, LanguageUpdate,
    TranslationCreate, TranslationUpdate,
    BulkTranslationCreate
)


class LocalizationService:
    """Service for managing languages and translations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Language Methods
    async def create_language(self, language_data: LanguageCreate) -> Language:
        """Create a new language."""
        language = Language(**language_data.model_dump())
        self.db.add(language)
        await self.db.commit()
        await self.db.refresh(language)
        return language
    
    async def get_language(self, language_id: UUID) -> Optional[Language]:
        """Get language by ID."""
        result = await self.db.execute(
            select(Language).where(Language.id == language_id)
        )
        return result.scalar_one_or_none()
    
    async def get_language_by_code(self, code: str) -> Optional[Language]:
        """Get language by code."""
        result = await self.db.execute(
            select(Language).where(Language.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_languages(
        self,
        is_active: Optional[bool] = None,
        is_default: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Language]:
        """Get languages with optional filters."""
        query = select(Language)
        
        if is_active is not None:
            query = query.where(Language.is_active == is_active)
        if is_default is not None:
            query = query.where(Language.is_default == is_default)
        
        query = query.offset(skip).limit(limit).order_by(Language.name.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_language(
        self,
        language_id: UUID,
        language_data: LanguageUpdate
    ) -> Optional[Language]:
        """Update language."""
        existing = await self.get_language(language_id)
        if not existing:
            return None
        
        update_data = language_data.model_dump(exclude_unset=True)
        
        # If setting as default, unset other defaults
        if update_data.get("is_default"):
            await self.db.execute(
                update(Language)
                .where(Language.id != language_id)
                .values(is_default=False)
            )
        
        await self.db.execute(
            update(Language)
            .where(Language.id == language_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_language(language_id)
    
    async def delete_language(self, language_id: UUID) -> bool:
        """Delete language and related translations."""
        result = await self.db.execute(
            delete(Language).where(Language.id == language_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_default_language(self) -> Optional[Language]:
        """Get the default language."""
        result = await self.db.execute(
            select(Language).where(Language.is_default == True)
        )
        return result.scalar_one_or_none()
    
    # Translation Methods
    async def create_translation(self, translation_data: TranslationCreate) -> Translation:
        """Create a new translation."""
        translation = Translation(**translation_data.model_dump())
        self.db.add(translation)
        await self.db.commit()
        await self.db.refresh(translation)
        
        # Update language completion percentage
        await self._update_language_completion(translation.language_id)
        
        return translation
    
    async def get_translation(self, translation_id: UUID) -> Optional[Translation]:
        """Get translation by ID."""
        result = await self.db.execute(
            select(Translation).where(Translation.id == translation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_translation_by_key(
        self,
        language_id: UUID,
        translation_key: str,
        context: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Optional[Translation]:
        """Get translation by key and language."""
        query = select(Translation).where(
            and_(
                Translation.language_id == language_id,
                Translation.translation_key == translation_key
            )
        )
        
        if context:
            query = query.where(Translation.context == context)
        if namespace:
            query = query.where(Translation.namespace == namespace)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_translations(
        self,
        language_id: Optional[UUID] = None,
        context: Optional[str] = None,
        namespace: Optional[str] = None,
        is_approved: Optional[bool] = None,
        needs_update: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Translation]:
        """Get translations with optional filters."""
        query = select(Translation)
        
        if language_id:
            query = query.where(Translation.language_id == language_id)
        if context:
            query = query.where(Translation.context == context)
        if namespace:
            query = query.where(Translation.namespace == namespace)
        if is_approved is not None:
            query = query.where(Translation.is_approved == is_approved)
        if needs_update is not None:
            query = query.where(Translation.needs_update == needs_update)
        if search:
            query = query.where(
                or_(
                    Translation.translation_key.ilike(f"%{search}%"),
                    Translation.translation_value.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(Translation.translation_key.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_translation(
        self,
        translation_id: UUID,
        translation_data: TranslationUpdate
    ) -> Optional[Translation]:
        """Update translation."""
        existing = await self.get_translation(translation_id)
        if not existing:
            return None
        
        update_data = translation_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Translation)
            .where(Translation.id == translation_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        # Update language completion percentage
        await self._update_language_completion(existing.language_id)
        
        return await self.get_translation(translation_id)
    
    async def delete_translation(self, translation_id: UUID) -> bool:
        """Delete translation."""
        translation = await self.get_translation(translation_id)
        if not translation:
            return False
        
        language_id = translation.language_id
        
        result = await self.db.execute(
            delete(Translation).where(Translation.id == translation_id)
        )
        await self.db.commit()
        
        if result.rowcount > 0:
            # Update language completion percentage
            await self._update_language_completion(language_id)
            return True
        
        return False
    
    async def bulk_create_translations(
        self,
        bulk_data: BulkTranslationCreate
    ) -> List[Translation]:
        """Create multiple translations at once."""
        translations = []
        
        for translation_item in bulk_data.translations:
            translation_data = TranslationCreate(
                language_id=bulk_data.language_id,
                translation_key=translation_item["key"],
                translation_value=translation_item["value"],
                context=bulk_data.context,
                namespace=bulk_data.namespace,
                translated_by=bulk_data.translated_by
            )
            
            # Check if translation already exists
            existing = await self.get_translation_by_key(
                bulk_data.language_id,
                translation_item["key"],
                bulk_data.context,
                bulk_data.namespace
            )
            
            if not existing:
                translation = Translation(**translation_data.model_dump())
                self.db.add(translation)
                translations.append(translation)
        
        await self.db.commit()
        
        # Refresh all created translations
        for translation in translations:
            await self.db.refresh(translation)
        
        # Update language completion percentage
        if translations:
            await self._update_language_completion(bulk_data.language_id)
        
        return translations
    
    async def approve_translation(self, translation_id: UUID, approved_by: UUID) -> bool:
        """Approve a translation."""
        result = await self.db.execute(
            update(Translation)
            .where(Translation.id == translation_id)
            .values(
                is_approved=True,
                approved_by=approved_by,
                needs_update=False
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def mark_translation_for_update(self, translation_id: UUID) -> bool:
        """Mark translation as needing update."""
        result = await self.db.execute(
            update(Translation)
            .where(Translation.id == translation_id)
            .values(needs_update=True, is_approved=False)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Utility Methods
    async def _update_language_completion(self, language_id: UUID) -> None:
        """Update completion percentage for a language."""
        # Get total translations for this language
        result = await self.db.execute(
            select(func.count(Translation.id)).where(Translation.language_id == language_id)
        )
        total_translations = result.scalar() or 0
        
        # Get approved translations
        result = await self.db.execute(
            select(func.count(Translation.id)).where(
                and_(
                    Translation.language_id == language_id,
                    Translation.is_approved == True
                )
            )
        )
        approved_translations = result.scalar() or 0
        
        # Calculate completion percentage
        completion_percentage = (approved_translations / total_translations * 100) if total_translations > 0 else 0
        
        # Update language
        await self.db.execute(
            update(Language)
            .where(Language.id == language_id)
            .values(completion_percentage=completion_percentage)
        )
        await self.db.commit()
    
    async def get_translation_keys_for_language(
        self,
        language_code: str,
        namespace: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """Get all translation key-value pairs for a language."""
        language = await self.get_language_by_code(language_code)
        if not language:
            return {}
        
        query = select(Translation).where(Translation.language_id == language.id)
        
        if namespace:
            query = query.where(Translation.namespace == namespace)
        if context:
            query = query.where(Translation.context == context)
        
        result = await self.db.execute(query)
        translations = result.scalars().all()
        
        return {t.translation_key: t.translation_value for t in translations}
    
    async def get_missing_translations(
        self,
        source_language_code: str,
        target_language_code: str,
        namespace: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get translation keys that exist in source language but not in target."""
        source_lang = await self.get_language_by_code(source_language_code)
        target_lang = await self.get_language_by_code(target_language_code)
        
        if not source_lang or not target_lang:
            return []
        
        # Get all keys from source language
        source_query = select(Translation.translation_key, Translation.translation_value).where(
            Translation.language_id == source_lang.id
        )
        if namespace:
            source_query = source_query.where(Translation.namespace == namespace)
        
        source_result = await self.db.execute(source_query)
        source_keys = {row[0]: row[1] for row in source_result.fetchall()}
        
        # Get all keys from target language
        target_query = select(Translation.translation_key).where(
            Translation.language_id == target_lang.id
        )
        if namespace:
            target_query = target_query.where(Translation.namespace == namespace)
        
        target_result = await self.db.execute(target_query)
        target_keys = {row[0] for row in target_result.fetchall()}
        
        # Find missing keys
        missing_keys = set(source_keys.keys()) - target_keys
        
        return [
            {
                "translation_key": key,
                "source_value": source_keys[key],
                "namespace": namespace
            }
            for key in missing_keys
        ]
    
    # Analytics
    async def get_localization_analytics(self) -> Dict[str, Any]:
        """Get comprehensive localization analytics."""
        # Get language statistics
        result = await self.db.execute(select(Language))
        languages = result.scalars().all()
        
        total_languages = len(languages)
        active_languages = len([l for l in languages if l.is_active])
        
        # Get translation statistics
        result = await self.db.execute(select(Translation))
        translations = result.scalars().all()
        
        total_translations = len(translations)
        approved_translations = len([t for t in translations if t.is_approved])
        pending_translations = len([t for t in translations if not t.is_approved])
        needs_update = len([t for t in translations if t.needs_update])
        
        # Language completion rates
        language_completion = {}
        for language in languages:
            language_completion[language.code] = {
                "name": language.name,
                "completion_percentage": language.completion_percentage,
                "is_active": language.is_active
            }
        
        # Context breakdown
        context_breakdown = {}
        for translation in translations:
            context = translation.context or "default"
            context_breakdown[context] = context_breakdown.get(context, 0) + 1
        
        return {
            "language_stats": {
                "total_languages": total_languages,
                "active_languages": active_languages,
                "inactive_languages": total_languages - active_languages
            },
            "translation_stats": {
                "total_translations": total_translations,
                "approved_translations": approved_translations,
                "pending_translations": pending_translations,
                "needs_update": needs_update,
                "approval_rate": (approved_translations / total_translations * 100) if total_translations > 0 else 0
            },
            "language_completion": language_completion,
            "context_breakdown": context_breakdown
        }