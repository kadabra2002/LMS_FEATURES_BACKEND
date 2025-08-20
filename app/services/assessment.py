from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.assessment import Assessment, Question, UserAnswer, Feedback
from app.schemas.assessment import (
    AssessmentCreate, AssessmentUpdate,
    QuestionCreate, QuestionUpdate,
    UserAnswerCreate, FeedbackCreate
)


class AssessmentService:
    """Service for managing assessments, questions, and feedback."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Assessment Methods
    async def create_assessment(self, assessment_data: AssessmentCreate) -> Assessment:
        """Create a new assessment."""
        assessment = Assessment(**assessment_data.model_dump())
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment
    
    async def get_assessment(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID with related questions."""
        result = await self.db.execute(
            select(Assessment)
            .options(selectinload(Assessment.questions))
            .where(Assessment.id == assessment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_assessments(
        self,
        course_id: Optional[UUID] = None,
        module_id: Optional[UUID] = None,
        assessment_type: Optional[str] = None,
        created_by: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Assessment]:
        """Get assessments with optional filters."""
        query = select(Assessment)
        
        if course_id:
            query = query.where(Assessment.course_id == course_id)
        if module_id:
            query = query.where(Assessment.module_id == module_id)
        if assessment_type:
            query = query.where(Assessment.assessment_type == assessment_type)
        if created_by:
            query = query.where(Assessment.created_by == created_by)
        
        query = query.offset(skip).limit(limit).order_by(Assessment.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_assessment(
        self,
        assessment_id: UUID,
        assessment_data: AssessmentUpdate
    ) -> Optional[Assessment]:
        """Update assessment."""
        existing = await self.get_assessment(assessment_id)
        if not existing:
            return None
        
        update_data = assessment_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Assessment)
            .where(Assessment.id == assessment_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_assessment(assessment_id)
    
    async def delete_assessment(self, assessment_id: UUID) -> bool:
        """Delete assessment and related records."""
        result = await self.db.execute(
            delete(Assessment).where(Assessment.id == assessment_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Question Methods
    async def create_question(self, question_data: QuestionCreate) -> Question:
        """Create a new question."""
        question = Question(**question_data.model_dump())
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question
    
    async def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID."""
        result = await self.db.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()
    
    async def get_assessment_questions(
        self,
        assessment_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Question]:
        """Get questions for an assessment ordered by sequence."""
        result = await self.db.execute(
            select(Question)
            .where(Question.assessment_id == assessment_id)
            .order_by(Question.order_sequence)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_question(
        self,
        question_id: UUID,
        question_data: QuestionUpdate
    ) -> Optional[Question]:
        """Update question."""
        existing = await self.get_question(question_id)
        if not existing:
            return None
        
        update_data = question_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Question)
            .where(Question.id == question_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_question(question_id)
    
    async def delete_question(self, question_id: UUID) -> bool:
        """Delete question."""
        result = await self.db.execute(
            delete(Question).where(Question.id == question_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # User Answer Methods
    async def create_user_answer(self, answer_data: UserAnswerCreate) -> UserAnswer:
        """Create a new user answer."""
        answer = UserAnswer(**answer_data.model_dump())
        self.db.add(answer)
        await self.db.commit()
        await self.db.refresh(answer)
        return answer
    
    async def get_user_answer(self, answer_id: UUID) -> Optional[UserAnswer]:
        """Get user answer by ID."""
        result = await self.db.execute(
            select(UserAnswer).where(UserAnswer.id == answer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_assessment_answers(
        self,
        user_assessment_id: UUID
    ) -> List[UserAnswer]:
        """Get all answers for a user assessment."""
        result = await self.db.execute(
            select(UserAnswer)
            .where(UserAnswer.user_assessment_id == user_assessment_id)
            .order_by(UserAnswer.submitted_at)
        )
        return result.scalars().all()
    
    # Feedback Methods
    async def create_feedback(self, feedback_data: FeedbackCreate) -> Feedback:
        """Create new feedback."""
        feedback = Feedback(**feedback_data.model_dump())
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback
    
    async def get_feedback(self, feedback_id: UUID) -> Optional[Feedback]:
        """Get feedback by ID."""
        result = await self.db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        return result.scalar_one_or_none()
    
    async def get_assessment_feedback(
        self,
        assessment_id: UUID,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Feedback]:
        """Get feedback for an assessment."""
        query = select(Feedback).where(Feedback.assessment_id == assessment_id)
        
        if user_id:
            query = query.where(Feedback.user_id == user_id)
        
        query = query.offset(skip).limit(limit).order_by(Feedback.given_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # Assessment Analytics
    async def get_assessment_analytics(self, assessment_id: UUID) -> Dict[str, Any]:
        """Get comprehensive analytics for an assessment."""
        # Get assessment details
        assessment = await self.get_assessment(assessment_id)
        if not assessment:
            return {"error": "Assessment not found"}
        
        # Get user assessments for this assessment
        from app.models.progress import UserAssessment
        result = await self.db.execute(
            select(UserAssessment).where(UserAssessment.assessment_id == assessment_id)
        )
        user_assessments = result.scalars().all()
        
        total_attempts = len(user_assessments)
        completed_attempts = len([ua for ua in user_assessments if ua.status == "completed"])
        
        if completed_attempts > 0:
            scores = [ua.score for ua in user_assessments if ua.score is not None]
            average_score = sum(scores) / len(scores) if scores else 0
            pass_rate = len([ua for ua in user_assessments if ua.percentage and ua.percentage >= assessment.passing_score]) / completed_attempts * 100
        else:
            average_score = 0
            pass_rate = 0
        
        return {
            "assessment_id": str(assessment_id),
            "assessment_title": assessment.title,
            "statistics": {
                "total_attempts": total_attempts,
                "completed_attempts": completed_attempts,
                "completion_rate": (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                "average_score": round(average_score, 2),
                "pass_rate": round(pass_rate, 2)
            },
            "performance_distribution": self._calculate_score_distribution(user_assessments)
        }
    
    def _calculate_score_distribution(self, user_assessments: List) -> Dict[str, int]:
        """Calculate score distribution for analytics."""
        distribution = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0
        }
        
        for ua in user_assessments:
            if ua.percentage is not None:
                if ua.percentage <= 20:
                    distribution["0-20"] += 1
                elif ua.percentage <= 40:
                    distribution["21-40"] += 1
                elif ua.percentage <= 60:
                    distribution["41-60"] += 1
                elif ua.percentage <= 80:
                    distribution["61-80"] += 1
                else:
                    distribution["81-100"] += 1
        
        return distribution