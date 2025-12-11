import logging
import json
import pika
from django.conf import settings

    from .tasks import index_course_for_search
    from .tasks import sync_course_content_to_cdn
    from .tasks import update_course_statistics
    from .tasks import index_course_for_search
    from .tasks import update_course_statistics
    from .tasks import update_course_statistics
    from .tasks import update_course_statistics
    from .services import CoursesService
    import asyncio

    from .services import CoursesService
    import asyncio

    from .services import CoursesService
    import asyncio

    from .services import CoursesService
    import asyncio

from datetime import datetime
logger = logging.getLogger(__name__)

# ========== EVENT PUBLISHERS ==========

def publish_event(event_type: str, data: dict):
    """Publier un événement vers RabbitMQ"""
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.CELERY_BROKER_URL)
        )
        channel = connection.channel()

        # Déclarer l'exchange
        channel.exchange_declare(
            exchange='courses_events',
            exchange_type='topic',
            durable=True
        )

        # Publier le message
        channel.basic_publish(
            exchange='courses_events',
            routing_key=event_type,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistant
                content_type='application/json'
            )
        )

        connection.close()
        logger.info(f"Event published: {event_type}")

    except Exception as e:
        logger.error(f"Error publishing event {event_type}: {str(e)}")

# ========== EVENT HANDLERS ==========

def course_created_handler(course_id: str, instructor_id: str):
    """Handler appelé quand un cours est créé"""
    logger.info(f"Course created: {course_id} by instructor {instructor_id}")

    # Publier l'événement
    publish_event('course.created', {
        'courseId': course_id,
        'instructorId': instructor_id,
        'timestamp': datetime.utcnow().isoformat()
    })

    # Indexer pour la recherche
    index_course_for_search.delay(course_id)

def course_published_handler(course_id: str):
    """Handler appelé quand un cours est publié"""
    logger.info(f"Course published: {course_id}")

    # Publier l'événement
    publish_event('course.published', {
        'courseId': course_id,
        'timestamp': datetime.utcnow().isoformat()
    })

    # Synchroniser vers le CDN
    sync_course_content_to_cdn.delay(course_id)

    # Notifier les utilisateurs en wishlist
    publish_event('course.available', {
        'courseId': course_id
    })

def course_updated_handler(course_id: str, changes: dict):
    """Handler appelé quand un cours est mis à jour"""
    logger.info(f"Course updated: {course_id}")

    # Publier l'événement
    publish_event('course.updated', {
        'courseId': course_id,
        'changes': changes,
        'timestamp': datetime.utcnow().isoformat()
    })

    # Mettre à jour les statistiques
    update_course_statistics.delay(course_id)

    # Réindexer pour la recherche
    index_course_for_search.delay(course_id)

    # Si changements importants, notifier les étudiants inscrits
    important_fields = ['title', 'price', 'description']
    if any(field in changes for field in important_fields):
        publish_event('course.major_update', {
            'courseId': course_id,
            'changes': changes
        })

def course_deleted_handler(course_id: str):
    """Handler appelé quand un cours est supprimé"""
    logger.info(f"Course deleted: {course_id}")

    # Publier l'événement
    publish_event('course.deleted', {
        'courseId': course_id,
        'timestamp': datetime.utcnow().isoformat()
    })

def lesson_created_handler(lesson_id: str, course_id: str):
    """Handler appelé quand une leçon est créée"""
    logger.info(f"Lesson created: {lesson_id} in course {course_id}")

    # Mettre à jour les statistiques du cours
    update_course_statistics.delay(course_id)

    # Publier l'événement
    publish_event('lesson.created', {
        'lessonId': lesson_id,
        'courseId': course_id,
        'timestamp': datetime.utcnow().isoformat()
    })

def lesson_updated_handler(lesson_id: str, course_id: str):
    """Handler appelé quand une leçon est mise à jour"""
    logger.info(f"Lesson updated: {lesson_id}")

    # Mettre à jour les statistiques du cours
    update_course_statistics.delay(course_id)

def lesson_deleted_handler(lesson_id: str, course_id: str):
    """Handler appelé quand une leçon est supprimée"""
    logger.info(f"Lesson deleted: {lesson_id} from course {course_id}")

    # Mettre à jour les statistiques du cours
    update_course_statistics.delay(course_id)

    # Publier l'événement
    publish_event('lesson.deleted', {
        'lessonId': lesson_id,
        'courseId': course_id,
        'timestamp': datetime.utcnow().isoformat()
    })

