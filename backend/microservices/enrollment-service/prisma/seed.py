"""
Seed script for development data
"""
from prisma import Prisma
from datetime import datetime, timedelta
import random

db = Prisma()
db.connect()

def seed_enrollments():
    """Seed sample enrollments"""
    
    # Sample student IDs (replace with actual IDs from your users service)
    student_ids = [
        'student-uuid-1',
        'student-uuid-2',
        'student-uuid-3',
    ]
    
    # Sample course IDs (replace with actual IDs from your courses service)
    course_ids = [
        'course-uuid-1',
        'course-uuid-2',
        'course-uuid-3',
    ]
    
    print("Seeding enrollments...")
    
    for student_id in student_ids:
        for course_id in course_ids[:2]:  # Enroll each student in 2 courses
            enrollment = db.enrollment.create(
                data={
                    'studentId': student_id,
                    'courseId': course_id,
                    'status': random.choice(['ACTIVE', 'IN_PROGRESS', 'COMPLETED']),
                    'progress': random.uniform(0, 100),
                    'purchasePrice': random.uniform(29.99, 199.99),
                    'enrolledAt': datetime.now() - timedelta(days=random.randint(1, 90)),
                }
            )
            
            # Create some progress records
            seed_progress(enrollment.id, student_id, course_id)
            
            # Create some notes
            seed_notes(enrollment.id, student_id, course_id)
    
    print("✓ Enrollments seeded successfully")


def seed_progress(enrollment_id, student_id, course_id):
    """Seed progress records for an enrollment"""
    
    # Sample lesson IDs
    lesson_ids = [
        f'{course_id}-lesson-1',
        f'{course_id}-lesson-2',
        f'{course_id}-lesson-3',
    ]
    
    for lesson_id in lesson_ids:
        db.progress.create(
            data={
                'studentId': student_id,
                'lessonId': lesson_id,
                'courseId': course_id,
                'enrollmentId': enrollment_id,
                'isCompleted': random.choice([True, False]),
                'percentage': random.uniform(0, 100),
                'timeSpent': random.randint(300, 3600),
                'watchedDuration': random.randint(200, 3000),
                'quizScore': random.uniform(60, 100) if random.random() > 0.3 else None,
            }
        )


def seed_notes(enrollment_id, student_id, course_id):
    """Seed notes for an enrollment"""
    
    lesson_ids = [
        f'{course_id}-lesson-1',
        f'{course_id}-lesson-2',
    ]
    
    note_types = ['TEXT', 'HIGHLIGHT', 'QUESTION']
    
    for lesson_id in lesson_ids:
        for _ in range(random.randint(1, 3)):
            db.note.create(
                data={
                    'studentId': student_id,
                    'courseId': course_id,
                    'lessonId': lesson_id,
                    'enrollmentId': enrollment_id,
                    'type': random.choice(note_types),
                    'content': f'Sample note content for {lesson_id}',
                    'timestamp': random.randint(0, 1800) if random.random() > 0.5 else None,
                }
            )


def seed_study_sessions():
    """Seed study sessions"""
    
    print("Seeding study sessions...")
    
    enrollments = db.enrollment.find_many()
    
    for enrollment in enrollments:
        for _ in range(random.randint(3, 10)):
            start_time = datetime.now() - timedelta(days=random.randint(0, 30))
            duration = random.randint(600, 7200)  # 10 min to 2 hours
            
            db.studysession.create(
                data={
                    'studentId': enrollment.studentId,
                    'courseId': enrollment.courseId,
                    'enrollmentId': enrollment.id,
                    'startTime': start_time,
                    'endTime': start_time + timedelta(seconds=duration),
                    'duration': duration,
                    'isActive': False,
                }
            )
    
    print("✓ Study sessions seeded successfully")


def seed_certificates():
    """Seed certificates for completed enrollments"""
    
    print("Seeding certificates...")
    
    completed_enrollments = db.enrollment.find_many(
        where={'status': 'COMPLETED'}
    )
    
    for enrollment in completed_enrollments:
        if not enrollment.certificateIssued:
            db.certificate.create(
                data={
                    'studentId': enrollment.studentId,
                    'courseId': enrollment.courseId,
                    'enrollmentId': enrollment.id,
                    'certificateNumber': f'CERT-{enrollment.id[:8].upper()}',
                    'verificationCode': f'VER-{enrollment.id[:12].upper()}',
                    'studentName': 'Sample Student',
                    'studentEmail': 'student@example.com',
                    'courseTitle': 'Sample Course',
                    'completionDate': datetime.now(),
                    'score': random.uniform(80, 100),
                    'grade': random.choice(['A+', 'A', 'B+']),
                    'isValid': True,
                }
            )
            
            # Update enrollment
            db.enrollment.update(
                where={'id': enrollment.id},
                data={'certificateIssued': True}
            )
    
    print("✓ Certificates seeded successfully")


def main():
    """Main seed function"""
    try:
        print("Starting database seeding...")
        print("=" * 50)
        
        seed_enrollments()
        seed_study_sessions()
        seed_certificates()
        
        print("=" * 50)
        print("✓ Database seeded successfully!")
        
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
    finally:
        db.disconnect()


if __name__ == '__main__':
    main()