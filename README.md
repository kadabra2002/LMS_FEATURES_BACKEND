# LMS Learning Management Features Backend

A comprehensive FastAPI backend system for managing learning features in an LMS (Learning Management System) platform. This system implements section 4.5 (Learning Management Features) from the LMS technical specification.

## Features

### 4.5.1 Progress Tracking
- Real-time tracking of learner progress including completion status, time spent, quiz scores, and overall performance
- Comprehensive user assessment tracking with multiple attempt support
- Online attendance tracking for live sessions with engagement metrics

### 4.5.2 Assessments and Online Attendance  
- Multi-format assessment support (MCQ, true-false, matching, essays, etc.)
- Automated grading with detailed feedback mechanisms
- Session attendance tracking with device and platform information

### 4.5.3 Adaptive Learning Paths
- Personalized learning paths based on skill levels and preferences
- Dynamic course recommendations using intelligent algorithms  
- Prerequisites and unlock criteria management

### 4.5.4 Assessments and Feedback
- Comprehensive question bank with multiple question types
- Automated and manual feedback systems
- Performance analytics and improvement suggestions

### 4.5.5 Target Achievement Tracking
- Goal setting and deadline management
- Automated reminder system for approaching deadlines
- Progress monitoring for thesis submissions, exams, certifications

### 4.5.6 Course Scheduling
- Flexible scheduling system for mandatory/optional courses
- Multiple delivery modes (online, blended, in-person)
- Enrollment management with capacity limits

### 4.5.7 Activity Reusability
- Reusable activity templates for efficient content creation
- Activity library with sharing capabilities
- Template versioning and rating system

### 4.5.8 Automation
- Rule-based automation engine for repetitive tasks
- User grouping and bulk operations
- Automated notifications and escalations

### 4.5.9 Localization
- Multi-language support with translation management
- Dynamic content localization
- RTL language support

### 4.5.10 Reports and Analytics
- Comprehensive reporting system with customizable parameters
- Real-time analytics dashboard data
- Performance metrics and engagement tracking

## Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy 2.0 with async support
- **Migration**: Alembic for database migrations
- **Validation**: Pydantic v2 for data validation
- **Task Queue**: Celery with Redis
- **Documentation**: Automatic OpenAPI/Swagger documentation

## Project Structure

```
app/
├── api/v1/
│   ├── endpoints/          # API endpoint definitions
│   └── api.py             # API router configuration
├── core/
│   ├── config.py          # Application configuration
│   └── database.py        # Database connection setup
├── models/                # SQLAlchemy database models
│   ├── progress.py        # Progress tracking models
│   ├── learning_path.py   # Learning path models
│   ├── assessment.py      # Assessment models
│   ├── target.py          # Target and reminder models
│   ├── schedule.py        # Scheduling models
│   ├── activity.py        # Activity models
│   ├── automation.py      # Automation models
│   ├── localization.py    # Localization models
│   └── analytics.py       # Analytics models
├── schemas/               # Pydantic schemas for validation
├── services/              # Business logic layer
└── __init__.py
migrations/                # Database migration files
main.py                   # FastAPI application entry point
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lms-learning-management
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database and configuration settings
```

5. **Set up PostgreSQL database**
```sql
CREATE DATABASE lms_learning;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE lms_learning TO postgres;
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the development server**
```bash
python main.py
# or
uvicorn main:app --reload
```

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints Overview

### Progress Tracking (`/api/v1/progress`)
- `POST /tracking` - Create progress tracking record
- `GET /tracking/{progress_id}` - Get progress by ID
- `GET /tracking/user/{user_id}` - Get user progress
- `PUT /tracking/{progress_id}` - Update progress
- `POST /assessments` - Create user assessment
- `POST /attendance` - Create attendance record

### Learning Paths (`/api/v1/learning-paths`)
- `POST /` - Create learning path
- `GET /{path_id}` - Get learning path details
- `POST /{path_id}/courses` - Add course to path
- `POST /enrollments` - Enroll user in path
- `POST /{path_id}/users/{user_id}/recommendations` - Get personalized recommendations

### Assessments (`/api/v1/assessments`)
- `POST /` - Create assessment
- `POST /{assessment_id}/questions` - Add questions
- `GET /{assessment_id}/results` - Get assessment results
- `POST /feedback` - Provide feedback

### Targets & Reminders (`/api/v1/targets`)
- `POST /` - Create target
- `GET /user/{user_id}` - Get user targets
- `POST /{target_id}/reminders` - Create reminder
- `GET /overdue` - Get overdue targets

### Additional endpoints for schedules, activities, automation, localization, and analytics...

## Database Schema

The system uses a comprehensive PostgreSQL schema with proper relationships:

- **Progress Tracking**: User progress, assessments, attendance
- **Learning Paths**: Adaptive learning with course sequences
- **Assessments**: Questions, answers, feedback
- **Targets**: Goals, deadlines, reminders  
- **Scheduling**: Course schedules, enrollments
- **Activities**: Reusable templates, course activities
- **Automation**: Rules, executions, logs
- **Localization**: Languages, translations
- **Analytics**: Metrics, reports, user data

## Configuration

Key configuration options in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/lms_learning
API_V1_STR=/api/v1
SECRET_KEY=your-super-secret-key
REDIS_URL=redis://localhost:6379/0
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=["en", "es", "fr", "de", "zh"]
```

## Integration with Main LMS

This backend is designed to integrate seamlessly with your main LMS system:

1. **Authentication**: Accepts user IDs from your auth system
2. **Course Integration**: References course/module IDs from your main system
3. **API-First**: RESTful APIs for easy integration
4. **Scalable Architecture**: Microservice-ready design
5. **Database Isolation**: Separate database that can be linked via foreign keys

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Generate new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black app/

# Lint code  
flake8 app/

# Type checking
mypy app/
```

## Production Deployment

1. **Environment Setup**
   - Use production PostgreSQL instance
   - Configure Redis for caching/tasks
   - Set secure SECRET_KEY
   - Enable HTTPS

2. **Database**
   - Run migrations: `alembic upgrade head`
   - Set up database backups
   - Configure connection pooling

3. **Application**
   - Use ASGI server like Gunicorn with Uvicorn workers
   - Configure reverse proxy (nginx)
   - Set up monitoring and logging
   - Configure CORS for your domain

4. **Security**
   - Use environment variables for secrets
   - Enable request validation
   - Set up rate limiting
   - Configure authentication integration

## Monitoring and Analytics

The system provides comprehensive analytics:

- **Performance Metrics**: Response times, throughput
- **User Analytics**: Progress, engagement, completion rates
- **System Metrics**: Database performance, error rates
- **Business Intelligence**: Learning outcomes, course effectiveness

## Support and Documentation

- **API Documentation**: Available at `/docs` endpoint
- **Database Schema**: Documented in model files
- **Configuration**: See `.env.example` for all options
- **Integration Guide**: Contact development team

## License

This project is proprietary software developed for LMS integration.# LMS_FEATURES_BACKEND
