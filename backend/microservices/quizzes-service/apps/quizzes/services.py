from typing import List, Optional, Dict, Any
from prisma import Prisma
from datetime import datetime
import random


class QuizzesService:
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        await self.db.connect()
    
    async def disconnect(self):
        await self.db.disconnect()
    
    # Quiz CRUD Operations
    async def create_quiz(self, quiz_data: Dict[str, Any], questions_data: List[Dict[str, Any]] = None) -> Dict:
        """Create a new quiz with optional questions"""
        quiz = await self.db.quiz.create(
            data={
                'lessonId': quiz_data['lesson_id'],
                'courseId': quiz_data['course_id'],
                'title': quiz_data['title'],
                'description': quiz_data.get('description'),
                'duration': quiz_data.get('duration'),
                'passingScore': quiz_data.get('passing_score', 70),
                'maxAttempts': quiz_data.get('max_attempts', 3),
                'randomizeQuestions': quiz_data.get('randomize_questions', False),
            }
        )
        
        if questions_data:
            for question in questions_data:
                await self.create_question(quiz.id, question)
        
        return await self.get_quiz_by_id(quiz.id)
    
    async def get_quiz_by_id(self, quiz_id: str, include_questions: bool = True) -> Optional[Dict]:
        """Get quiz by ID with optional questions"""
        quiz = await self.db.quiz.find_unique(
            where={'id': quiz_id},
            include={'questions': True} if include_questions else None
        )
        return quiz
    
    async def get_quizzes_by_lesson(self, lesson_id: str) -> List[Dict]:
        """Get all quizzes for a lesson"""
        quizzes = await self.db.quiz.find_many(
            where={'lessonId': lesson_id},
            include={'questions': True}
        )
        return quizzes
    
    async def get_quizzes_by_course(self, course_id: str) -> List[Dict]:
        """Get all quizzes for a course"""
        quizzes = await self.db.quiz.find_many(
            where={'courseId': course_id},
            include={'questions': True}
        )
        return quizzes
    
    async def update_quiz(self, quiz_id: str, quiz_data: Dict[str, Any]) -> Dict:
        """Update quiz details"""
        update_data = {}
        if 'title' in quiz_data:
            update_data['title'] = quiz_data['title']
        if 'description' in quiz_data:
            update_data['description'] = quiz_data['description']
        if 'duration' in quiz_data:
            update_data['duration'] = quiz_data['duration']
        if 'passing_score' in quiz_data:
            update_data['passingScore'] = quiz_data['passing_score']
        if 'max_attempts' in quiz_data:
            update_data['maxAttempts'] = quiz_data['max_attempts']
        if 'randomize_questions' in quiz_data:
            update_data['randomizeQuestions'] = quiz_data['randomize_questions']
        
        quiz = await self.db.quiz.update(
            where={'id': quiz_id},
            data=update_data
        )
        return await self.get_quiz_by_id(quiz_id)
    
    async def delete_quiz(self, quiz_id: str) -> bool:
        """Delete a quiz and its questions"""
        await self.db.question.delete_many(where={'quizId': quiz_id})
        await self.db.quiz.delete(where={'id': quiz_id})
        return True
    
    # Question Operations
    async def create_question(self, quiz_id: str, question_data: Dict[str, Any]) -> Dict:
        """Create a question for a quiz"""
        question = await self.db.question.create(
            data={
                'quizId': quiz_id,
                'type': question_data['type'],
                'question': question_data['question'],
                'order': question_data['order'],
                'points': question_data.get('points', 1.0),
                'options': question_data.get('options'),
                'correctAnswer': question_data.get('correct_answer'),
                'explanation': question_data.get('explanation'),
            }
        )
        return question
    
    async def update_question(self, question_id: str, question_data: Dict[str, Any]) -> Dict:
        """Update a question"""
        update_data = {}
        if 'type' in question_data:
            update_data['type'] = question_data['type']
        if 'question' in question_data:
            update_data['question'] = question_data['question']
        if 'order' in question_data:
            update_data['order'] = question_data['order']
        if 'points' in question_data:
            update_data['points'] = question_data['points']
        if 'options' in question_data:
            update_data['options'] = question_data['options']
        if 'correct_answer' in question_data:
            update_data['correctAnswer'] = question_data['correct_answer']
        if 'explanation' in question_data:
            update_data['explanation'] = question_data['explanation']
        
        question = await self.db.question.update(
            where={'id': question_id},
            data=update_data
        )
        return question
    
    async def delete_question(self, question_id: str) -> bool:
        """Delete a question"""
        await self.db.question.delete(where={'id': question_id})
        return True
    
    async def get_questions_by_quiz(self, quiz_id: str, randomize: bool = False) -> List[Dict]:
        """Get all questions for a quiz"""
        questions = await self.db.question.find_many(
            where={'quizId': quiz_id},
            order={'order': 'asc'}
        )
        
        if randomize:
            random.shuffle(questions)
        
        return questions
    
    # Quiz Attempt Operations
    async def start_quiz_attempt(self, quiz_id: str, student_id: str) -> Dict:
        """Start a new quiz attempt"""
        # Check previous attempts
        attempts = await self.db.quizattempt.find_many(
            where={
                'quizId': quiz_id,
                'studentId': student_id
            }
        )
        
        quiz = await self.get_quiz_by_id(quiz_id, include_questions=False)
        
        if len(attempts) >= quiz.maxAttempts:
            raise ValueError(f"Maximum attempts ({quiz.maxAttempts}) reached")
        
        attempt = await self.db.quizattempt.create(
            data={
                'quizId': quiz_id,
                'studentId': student_id,
                'attemptNumber': len(attempts) + 1,
                'score': 0.0,
                'percentage': 0.0,
                'isPassed': False,
                'answers': {},
                'startedAt': datetime.now(),
            }
        )
        return attempt
    
    async def submit_quiz_attempt(self, attempt_id: str, answers: Dict[str, Any]) -> Dict:
        """Submit and grade a quiz attempt"""
        attempt = await self.db.quizattempt.find_unique(where={'id': attempt_id})
        
        if not attempt:
            raise ValueError("Attempt not found")
        
        if attempt.submittedAt:
            raise ValueError("Attempt already submitted")
        
        # Get questions with correct answers
        questions = await self.db.question.find_many(
            where={'quizId': attempt.quizId}
        )
        
        # Calculate score
        total_points = sum(q.points for q in questions)
        earned_points = 0.0
        
        for question in questions:
            question_id = question.id
            if question_id in answers:
                if self._check_answer(question, answers[question_id]):
                    earned_points += question.points
        
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        
        # Get quiz to check passing score
        quiz = await self.get_quiz_by_id(attempt.quizId, include_questions=False)
        is_passed = percentage >= quiz.passingScore
        
        # Calculate time spent
        time_spent = int((datetime.now() - attempt.startedAt).total_seconds())
        
        # Update attempt
        updated_attempt = await self.db.quizattempt.update(
            where={'id': attempt_id},
            data={
                'answers': answers,
                'score': earned_points,
                'percentage': percentage,
                'isPassed': is_passed,
                'submittedAt': datetime.now(),
                'timeSpent': time_spent,
            }
        )
        
        return updated_attempt
    
    def _check_answer(self, question: Dict, user_answer: Any) -> bool:
        """Check if user answer is correct"""
        correct_answer = question.correctAnswer
        
        if question.type == 'MULTIPLE_CHOICE':
            return user_answer == correct_answer
        elif question.type == 'TRUE_FALSE':
            return user_answer == correct_answer
        elif question.type == 'SHORT_ANSWER':
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
        elif question.type == 'MATCHING':
            return user_answer == correct_answer
        elif question.type == 'FILL_BLANK':
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
        else:
            # For ESSAY and CODING, manual grading required
            return False
    
    async def get_student_attempts(self, quiz_id: str, student_id: str) -> List[Dict]:
        """Get all attempts for a student on a quiz"""
        attempts = await self.db.quizattempt.find_many(
            where={
                'quizId': quiz_id,
                'studentId': student_id
            },
            order={'attemptNumber': 'asc'}
        )
        return attempts
    
    async def get_quiz_attempts(self, quiz_id: str) -> List[Dict]:
        """Get all attempts for a quiz"""
        attempts = await self.db.quizattempt.find_many(
            where={'quizId': quiz_id},
            order={'createdAt': 'desc'}
        )
        return attempts
    
    # Proctoring Operations
    async def create_proctoring_session(self, quiz_attempt_id: str) -> Dict:
        """Create a proctoring session for a quiz attempt"""
        session = await self.db.proctoringsession.create(
            data={
                'quizAttemptId': quiz_attempt_id,
                'startedAt': datetime.now(),
            }
        )
        return session
    
    async def update_proctoring_session(self, session_id: str, session_data: Dict[str, Any]) -> Dict:
        """Update proctoring session data"""
        update_data = {}
        
        if 'webcam_url' in session_data:
            update_data['webcamUrl'] = session_data['webcam_url']
        if 'screen_url' in session_data:
            update_data['screenUrl'] = session_data['screen_url']
        if 'audio_url' in session_data:
            update_data['audioUrl'] = session_data['audio_url']
        if 'face_detections' in session_data:
            update_data['faceDetections'] = session_data['face_detections']
        if 'suspicious_activity' in session_data:
            update_data['suspiciousActivity'] = session_data['suspicious_activity']
        if 'tab_switches' in session_data:
            update_data['tabSwitches'] = session_data['tab_switches']
        if 'multiple_faces' in session_data:
            update_data['multipleFaces'] = session_data['multiple_faces']
        if 'no_face_detected' in session_data:
            update_data['noFaceDetected'] = session_data['no_face_detected']
        if 'copy_paste_detected' in session_data:
            update_data['copyPasteDetected'] = session_data['copy_paste_detected']
        if 'flagged_for_review' in session_data:
            update_data['flaggedForReview'] = session_data['flagged_for_review']
        if 'ended_at' in session_data:
            update_data['endedAt'] = session_data['ended_at']
        
        session = await self.db.proctoringsession.update(
            where={'id': session_id},
            data=update_data
        )
        return session
    
    async def record_proctoring_event(self, quiz_attempt_id: str, event_type: str, details: Dict = None) -> Dict:
        """Record a proctoring event"""
        session = await self.db.proctoringsession.find_unique(
            where={'quizAttemptId': quiz_attempt_id}
        )
        
        if not session:
            session = await self.create_proctoring_session(quiz_attempt_id)
        
        update_data = {}
        
        if event_type == 'tab_switch':
            update_data['tabSwitches'] = session.tabSwitches + 1
            if session.tabSwitches + 1 > 3:
                update_data['flaggedForReview'] = True
        elif event_type == 'multiple_faces':
            update_data['multipleFaces'] = True
            update_data['flaggedForReview'] = True
        elif event_type == 'no_face':
            update_data['noFaceDetected'] = True
            update_data['flaggedForReview'] = True
        elif event_type == 'copy_paste':
            update_data['copyPasteDetected'] = True
            update_data['flaggedForReview'] = True
        
        # Update suspicious activity log
        suspicious_activities = session.suspiciousActivity or []
        suspicious_activities.append({
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        })
        update_data['suspiciousActivity'] = suspicious_activities
        
        return await self.update_proctoring_session(session.id, update_data)
    
    async def get_flagged_sessions(self) -> List[Dict]:
        """Get all proctoring sessions flagged for review"""
        sessions = await self.db.proctoringsession.find_many(
            where={'flaggedForReview': True},
            order={'startedAt': 'desc'}
        )
        return sessions
    
    async def review_proctoring_session(self, session_id: str, reviewer_id: str, notes: str) -> Dict:
        """Mark a proctoring session as reviewed"""
        session = await self.db.proctoringsession.update(
            where={'id': session_id},
            data={
                'reviewedBy': reviewer_id,
                'reviewedAt': datetime.now(),
                'reviewNotes': notes,
            }
        )
        return session
    
    # Statistics and Analytics
    async def get_quiz_statistics(self, quiz_id: str) -> Dict:
        """Get statistics for a quiz"""
        attempts = await self.db.quizattempt.find_many(
            where={'quizId': quiz_id}
        )
        
        if not attempts:
            return {
                'quiz_id': quiz_id,
                'total_attempts': 0,
                'average_score': 0,
                'pass_rate': 0,
                'average_time_spent': 0,
            }
        
        total_attempts = len(attempts)
        average_score = sum(a.percentage for a in attempts) / total_attempts
        passed_attempts = sum(1 for a in attempts if a.isPassed)
        pass_rate = (passed_attempts / total_attempts) * 100
        
        completed_attempts = [a for a in attempts if a.timeSpent]
        average_time_spent = sum(a.timeSpent for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0
        
        return {
            'quiz_id': quiz_id,
            'total_attempts': total_attempts,
            'average_score': round(average_score, 2),
            'pass_rate': round(pass_rate, 2),
            'average_time_spent': int(average_time_spent),
        }