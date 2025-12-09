import logging
from apps.courses.signals import publish_event

logger = logging.getLogger(__name__)

def lesson_created_handler(lesson_id: str, section_id: str, course_id: str):
    """Handler appelé quand une leçon est créée"""
    logger.info(f"Lesson created: {lesson_id} in section {section_id}")
    
    # Publier l'événement
    publish_event('lesson.created', {
        'lessonId': lesson_id,
        'sectionId': section_id,
        'courseId': course_id
    })
    
    # Mettre à jour les statistiques du cours
    from apps.courses.tasks import update_course_statistics
    update_course_statistics.delay(course_id)

def lesson_updated_handler(lesson_id: str, changes: dict, course_id: str):
    """Handler appelé quand une leçon est mise à jour"""
    logger.info(f"Lesson updated: {lesson_id}")
    
    # Publier l'événement
    publish_event('lesson.updated', {
        'lessonId': lesson_id,
        'changes': changes,
        'courseId': course_id
    })
    
    # Si la durée vidéo change, mettre à jour les stats
    if 'videoDuration' in changes:
        from apps.courses.tasks import update_course_statistics
        update_course_statistics.delay(course_id)

def lesson_deleted_handler(lesson_id: str, course_id: str):
    """Handler appelé quand une leçon est supprimée"""
    logger.info(f"Lesson deleted: {lesson_id}")
    
    # Publier l'événement
    publish_event('lesson.deleted', {
        'lessonId': lesson_id,
        'courseId': course_id
    })
    
    # Notifier enrollments-service pour nettoyer les progressions
    publish_event('lesson.requires_cleanup', {
        'lessonId': lesson_id
    })

def video_uploaded_handler(lesson_id: str, video_url: str):
    """Handler appelé quand une vidéo est uploadée"""
    logger.info(f"Video uploaded for lesson {lesson_id}")
    
    # Lancer le traitement vidéo asynchrone
    from .tasks import process_video_upload
    process_video_upload.delay(lesson_id, video_url)
    
    # Générer les sous-titres
    from .tasks import generate_lesson_subtitles
    generate_lesson_subtitles.delay(lesson_id, video_url)

def resource_added_handler(resource_id: str, lesson_id: str, resource_type: str):
    """Handler appelé quand une ressource est ajoutée"""
    logger.info(f"Resource added: {resource_id} to lesson {lesson_id}")
    
    # Publier l'événement
    publish_event('resource.added', {
        'resourceId': resource_id,
        'lessonId': lesson_id,
        'type': resource_type
    })
    
    # Synchroniser vers le CDN si nécessaire
    from apps.courses.lessons.tasks import sync_lesson_resources_to_cdn
    sync_lesson_resources_to_cdn.delay(lesson_id)

def resource_downloaded_handler(resource_id: str, user_id: str):
    """Handler appelé quand une ressource est téléchargée"""
    logger.info(f"Resource {resource_id} downloaded by user {user_id}")
    
    # Publier l'événement pour analytics
    publish_event('resource.downloaded', {
        'resourceId': resource_id,
        'userId': user_id
    })