def section_created_handler(section_id: str, course_id: str):
    """Handler appelé quand une section est créée"""
    logger.info(f"Section created: {section_id} in course {course_id}")

    publish_event('section.created', {
        'sectionId': section_id,
        'courseId': course_id,
        'timestamp': datetime.utcnow().isoformat()
    })

def resource_added_handler(resource_id: str, lesson_id: str):
    """Handler appelé quand une ressource est ajoutée"""
    logger.info(f"Resource added: {resource_id} to lesson {lesson_id}")

    # Synchroniser vers le CDN si nécessaire
    # sync_resource_to_cdn.delay(resource_id)

def wishlist_item_added_handler(user_id: str, course_id: str):
    """Handler appelé quand un cours est ajouté à une wishlist"""
    logger.info(f"User {user_id} added course {course_id} to wishlist")

    publish_event('wishlist.added', {
        'userId': user_id,
        'courseId': course_id,
        'timestamp': datetime.utcnow().isoformat()
    })

# ========== EVENT CONSUMERS ==========
# Ces handlers écoutent les événements des autres services

def handle_enrollment_created(message):
    """
    Écoute: enrollment.created (depuis enrollments-service)
    Action: Incrémenter enrollmentCount
    """
    data = json.loads(message.body)
    course_id = data.get('courseId')

    logger.info(f"Received enrollment.created for course {course_id}")

    # Appeler le service pour incrémenter le compteur
    async def _increment():
        service = CoursesService()
        await service.connect()
        try:
            await service.increment_enrollment_count(course_id)
        finally:
            await service.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_increment())
    loop.close()

def handle_enrollment_dropped(message):
    """
    Écoute: enrollment.dropped (depuis enrollments-service)
    Action: Décrémenter enrollmentCount
    """
    data = json.loads(message.body)
    course_id = data.get('courseId')

    logger.info(f"Received enrollment.dropped for course {course_id}")

    async def _decrement():
        service = CoursesService()
        await service.connect()
        try:
            await service.decrement_enrollment_count(course_id)
        finally:
            await service.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_decrement())
    loop.close()

def handle_course_completed(message):
    """
    Écoute: course.completed (depuis enrollments-service)
    Action: Incrémenter completionCount
    """
    data = json.loads(message.body)
    course_id = data.get('courseId')

    logger.info(f"Received course.completed for course {course_id}")

    async def _increment():
        service = CoursesService()
        await service.connect()
        try:
            await service.increment_completion_count(course_id)
        finally:
            await service.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_increment())
    loop.close()

def handle_review_created(message):
    """
    Écoute: review.created (depuis reviews-service)
    Action: Mettre à jour rating et reviewCount
    """
    data = json.loads(message.body)
    course_id = data.get('courseId')
    new_average_rating = data.get('newAverageRating')

    logger.info(f"Received review.created for course {course_id}")

    async def _update():
        service = CoursesService()
        await service.connect()
        try:
            await service.update_course_rating(course_id, new_average_rating)
        finally:
            await service.disconnect()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_update())
    loop.close()

# ========== RABBITMQ CONSUMER SETUP ==========

def start_event_consumers():
    """Démarrer les consumers RabbitMQ"""
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.CELERY_BROKER_URL)
        )
        channel = connection.channel()

        # Déclarer la queue
        channel.queue_declare(queue='courses_service_events', durable=True)

        # Binder aux événements des autres services
        events_to_listen = [
            'enrollment.created',
            'enrollment.dropped',
            'course.completed',
            'review.created'
        ]

        for event in events_to_listen:
            channel.queue_bind(
                exchange='platform_events',
                queue='courses_service_events',
                routing_key=event
            )

        # Mapper les événements aux handlers
        def callback(ch, method, properties, body):
            event_type = method.routing_key

            handlers = {
                'enrollment.created': handle_enrollment_created,
                'enrollment.dropped': handle_enrollment_dropped,
                'course.completed': handle_course_completed,
                'review.created': handle_review_created
            }

            handler = handlers.get(event_type)
            if handler:
                handler(type('Message', (), {'body': body})())

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue='courses_service_events',
            on_message_callback=callback
        )

        logger.info("Started consuming events from RabbitMQ")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Error starting event consumers: {str(e)}")

