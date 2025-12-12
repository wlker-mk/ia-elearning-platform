import pytest
from apps.quizzes.services import QuizzesService
from datetime import datetime
import uuid


@pytest.fixture
async def service():
    """Create and connect service instance"""
    svc = QuizzesService()
    await svc.connect()
    yield svc
    await svc.disconnect()


@pytest.fixture
def sample_quiz_data():
    """Sample quiz data"""
    return {
        'lesson_id': str(uuid.uuid4()),
        'course_id': str(uuid.uuid4()),
        'title': 'Test Quiz',
        'description': 'A test quiz',
        'duration': 30,
        'passing_score': 70.0,
        'max_attempts': 3,
        'randomize_questions': False,
    }


@pytest.fixture
def sample_question_data():
    """Sample question data"""
    return {
        'type': 'MULTIPLE_CHOICE',
        'question': 'What is 2 + 2?',
        'order': 1,
        'points': 1.0,
        'options': ['3', '4', '5', '6'],
        'correct_answer': 1,
        'explanation': 'Basic arithmetic',
    }


@pytest.mark.asyncio
async def test_create_quiz(service, sample_quiz_data):
    """Test creating a quiz"""
    quiz = await service.create_quiz(sample_quiz_data)
    
    assert quiz is not None
    assert quiz.title == sample_quiz_data['title']
    assert quiz.passingScore == sample_quiz_data['passing_score']


@pytest.mark.asyncio
async def test_get_quiz_by_id(service, sample_quiz_data):
    """Test retrieving a quiz by ID"""
    created_quiz = await service.create_quiz(sample_quiz_data)
    retrieved_quiz = await service.get_quiz_by_id(created_quiz.id)
    
    assert retrieved_quiz is not None
    assert retrieved_quiz.id == created_quiz.id
    assert retrieved_quiz.title == created_quiz.title


@pytest.mark.asyncio
async def test_update_quiz(service, sample_quiz_data):
    """Test updating a quiz"""
    quiz = await service.create_quiz(sample_quiz_data)
    
    update_data = {'title': 'Updated Test Quiz', 'passing_score': 80.0}
    updated_quiz = await service.update_quiz(quiz.id, update_data)
    
    assert updated_quiz.title == 'Updated Test Quiz'
    assert updated_quiz.passingScore == 80.0


@pytest.mark.asyncio
async def test_delete_quiz(service, sample_quiz_data):
    """Test deleting a quiz"""
    quiz = await service.create_quiz(sample_quiz_data)
    result = await service.delete_quiz(quiz.id)
    
    assert result is True
    
    deleted_quiz = await service.get_quiz_by_id(quiz.id)
    assert deleted_quiz is None


@pytest.mark.asyncio
async def test_create_question(service, sample_quiz_data, sample_question_data):
    """Test creating a question"""
    quiz = await service.create_quiz(sample_quiz_data)
    question = await service.create_question(quiz.id, sample_question_data)
    
    assert question is not None
    assert question.quizId == quiz.id
    assert question.question == sample_question_data['question']


@pytest.mark.asyncio
async def test_get_questions_by_quiz(service, sample_quiz_data, sample_question_data):
    """Test getting all questions for a quiz"""
    quiz = await service.create_quiz(sample_quiz_data)
    
    # Create multiple questions
    for i in range(3):
        question_data = sample_question_data.copy()
        question_data['order'] = i + 1
        await service.create_question(quiz.id, question_data)
    
    questions = await service.get_questions_by_quiz(quiz.id)
    
    assert len(questions) == 3
    assert questions[0].order == 1


@pytest.mark.asyncio
async def test_start_quiz_attempt(service, sample_quiz_data):
    """Test starting a quiz attempt"""
    quiz = await service.create_quiz(sample_quiz_data)
    student_id = str(uuid.uuid4())
    
    attempt = await service.start_quiz_attempt(quiz.id, student_id)
    
    assert attempt is not None
    assert attempt.quizId == quiz.id
    assert attempt.studentId == student_id
    assert attempt.attemptNumber == 1


@pytest.mark.asyncio
async def test_max_attempts_limit(service, sample_quiz_data):
    """Test that max attempts limit is enforced"""
    quiz = await service.create_quiz(sample_quiz_data)
    student_id = str(uuid.uuid4())
    
    # Create max attempts
    for i in range(quiz.maxAttempts):
        await service.start_quiz_attempt(quiz.id, student_id)
    
    # Try to create one more - should fail
    with pytest.raises(ValueError, match="Maximum attempts"):
        await service.start_quiz_attempt(quiz.id, student_id)


