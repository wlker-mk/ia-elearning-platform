from prisma import Prisma
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from apps.enrollments.exceptions import (
    EnrollmentNotFound,
    ProgressNotFound
)


class ProgressService:
    def __init__(self):
        self.db = Prisma()
    
    def __enter__(self):
        self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()
    
    def create_or_update_progress(self, student_id: str, data: Dict) -> Dict:
        """Create or update progress for a lesson"""
        # Get enrollment
        enrollment = self.db.enrollment.find_first(
            where={
                'studentId': student_id,
                'courseId': data['courseId']
            }
        )
        
        if not enrollment:
            raise EnrollmentNotFound()
        
        # Check if progress exists
        existing_progress = self.db.progress.find_first(
            where={
                'studentId': student_id,
                'lessonId': data['lessonId']
            }
        )
        
        progress_data = {
            'percentage': data.get('percentage', 0),
            'timeSpent': data.get('timeSpent', 0),
            'lastPosition': data.get('lastPosition'),
            'watchedDuration': data.get('watchedDuration', 0),
            'quizScore': data.get('quizScore'),
            'lastAccessedAt': datetime.now(),
        }
        
        # Check if lesson is completed
        if data.get('isCompleted') or progress_data.get('percentage', 0) >= 100:
            progress_data['isCompleted'] = True
            progress_data['completedAt'] = datetime.now()
            progress_data['percentage'] = 100
        
        if existing_progress:
            # Update existing progress
            progress = self.db.progress.update(
                where={'id': existing_progress.id},
                data=progress_data
            )
        else:
            # Create new progress
            progress = self.db.progress.create(
                data={
                    **progress_data,
                    'studentId': student_id,
                    'lessonId': data['lessonId'],
                    'courseId': data['courseId'],
                    'enrollmentId': enrollment.id,
                }
            )
        
        # Update enrollment progress and time
        self._update_enrollment_progress(enrollment.id)
        
        return progress
    
    def get_progress(self, progress_id: str, student_id: str) -> Dict:
        """Get progress by ID"""
        progress = self.db.progress.find_first(
            where={
                'id': progress_id,
                'studentId': student_id
            }
        )
        
        if not progress:
            raise ProgressNotFound()
        
        return progress
    
    def get_course_progress(self, student_id: str, course_id: str) -> Dict:
        """Get all progress for a course"""
        # Get enrollment
        enrollment = self.db.enrollment.find_first(
            where={
                'studentId': student_id,
                'courseId': course_id
            }
        )
        
        if not enrollment:
            raise EnrollmentNotFound()
        
        # Get all progress records
        progress_records = self.db.progress.find_many(
            where={
                'studentId': student_id,
                'courseId': course_id
            },
            order={'lastAccessedAt': 'desc'}
        )
        
        # Calculate stats
        total_lessons = len(progress_records)
        completed_lessons = sum(1 for p in progress_records if p.isCompleted)
        total_time = sum(p.timeSpent for p in progress_records)
        overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        last_accessed = max(
            (p.lastAccessedAt for p in progress_records),
            default=None
        )
        
        return {
            'courseId': course_id,
            'totalLessons': total_lessons,
            'completedLessons': completed_lessons,
            'overallProgress': round(overall_progress, 2),
            'totalTimeSpent': total_time,
            'lastAccessedAt': last_accessed,
            'lessons': progress_records
        }
    
    def get_student_progress_stats(self, student_id: str) -> Dict:
        """Get overall progress statistics for a student"""
        # Get all enrollments
        enrollments = self.db.enrollment.find_many(
            where={'studentId': student_id}
        )
        
        # Get all progress records
        all_progress = self.db.progress.find_many(
            where={'studentId': student_id}
        )
        
        in_progress = [e for e in enrollments if e.status == 'IN_PROGRESS' or e.status == 'ACTIVE']
        completed_lessons = sum(1 for p in all_progress if p.isCompleted)
        total_time = sum(p.timeSpent for p in all_progress)
        avg_progress = sum(p.percentage for p in all_progress) / len(all_progress) if all_progress else 0
        
        # Calculate streaks
        current_streak, longest_streak = self._calculate_streaks(student_id)
        
        return {
            'totalCoursesInProgress': len(in_progress),
            'totalLessonsCompleted': completed_lessons,
            'totalTimeSpent': total_time,
            'averageProgress': round(avg_progress, 2),
            'currentStreak': current_streak,
            'longestStreak': longest_streak
        }
    
    def _update_enrollment_progress(self, enrollment_id: str):
        """Update enrollment's overall progress"""
        progress_records = self.db.progress.find_many(
            where={'enrollmentId': enrollment_id}
        )
        
        if not progress_records:
            return
        
        # Calculate overall progress
        total_percentage = sum(p.percentage for p in progress_records)
        overall_progress = total_percentage / len(progress_records)
        
        # Calculate total time
        total_time = sum(p.timeSpent for p in progress_records)
        
        # Update enrollment
        self.db.enrollment.update(
            where={'id': enrollment_id},
            data={
                'progress': round(overall_progress, 2),
                'totalTimeSpent': total_time,
                'lastAccessedAt': datetime.now()
            }
        )
    
    def _calculate_streaks(self, student_id: str) -> tuple:
        """Calculate current and longest learning streaks"""
        # Get study sessions ordered by date
        sessions = self.db.studysession.find_many(
            where={'studentId': student_id},
            order={'startTime': 'desc'}
        )
        
        if not sessions:
            return 0, 0
        
        # Group sessions by day
        days_active = set()
        for session in sessions:
            day = session.startTime.date()
            days_active.add(day)
        
        sorted_days = sorted(days_active, reverse=True)
        
        # Calculate current streak
        current_streak = 0
        today = datetime.now().date()
        
        for i, day in enumerate(sorted_days):
            expected_day = today - timedelta(days=i)
            if day == expected_day:
                current_streak += 1
            else:
                break
        
        # Calculate longest streak
        longest_streak = 1
        current_count = 1
        
        for i in range(1, len(sorted_days)):
            diff = (sorted_days[i-1] - sorted_days[i]).days
            if diff == 1:
                current_count += 1
                longest_streak = max(longest_streak, current_count)
            else:
                current_count = 1
        
        return current_streak, longest_streak


