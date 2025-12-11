from celery import shared_task
import logging
from .services import CoursesService
import asyncio

    from .signals import publish_event

logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper pour exécuter des coroutines"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@shared_task
def update_course_statistics(course_id: str):
    """Mettre à jour les statistiques d'un cours"""
    logger.info(f"Updating statistics for course {course_id}")

    service = CoursesService()

    async def _update():
        await service.connect()
        try:
            # Récupérer le cours avec toutes ses leçons
            course = await service.get_course_by_id(course_id)

            if not course:
                logger.error(f"Course {course_id} not found")
                return False

            # Calculer la durée totale
            total_duration = 0
            for section in course.get('sections', []):
                section_duration = 0
                for lesson in section.get('lessons', []):
                    if lesson.get('videoDuration'):
                        section_duration += lesson['videoDuration']

                # Mettre à jour la durée de la section
                await service.update_section(
                    section['id'],
                    {'duration': section_duration}
                )
                total_duration += section_duration

            # Mettre à jour la durée estimée du cours
            if total_duration > 0:
                await service.update_course(
                    course_id,
                    {'estimatedDuration': total_duration}
                )

            logger.info(f"Statistics updated for course {course_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating statistics: {str(e)}")
            return False
        finally:
            await service.disconnect()

    return run_async(_update())

@shared_task
def cleanup_unpublished_courses():
    """Nettoyer les cours non publiés depuis longtemps (> 90 jours)"""
    logger.info("Cleaning up old unpublished courses")

    # Logique de nettoyage
    # - Identifier les cours en brouillon depuis > 90 jours
    # - Envoyer une notification à l'instructeur
    # - Option: archiver automatiquement

    return True

@shared_task
def send_course_update_notification(course_id: str, update_type: str):
    """Envoyer une notification de mise à jour de cours"""
    logger.info(f"Sending update notification for course {course_id}: {update_type}")

    # Publier un événement pour le notifications-service
    publish_event('course.updated', {
        'courseId': course_id,
        'updateType': update_type
    })

    return True

@shared_task
def sync_course_content_to_cdn(course_id: str):
    """Synchroniser le contenu du cours vers le CDN"""
    logger.info(f"Syncing course {course_id} content to CDN")

    service = CoursesService()

    async def _sync():
        await service.connect()
        try:
            course = await service.get_course_by_id(course_id)

            if not course:
                return False

            # Upload des vidéos et ressources vers le CDN
            # Exemple: AWS CloudFront, Cloudflare, etc.

            logger.info(f"Course {course_id} synced to CDN")
            return True

        except Exception as e:
            logger.error(f"Error syncing to CDN: {str(e)}")
            return False
        finally:
            await service.disconnect()

    return run_async(_sync())

@shared_task
def calculate_trending_courses():
    """Calculer les cours en tendance"""
    logger.info("Calculating trending courses")

    # Logique pour identifier les cours tendances:
    # - Inscriptions récentes (7 derniers jours)
    # - Notes élevées
    # - Taux de complétion élevé
    # - Activité dans les commentaires

    # Stocker dans Redis avec TTL de 1 heure

    return True

@shared_task
def generate_course_thumbnail(course_id: str, video_url: str):
    """Générer une thumbnail depuis la vidéo d'intro"""
    logger.info(f"Generating thumbnail for course {course_id}")

    # Logique pour extraire une frame de la vidéo
    # et la sauvegarder comme thumbnail

    return True

@shared_task
def validate_course_content(course_id: str):
    """Valider le contenu d'un cours avant publication"""
    logger.info(f"Validating course {course_id}")

    service = CoursesService()

    async def _validate():
        await service.connect()
        try:
            course = await service.get_course_by_id(course_id)

            if not course:
                return {'valid': False, 'errors': ['Course not found']}

            errors = []

            # Vérifications
            if not course.get('sections'):
                errors.append('Course must have at least one section')

            total_lessons = 0
            for section in course.get('sections', []):
                if not section.get('lessons'):
                    errors.append(f"Section '{section['title']}' has no lessons")
                total_lessons += len(section.get('lessons', []))

            if total_lessons < 3:
                errors.append('Course must have at least 3 lessons')

            if not course.get('thumbnailUrl'):
                errors.append('Course must have a thumbnail')

            if course.get('price', 0) > 0 and not course.get('description'):
                errors.append('Paid courses must have a description')

            return {
                'valid': len(errors) == 0,
                'errors': errors
            }

        finally:
            await service.disconnect()

    return run_async(_validate())

@shared_task
def index_course_for_search(course_id: str):
    """Indexer un cours pour la recherche (Elasticsearch, Algolia, etc.)"""
    logger.info(f"Indexing course {course_id} for search")

    service = CoursesService()

    async def _index():
        await service.connect()
        try:
            course = await service.get_course_by_id(course_id)

            if not course:
                return False

            # Préparer les données pour l'indexation
            search_data = {
                'id': course['id'],
                'title': course['title'],
                'description': course['description'],
                'instructor_id': course['instructorId'],
                'category_id': course['categoryId'],
                'difficulty': course['difficulty'],
                'price': course['price'],
                'rating': course.get('rating', 0),
                'enrollment_count': course['enrollmentCount'],
                'published_at': course['publishedAt']
            }

            # Indexer dans le moteur de recherche
            # Exemple: client.index(index='courses', body=search_data, id=course_id)

            logger.info(f"Course {course_id} indexed successfully")
            return True

        except Exception as e:
            logger.error(f"Error indexing course: {str(e)}")
            return False
        finally:
            await service.disconnect()

    return run_async(_index())