@pytest.mark.asyncio
async def test_submit_quiz_attempt(service, sample_quiz_data, sample_question_data):
    """Test submitting a quiz attempt"""
    # Create quiz with questions
    quiz = await service.create_quiz(sample_quiz_data)
    question = await service.create_question(quiz.id, sample_question_data)
    
    # Start attempt
    student_id = str(uuid.uuid4())
    attempt = await service.start_quiz_attempt(quiz.id, student_id)
    
    # Submit answers
    answers = {question.id: 1}  # Correct answer
    submitted = await service.submit_quiz_attempt(attempt.id, answers)
    
    assert submitted.submittedAt is not None
    assert submitted.score > 0
    assert submitted.percentage == 100.0
    assert submitted.isPassed is True


@pytest.mark.asyncio
async def test_check_answer_multiple_choice(service):
    """Test answer checking for multiple choice"""
    question = {
        'type': 'MULTIPLE_CHOICE',
        'correctAnswer': 2
    }
    
    assert service._check_answer(question, 2) is True
    assert service._check_answer(question, 1) is False


@pytest.mark.asyncio
async def test_check_answer_true_false(service):
    """Test answer checking for true/false"""
    question = {
        'type': 'TRUE_FALSE',
        'correctAnswer': 0
    }
    
    assert service._check_answer(question, 0) is True
    assert service._check_answer(question, 1) is False


@pytest.mark.asyncio
async def test_check_answer_short_answer(service):
    """Test answer checking for short answer"""
    question = {
        'type': 'SHORT_ANSWER',
        'correctAnswer': 'python'
    }
    
    assert service._check_answer(question, 'python') is True
    assert service._check_answer(question, 'Python') is True  # Case insensitive
    assert service._check_answer(question, '  python  ') is True  # Strips whitespace
    assert service._check_answer(question, 'java') is False


@pytest.mark.asyncio
async def test_create_proctoring_session(service, sample_quiz_data):
    """Test creating a proctoring session"""
    quiz = await service.create_quiz(sample_quiz_data)
    student_id = str(uuid.uuid4())
    attempt = await service.start_quiz_attempt(quiz.id, student_id)
    
    session = await service.create_proctoring_session(attempt.id)
    
    assert session is not None
    assert session.quizAttemptId == attempt.id


@pytest.mark.asyncio
async def test_record_proctoring_event(service, sample_quiz_data):
    """Test recording proctoring events"""
    quiz = await service.create_quiz(sample_quiz_data)
    student_id = str(uuid.uuid4())
    attempt = await service.start_quiz_attempt(quiz.id, student_id)
    
    # Record tab switch event
    session = await service.record_proctoring_event(
        attempt.id, 
        'tab_switch',
        {'timestamp': datetime.now().isoformat()}
    )
    
    assert session.tabSwitches == 1


@pytest.mark.asyncio
async def test_flagging_for_review(service, sample_quiz_data):
    """Test that sessions are flagged for suspicious activity"""
    quiz = await service.create_quiz(sample_quiz_data)
    student_id = str(uuid.uuid4())
    attempt = await service.start_quiz_attempt(quiz.id, student_id)
    
    # Record multiple tab switches
    for i in range(4):
        await service.record_proctoring_event(attempt.id, 'tab_switch')
    
    # Get the session
    from prisma import Prisma
    db = Prisma()
    await db.connect()
    session = await db.proctoringsession.find_unique(
        where={'quizAttemptId': attempt.id}
    )
    await db.disconnect()
    
    assert session.flaggedForReview is True


@pytest.mark.asyncio
async def test_quiz_statistics(service, sample_quiz_data, sample_question_data):
    """Test calculating quiz statistics"""
    # Create quiz with question
    quiz = await service.create_quiz(sample_quiz_data)
    question = await service.create_question(quiz.id, sample_question_data)
    
    # Create multiple attempts
    for i in range(3):
        student_id = str(uuid.uuid4())
        attempt = await service.start_quiz_attempt(quiz.id, student_id)
        
        # Submit with different scores
        answers = {question.id: 1 if i == 0 else 0}
        await service.submit_quiz_attempt(attempt.id, answers)
    
    # Get statistics
    stats = await service.get_quiz_statistics(quiz.id)
    
    assert stats['total_attempts'] == 3  # nosec
    assert stats['quiz_id'] == quiz.id  # nosec
    assert 'average_score' in stats  # nosec
    assert 'pass_rate' in stats  # nosec


@pytest.mark.asyncio
async def test_get_student_attempts(service, sample_quiz_data):
    """Test getting student's attempts"""
    quiz = await service.create_quiz(sample_quiz_data)
    student_id = str(uuid.uuid4())
    
    # Create multiple attempts
    for i in range(2):
        await service.start_quiz_attempt(quiz.id, student_id)
    
    attempts = await service.get_student_attempts(quiz.id, student_id)
    
    assert len(attempts) == 2
    assert all(a.studentId == student_id for a in attempts)