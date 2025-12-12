from prisma import Prisma
from datetime import datetime
from typing import Optional, Dict, List
from apps.enrollments.exceptions import (
    EnrollmentNotFound,
    NoteNotFound,
    BookmarkNotFound,
    CertificateNotFound,
    InvalidVerificationCode
)


class NoteService:
    def __init__(self):
        self.db = Prisma()
    
    def __enter__(self):
        self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()
    
    def create_note(self, student_id: str, data: Dict) -> Dict:
        """Create a new note"""
        # Get enrollment
        enrollment = self.db.enrollment.find_first(
            where={
                'studentId': student_id,
                'courseId': data['courseId']
            }
        )
        
        if not enrollment:
            raise EnrollmentNotFound()
        
        # Create note
        note = self.db.note.create(
            data={
                'studentId': student_id,
                'courseId': data['courseId'],
                'lessonId': data['lessonId'],
                'enrollmentId': enrollment.id,
                'type': data.get('type', 'TEXT'),
                'content': data['content'],
                'highlight': data.get('highlight'),
                'timestamp': data.get('timestamp'),
                'pageNumber': data.get('pageNumber'),
                'isPrivate': data.get('isPrivate', True),
                'color': data.get('color')
            }
        )
        
        # Update progress notes count
        progress = self.db.progress.find_first(
            where={
                'studentId': student_id,
                'lessonId': data['lessonId']
            }
        )
        
        if progress:
            self.db.progress.update(
                where={'id': progress.id},
                data={'notesCount': progress.notesCount + 1}
            )
        
        return note
    
    def get_note(self, note_id: str, student_id: str) -> Dict:
        """Get note by ID"""
        note = self.db.note.find_first(
            where={
                'id': note_id,
                'studentId': student_id
            }
        )
        
        if not note:
            raise NoteNotFound()
        
        return note
    
    def get_notes(self, student_id: str, 
                  course_id: Optional[str] = None,
                  lesson_id: Optional[str] = None,
                  note_type: Optional[str] = None,
                  skip: int = 0,
                  take: int = 50) -> List[Dict]:
        """Get list of notes with filters"""
        where = {'studentId': student_id}
        
        if course_id:
            where['courseId'] = course_id
        if lesson_id:
            where['lessonId'] = lesson_id
        if note_type:
            where['type'] = note_type
        
        notes = self.db.note.find_many(
            where=where,
            skip=skip,
            take=take,
            order={'createdAt': 'desc'}
        )
        
        return notes
    
    def update_note(self, note_id: str, student_id: str, data: Dict) -> Dict:
        """Update note"""
        note = self.get_note(note_id, student_id)
        
        note = self.db.note.update(
            where={'id': note_id},
            data=data
        )
        
        return note
    
    def delete_note(self, note_id: str, student_id: str) -> bool:
        """Delete note"""
        note = self.get_note(note_id, student_id)
        
        # Update progress notes count
        progress = self.db.progress.find_first(
            where={
                'studentId': student_id,
                'lessonId': note.lessonId
            }
        )
        
        if progress and progress.notesCount > 0:
            self.db.progress.update(
                where={'id': progress.id},
                data={'notesCount': progress.notesCount - 1}
            )
        
        self.db.note.delete(where={'id': note_id})
        
        return True


class BookmarkService:
    def __init__(self):
        self.db = Prisma()
    
    def __enter__(self):
        self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()
    
    def create_bookmark(self, student_id: str, data: Dict) -> Dict:
        """Create a new bookmark"""
        # Get enrollment
        enrollment = self.db.enrollment.find_first(
            where={
                'studentId': student_id,
                'courseId': data['courseId']
            }
        )
        
        if not enrollment:
            raise EnrollmentNotFound()
        
        # Create bookmark
        bookmark = self.db.bookmark.create(
            data={
                'studentId': student_id,
                'courseId': data['courseId'],
                'lessonId': data['lessonId'],
                'enrollmentId': enrollment.id,
                'type': data.get('type', 'LESSON'),
                'title': data['title'],
                'description': data.get('description'),
                'timestamp': data.get('timestamp'),
                'url': data.get('url')
            }
        )
        
        return bookmark
    
    def get_bookmark(self, bookmark_id: str, student_id: str) -> Dict:
        """Get bookmark by ID"""
        bookmark = self.db.bookmark.find_first(
            where={
                'id': bookmark_id,
                'studentId': student_id
            }
        )
        
        if not bookmark:
            raise BookmarkNotFound()
        
        return bookmark
    
    def get_bookmarks(self, student_id: str,
                     course_id: Optional[str] = None,
                     lesson_id: Optional[str] = None,
                     bookmark_type: Optional[str] = None,
                     skip: int = 0,
                     take: int = 50) -> List[Dict]:
        """Get list of bookmarks with filters"""
        where = {'studentId': student_id}
        
        if course_id:
            where['courseId'] = course_id
        if lesson_id:
            where['lessonId'] = lesson_id
        if bookmark_type:
            where['type'] = bookmark_type
        
        bookmarks = self.db.bookmark.find_many(
            where=where,
            skip=skip,
            take=take,
            order={'createdAt': 'desc'}
        )
        
        return bookmarks
    
    def delete_bookmark(self, bookmark_id: str, student_id: str) -> bool:
        """Delete bookmark"""
        bookmark = self.get_bookmark(bookmark_id, student_id)
        
        self.db.bookmark.delete(where={'id': bookmark_id})
        
        return True


class CertificateService:
    def __init__(self):
        self.db = Prisma()
    
    def __enter__(self):
        self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()
    
    def get_certificate(self, certificate_id: str) -> Dict:
        """Get certificate by ID"""
        certificate = self.db.certificate.find_unique(
            where={'id': certificate_id}
        )
        
        if not certificate:
            raise CertificateNotFound()
        
        return certificate
    
    def get_student_certificates(self, student_id: str) -> List[Dict]:
        """Get all certificates for a student"""
        certificates = self.db.certificate.find_many(
            where={'studentId': student_id},
            order={'issueDate': 'desc'}
        )
        
        return certificates
    
    def verify_certificate(self, verification_code: str) -> Dict:
        """Verify certificate by verification code"""
        certificate = self.db.certificate.find_first(
            where={'verificationCode': verification_code}
        )
        
        if not certificate:
            return {
                'isValid': False,
                'certificate': None,
                'message': 'Certificate not found'
            }
        
        if not certificate.isValid:
            return {
                'isValid': False,
                'certificate': certificate,
                'message': f'Certificate has been revoked. Reason: {certificate.revokeReason or "Not specified"}'
            }
        
        return {
            'isValid': True,
            'certificate': certificate,
            'message': 'Certificate is valid'
        }
    
    def revoke_certificate(self, certificate_id: str, reason: str) -> Dict:
        """Revoke a certificate"""
        certificate = self.get_certificate(certificate_id)
        
        certificate = self.db.certificate.update(
            where={'id': certificate_id},
            data={
                'isValid': False,
                'revokedAt': datetime.now(),
                'revokeReason': reason
            }
        )
        
        return certificate
    
    def get_certificate_by_enrollment(self, enrollment_id: str) -> Optional[Dict]:
        """Get certificate for an enrollment"""
        certificate = self.db.certificate.find_first(
            where={'enrollmentId': enrollment_id}
        )
        
        return certificate