class StudySessionService:
    def __init__(self):
        self.db = Prisma()
    
    def __enter__(self):
        self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()
    
    def start_session(self, student_id: str, data: Dict, ip_address: str = None) -> Dict:
        """Start a new study session"""
        # Get enrollment
        enrollment = self.db.enrollment.find_first(
            where={
                'studentId': student_id,
                'courseId': data['courseId']
            }
        )
        
        if not enrollment:
            raise EnrollmentNotFound()
        
        # End any active sessions for this student
        self.db.studysession.update_many(
            where={
                'studentId': student_id,
                'isActive': True
            },
            data={
                'isActive': False,
                'endTime': datetime.now(),
                'duration': 0  # Will be calculated
            }
        )
        
        # Create new session
        session = self.db.studysession.create(
            data={
                'studentId': student_id,
                'courseId': data['courseId'],
                'lessonId': data.get('lessonId'),
                'enrollmentId': enrollment.id,
                'deviceInfo': data.get('deviceInfo'),
                'ipAddress': ip_address,
                'isActive': True
            }
        )
        
        return session
    
    def end_session(self, session_id: str, student_id: str) -> Dict:
        """End a study session"""
        session = self.db.studysession.find_first(
            where={
                'id': session_id,
                'studentId': student_id
            }
        )
        
        if not session:
            raise ProgressNotFound('Study session not found')
        
        # Calculate duration
        duration = int((datetime.now() - session.startTime).total_seconds())
        
        # Update session
        session = self.db.studysession.update(
            where={'id': session_id},
            data={
                'endTime': datetime.now(),
                'duration': duration,
                'isActive': False
            }
        )
        
        # Update enrollment time
        enrollment = self.db.enrollment.find_unique(
            where={'id': session.enrollmentId}
        )
        
        if enrollment:
            self.db.enrollment.update(
                where={'id': enrollment.id},
                data={
                    'totalTimeSpent': enrollment.totalTimeSpent + duration
                }
            )
        
        return session
    
    def get_active_session(self, student_id: str, course_id: str) -> Optional[Dict]:
        """Get active session for a student"""
        session = self.db.studysession.find_first(
            where={
                'studentId': student_id,
                'courseId': course_id,
                'isActive': True
            }
        )
        
        return session