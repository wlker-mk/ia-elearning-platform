from prisma import Prisma
from datetime import datetime
from typing import Optional, Dict, List
from apps.enrollments.exceptions import (
    EnrollmentAlreadyExists,
    EnrollmentNotFound,
    EnrollmentExpired,
    EnrollmentSuspended,
    InsufficientProgress
)
from apps.enrollments.utils import (
    fetch_course_details,
    fetch_user_details,
    calculate_course_progress,
    check_enrollment_validity
)
from apps.enrollments.constants import MIN_COMPLETION_PERCENTAGE


class EnrollmentService:
    def __init__(self):
        self.db = Prisma()
    
    def __enter__(self):
        self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()
    
    def create_enrollment(self, student_id: str, data: Dict) -> Dict:
        """Create a new enrollment"""
        # Check if enrollment already exists
        existing = self.db.enrollment.find_first(
            where={
                'studentId': student_id,
                'courseId': data['courseId']
            }
        )
        
        if existing:
            raise EnrollmentAlreadyExists()
        
        # Create enrollment
        enrollment = self.db.enrollment.create(
            data={
                'studentId': student_id,
                'courseId': data['courseId'],
                'purchasePrice': data.get('purchasePrice'),
                'paymentId': data.get('paymentId'),
                'expiresAt': data.get('expiresAt'),
                'status': 'ACTIVE'
            }
        )
        
        return enrollment
    
    def get_enrollment(self, enrollment_id: str, student_id: Optional[str] = None) -> Dict:
        """Get enrollment by ID"""
        where = {'id': enrollment_id}
        if student_id:
            where['studentId'] = student_id
        
        enrollment = self.db.enrollment.find_unique(where=where)
        
        if not enrollment:
            raise EnrollmentNotFound()
        
        return enrollment
    
    def get_enrollments(self, student_id: Optional[str] = None, 
                       course_id: Optional[str] = None,
                       status: Optional[str] = None,
                       skip: int = 0, 
                       take: int = 20) -> List[Dict]:
        """Get list of enrollments with filters"""
        where = {}
        
        if student_id:
            where['studentId'] = student_id
        if course_id:
            where['courseId'] = course_id
        if status:
            where['status'] = status
        
        enrollments = self.db.enrollment.find_many(
            where=where,
            skip=skip,
            take=take,
            order={'createdAt': 'desc'}
        )
        
        return enrollments
    
    def update_enrollment(self, enrollment_id: str, student_id: str, data: Dict) -> Dict:
        """Update enrollment"""
        enrollment = self.get_enrollment(enrollment_id, student_id)
        
        enrollment = self.db.enrollment.update(
            where={'id': enrollment_id},
            data=data
        )
        
        return enrollment
    
    def cancel_enrollment(self, enrollment_id: str, student_id: str) -> Dict:
        """Cancel enrollment"""
        enrollment = self.get_enrollment(enrollment_id, student_id)
        
        enrollment = self.db.enrollment.update(
            where={'id': enrollment_id},
            data={
                'status': 'CANCELLED',
                'updatedAt': datetime.now()
            }
        )
        
        return enrollment
    
    def complete_enrollment(self, enrollment_id: str, student_id: str) -> Dict:
        """Complete enrollment and mark as finished"""
        enrollment = self.get_enrollment(enrollment_id, student_id)
        
        # Check validity
        is_valid, error_msg = check_enrollment_validity(enrollment)
        if not is_valid:
            if 'expired' in error_msg.lower():
                raise EnrollmentExpired()
            elif 'suspended' in error_msg.lower():
                raise EnrollmentSuspended()
        
        # Check progress
        progress = calculate_course_progress(enrollment_id)
        if progress < MIN_COMPLETION_PERCENTAGE:
            raise InsufficientProgress(
                f'Progress must be at least {MIN_COMPLETION_PERCENTAGE}% to complete. Current: {progress}%'
            )
        
        # Update enrollment
        enrollment = self.db.enrollment.update(
            where={'id': enrollment_id},
            data={
                'status': 'COMPLETED',
                'isCompleted': True,
                'completedAt': datetime.now(),
                'progress': 100.0,
                'updatedAt': datetime.now()
            }
        )
        
        # Trigger certificate generation (async)
        from .tasks import generate_certificate_task
        generate_certificate_task.delay(enrollment_id)
        
        return enrollment
    
    def get_enrollment_with_details(self, enrollment_id: str, student_id: str) -> Dict:
        """Get enrollment with related details"""
        enrollment = self.get_enrollment(enrollment_id, student_id)
        
        # Fetch course details
        course_details = fetch_course_details(enrollment.courseId)
        
        # Fetch student details
        student_details = fetch_user_details(enrollment.studentId)
        
        # Get progress stats
        progress_records = self.db.progress.find_many(
            where={'enrollmentId': enrollment_id}
        )
        
        completed_lessons = sum(1 for p in progress_records if p.isCompleted)
        
        progress_stats = {
            'totalLessons': len(progress_records),
            'completedLessons': completed_lessons,
            'averageScore': sum(p.quizScore or 0 for p in progress_records) / len(progress_records) if progress_records else 0,
            'totalTimeSpent': sum(p.timeSpent for p in progress_records)
        }
        
        # Get certificate if issued
        certificate = None
        if enrollment.certificateIssued:
            certificate = self.db.certificate.find_first(
                where={'enrollmentId': enrollment_id}
            )
        
        return {
            **enrollment.dict(),
            'courseDetails': course_details,
            'studentDetails': student_details,
            'progressStats': progress_stats,
            'certificateDetails': certificate.dict() if certificate else None
        }
    
    def get_student_stats(self, student_id: str) -> Dict:
        """Get enrollment statistics for a student"""
        enrollments = self.db.enrollment.find_many(
            where={'studentId': student_id}
        )
        
        active = [e for e in enrollments if e.status == 'ACTIVE']
        completed = [e for e in enrollments if e.status == 'COMPLETED']
        certificates = [e for e in enrollments if e.certificateIssued]
        
        total_time = sum(e.totalTimeSpent for e in enrollments)
        avg_progress = sum(e.progress for e in enrollments) / len(enrollments) if enrollments else 0
        
        return {
            'totalEnrollments': len(enrollments),
            'activeEnrollments': len(active),
            'completedEnrollments': len(completed),
            'totalTimeSpent': total_time,
            'averageProgress': round(avg_progress, 2),
            'certificatesEarned': len(certificates)
        }
    
    def update_last_access(self, enrollment_id: str):
        """Update last accessed timestamp"""
        self.db.enrollment.update(
            where={'id': enrollment_id},
            data={'lastAccessedAt': datetime.now()}
        )
    
    def update_total_time_spent(self, enrollment_id: str, additional_time: int):
        """Add time to total time spent"""
        enrollment = self.db.enrollment.find_unique(where={'id': enrollment_id})
        
        if enrollment:
            self.db.enrollment.update(
                where={'id': enrollment_id},
                data={
                    'totalTimeSpent': enrollment.totalTimeSpent + additional_time,
                    'lastAccessedAt': datetime.now()
                }
            )