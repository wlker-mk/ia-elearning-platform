#!/usr/bin/env python
"""
Seed script for quizzes-service
"""
import asyncio
from prisma import Prisma
from datetime import datetime, timedelta
import uuid

async def main():
    db = Prisma()
    await db.connect()
    
    print(f"🌱 Seeding quizzes-service...")
    
    try:
        # Sample course and lesson IDs
        course_id = str(uuid.uuid4())
        lesson_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        
        # Create sample quizzes
        quiz1 = await db.quiz.create(
            data={
                'lessonId': lesson_id,
                'courseId': course_id,
                'title': 'Introduction to Python',
                'description': 'Test your basic Python knowledge',
                'duration': 30,
                'passingScore': 70.0,
                'maxAttempts': 3,
                'randomizeQuestions': False,
            }
        )
        print(f"✅ Created quiz: {quiz1.title}")
        
        # Create questions for quiz1
        questions_data = [
            {
                'quizId': quiz1.id,
                'type': 'MULTIPLE_CHOICE',
                'question': 'What is the correct syntax to output "Hello World" in Python?',
                'order': 1,
                'points': 1.0,
                'options': [
                    'echo("Hello World")',
                    'print("Hello World")',
                    'printf("Hello World")',
                    'console.log("Hello World")'
                ],
                'correctAnswer': 1,
                'explanation': 'In Python, we use the print() function to output text.'
            },
            {
                'quizId': quiz1.id,
                'type': 'TRUE_FALSE',
                'question': 'Python is a case-sensitive language.',
                'order': 2,
                'points': 1.0,
                'options': ['True', 'False'],
                'correctAnswer': 0,
                'explanation': 'Python is case-sensitive, meaning "variable" and "Variable" are different.'
            },
            {
                'quizId': quiz1.id,
                'type': 'SHORT_ANSWER',
                'question': 'What keyword is used to define a function in Python?',
                'order': 3,
                'points': 1.0,
                'correctAnswer': 'def',
                'explanation': 'The "def" keyword is used to define functions in Python.'
            },
            {
                'quizId': quiz1.id,
                'type': 'MULTIPLE_CHOICE',
                'question': 'Which of the following is a mutable data type in Python?',
                'order': 4,
                'points': 1.0,
                'options': ['tuple', 'string', 'list', 'int'],
                'correctAnswer': 2,
                'explanation': 'Lists are mutable in Python, meaning they can be modified after creation.'
            },
        ]
        
        for q_data in questions_data:
            await db.question.create(data=q_data)
        
        print(f"✅ Created {len(questions_data)} questions for quiz: {quiz1.title}")
        
        # Create another quiz
        quiz2 = await db.quiz.create(
            data={
                'lessonId': lesson_id,
                'courseId': course_id,
                'title': 'Advanced JavaScript Concepts',
                'description': 'Test your knowledge of advanced JavaScript',
                'duration': 45,
                'passingScore': 75.0,
                'maxAttempts': 2,
                'randomizeQuestions': True,
            }
        )
        print(f"✅ Created quiz: {quiz2.title}")
        
        # Create questions for quiz2
        questions_data2 = [
            {
                'quizId': quiz2.id,
                'type': 'MULTIPLE_CHOICE',
                'question': 'What is closure in JavaScript?',
                'order': 1,
                'points': 2.0,
                'options': [
                    'A way to close browser windows',
                    'A function that has access to variables in its outer scope',
                    'A method to close database connections',
                    'A CSS property'
                ],
                'correctAnswer': 1,
                'explanation': 'Closures allow functions to access variables from their outer lexical scope.'
            },
            {
                'quizId': quiz2.id,
                'type': 'CODING',
                'question': 'Write a function that returns the sum of two numbers.',
                'order': 2,
                'points': 3.0,
                'correctAnswer': 'function sum(a, b) { return a + b; }',
                'explanation': 'This requires manual grading.'
            },
        ]
        
        for q_data in questions_data2:
            await db.question.create(data=q_data)
        
        print(f"✅ Created {len(questions_data2)} questions for quiz: {quiz2.title}")
        
        # Create sample quiz attempt
        attempt = await db.quizattempt.create(
            data={
                'quizId': quiz1.id,
                'studentId': student_id,
                'attemptNumber': 1,
                'score': 3.0,
                'percentage': 75.0,
                'isPassed': True,
                'answers': {
                    'question_1': 1,
                    'question_2': 0,
                    'question_3': 'def',
                    'question_4': 2
                },
                'startedAt': datetime.now() - timedelta(minutes=25),
                'submittedAt': datetime.now(),
                'timeSpent': 1500,  # 25 minutes in seconds
            }
        )
        print(f"✅ Created quiz attempt for student")
        
        # Create proctoring session
        proctoring = await db.proctoringsession.create(
            data={
                'quizAttemptId': attempt.id,
                'tabSwitches': 2,
                'multipleFaces': False,
                'noFaceDetected': False,
                'copyPasteDetected': False,
                'flaggedForReview': False,
                'startedAt': datetime.now() - timedelta(minutes=25),
                'endedAt': datetime.now(),
            }
        )
        print(f"✅ Created proctoring session")
        
        # Create a flagged attempt
        attempt2 = await db.quizattempt.create(
            data={
                'quizId': quiz1.id,
                'studentId': str(uuid.uuid4()),
                'attemptNumber': 1,
                'score': 4.0,
                'percentage': 100.0,
                'isPassed': True,
                'answers': {
                    'question_1': 1,
                    'question_2': 0,
                    'question_3': 'def',
                    'question_4': 2
                },
                'startedAt': datetime.now() - timedelta(minutes=5),
                'submittedAt': datetime.now(),
                'timeSpent': 300,  # Only 5 minutes
            }
        )
        
        proctoring2 = await db.proctoringsession.create(
            data={
                'quizAttemptId': attempt2.id,
                'tabSwitches': 8,
                'multipleFaces': True,
                'noFaceDetected': False,
                'copyPasteDetected': True,
                'flaggedForReview': True,
                'suspiciousActivity': [
                    {
                        'type': 'tab_switch',
                        'timestamp': datetime.now().isoformat(),
                        'count': 8
                    },
                    {
                        'type': 'multiple_faces',
                        'timestamp': datetime.now().isoformat(),
                        'details': 'Multiple people detected'
                    }
                ],
                'startedAt': datetime.now() - timedelta(minutes=5),
                'endedAt': datetime.now(),
            }
        )
        print(f"✅ Created flagged proctoring session")
        
        print("\n📊 Seed Summary:")
        print(f"   - Quizzes created: 2")
        print(f"   - Questions created: {len(questions_data) + len(questions_data2)}")
        print(f"   - Quiz attempts: 2")
        print(f"   - Proctoring sessions: 2 (1 flagged)")
        print("\n✅ Seed completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())