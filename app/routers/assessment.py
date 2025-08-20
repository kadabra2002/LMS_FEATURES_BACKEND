from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.assessment import (
    AssessmentCreate, AssessmentUpdate, AssessmentResponse,
    QuestionCreate, QuestionUpdate, QuestionResponse,
    UserAnswerCreate, UserAnswerResponse,
    FeedbackCreate, FeedbackResponse
)
from app.services.assessment import AssessmentService

router = APIRouter()


# Assessment Endpoints
@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new assessment."""
    service = AssessmentService(db)
    return await service.create_assessment(assessment_data)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get assessment by ID."""
    service = AssessmentService(db)
    assessment = await service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.get("/", response_model=List[AssessmentResponse])
async def get_assessments(
    course_id: Optional[UUID] = Query(None),
    module_id: Optional[UUID] = Query(None),
    assessment_type: Optional[str] = Query(None),
    created_by: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get assessments with optional filters."""
    service = AssessmentService(db)
    return await service.get_assessments(
        course_id=course_id,
        module_id=module_id,
        assessment_type=assessment_type,
        created_by=created_by,
        skip=skip,
        limit=limit
    )


@router.put("/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(
    assessment_id: UUID,
    assessment_data: AssessmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update assessment."""
    service = AssessmentService(db)
    assessment = await service.update_assessment(assessment_id, assessment_data)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.delete("/{assessment_id}")
async def delete_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete assessment."""
    service = AssessmentService(db)
    success = await service.delete_assessment(assessment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"message": "Assessment deleted successfully"}


# Question Endpoints
@router.post("/{assessment_id}/questions", response_model=QuestionResponse)
async def create_question(
    assessment_id: UUID,
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new question for an assessment."""
    if question_data.assessment_id != assessment_id:
        raise HTTPException(status_code=400, detail="Assessment ID mismatch")
    
    service = AssessmentService(db)
    return await service.create_question(question_data)


@router.get("/{assessment_id}/questions", response_model=List[QuestionResponse])
async def get_assessment_questions(
    assessment_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession =  Depends(get_db)
):
    """Get questions for an assessment."""
    service = AssessmentService(db)
    return await service.get_assessment_questions(assessment_id, skip, limit)


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get question by ID."""
    service = AssessmentService(db)
    question = await service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update question."""
    service = AssessmentService(db)
    question = await service.update_question(question_id, question_data)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete question."""
    service = AssessmentService(db)
    success = await service.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


# User Answer Endpoints
@router.post("/answers", response_model=UserAnswerResponse)
async def create_user_answer(
    answer_data: UserAnswerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user answer."""
    service = AssessmentService(db)
    return await service.create_user_answer(answer_data)


@router.get("/answers/{answer_id}", response_model=UserAnswerResponse)
async def get_user_answer(
    answer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user answer by ID."""
    service = AssessmentService(db)
    answer = await service.get_user_answer(answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="User answer not found")
    return answer


@router.get("/user-assessments/{user_assessment_id}/answers", response_model=List[UserAnswerResponse])
async def get_user_assessment_answers(
    user_assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all answers for a user assessment."""
    service = AssessmentService(db)
    return await service.get_user_assessment_answers(user_assessment_id)


# Feedback Endpoints
@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new feedback."""
    service = AssessmentService(db)
    return await service.create_feedback(feedback_data)


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get feedback by ID."""
    service = AssessmentService(db)
    feedback = await service.get_feedback(feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.get("/{assessment_id}/feedback", response_model=List[FeedbackResponse])
async def get_assessment_feedback(
    assessment_id: UUID,
    user_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get feedback for an assessment."""
    service = AssessmentService(db)
    return await service.get_assessment_feedback(
        assessment_id=assessment_id,
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get("/{assessment_id}/analytics")
async def get_assessment_analytics(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics for an assessment."""
    service = AssessmentService(db)
    return await service.get_assessment_analytics(assessment_id)