from celery import shared_task
import logging
from .services import CertificatesService
import asyncio
from datetime import datetime
import os

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
def generate_certificate_pdf(certificate_id: str):
    """Générer le PDF d'un certificat"""
    logger.info(f"Generating PDF for certificate {certificate_id}")
    
    service = CertificatesService()
    
    async def _generate():
        await service.connect()
        try:
            # Récupérer le certificat
            certificate = await service.get_certificate_by_id(certificate_id)
            
            if not certificate:
                logger.error(f"Certificate {certificate_id} not found")
                return False
            
            # Récupérer le cours
            from apps.courses.courses.services import CoursesService
            courses_service = CoursesService()
            await courses_service.connect()
            
            course = await courses_service.get_course_by_id(
                certificate['courseId']
            )
            
            await courses_service.disconnect()
            
            if not course:
                logger.error(f"Course not found for certificate {certificate_id}")
                return False
            
            # Récupérer le template
            template = await service.get_default_template()
            
            if not template:
                logger.error("No default template found")
                return False
            
            # Préparer les données pour le template
            template_data = {
                'certificate_number': certificate['certificateNumber'],
                'student_name': 'Student Name',  # À récupérer du user-service
                'course_title': course['title'],
                'completion_date': certificate['completionDate'].strftime('%B %d, %Y'),
                'issue_date': certificate['issuedAt'].strftime('%B %d, %Y'),
                'grade': certificate.get('grade', 'Pass'),
                'instructor_name': 'Instructor Name',  # À récupérer du user-service
                'verification_url': certificate['verificationUrl'],
                'course_duration': f"{course['estimatedDuration'] // 3600} hours"
            }
            
            # Générer le HTML
            html_content = template['templateHtml']
            css_content = template.get('templateCss', '')
            
            # Remplacer les placeholders
            for key, value in template_data.items():
                html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
            
            # Générer le PDF avec WeasyPrint
            try:
                from weasyprint import HTML, CSS
                from io import BytesIO
                
                pdf_buffer = BytesIO()
                HTML(string=html_content).write_pdf(
                    pdf_buffer,
                    stylesheets=[CSS(string=css_content)] if css_content else []
                )
                
                # Upload vers le stockage cloud
                pdf_url = upload_to_storage(
                    pdf_buffer.getvalue(),
                    f"certificates/{certificate['certificateNumber']}.pdf"
                )
                
                # Mettre à jour le certificat
                await service.update_certificate_pdf(certificate_id, pdf_url)
                
                logger.info(f"PDF generated: {pdf_url}")
                
                # Envoyer l'email
                send_certificate_email.delay(certificate_id)
                
                return True
                
            except ImportError:
                logger.warning("WeasyPrint not installed, using mock PDF generation")
                # Mock pour développement
                mock_url = f"https://cdn.platform.com/certificates/{certificate['certificateNumber']}.pdf"
                await service.update_certificate_pdf(certificate_id, mock_url)
                return True
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return False
        finally:
            await service.disconnect()
    
    return run_async(_generate())

def upload_to_storage(file_content: bytes, file_path: str) -> str:
    """Upload un fichier vers le stockage cloud"""
    try:
        # Exemple avec boto3 pour S3:
        # import boto3
        # s3 = boto3.client('s3')
        # bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
        # s3.put_object(
        #     Bucket=bucket,
        #     Key=file_path,
        #     Body=file_content,
        #     ContentType='application/pdf',
        #     ACL='public-read'
        # )
        # return f"https://{bucket}.s3.amazonaws.com/{file_path}"
        
        # Mock pour développement
        return f"https://cdn.platform.com/{file_path}"
    
    except Exception as e:
        logger.error(f"Error uploading to storage: {str(e)}")
        raise

@shared_task
def send_certificate_email(certificate_id: str):
    """Envoyer l'email avec le certificat"""
    logger.info(f"Sending certificate email for {certificate_id}")
    
    service = CertificatesService()
    
    async def _send():
        await service.connect()
        try:
            certificate = await service.get_certificate_by_id(certificate_id)
            
            if not certificate:
                return False
            
            # Publier un événement pour le notifications-service
            from apps.courses.courses.signals import publish_event
            publish_event('certificate.ready', {
                'certificateId': certificate_id,
                'userId': certificate['userId'],
                'certificateNumber': certificate['certificateNumber'],
                'pdfUrl': certificate.get('pdfUrl')
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending certificate email: {str(e)}")
            return False
        finally:
            await service.disconnect()
    
    return run_async(_send())

@shared_task
def check_expired_certificates():
    """Vérifier et notifier les certificats expirés"""
    logger.info("Checking for expired or expiring certificates")
    
    # Logique pour:
    # - Identifier les certificats qui expirent dans 30 jours
    # - Notifier les utilisateurs
    # - Proposer le renouvellement
    
    return True

@shared_task
def generate_certificate_analytics():
    """Générer les analytics des certificats"""
    logger.info("Generating certificate analytics")
    
    service = CertificatesService()
    
    async def _analytics():
        await service.connect()
        try:
            # Récupérer les statistiques globales
            stats = await service.get_certificate_statistics()
            
            # Stocker dans Redis pour un accès rapide
            # ou dans une DB analytics
            
            logger.info(f"Analytics generated: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return None
        finally:
            await service.disconnect()
    
    return run_async(_analytics())

@shared_task
def cleanup_old_certificate_verifications():
    """Nettoyer les anciennes vérifications (> 1 an)"""
    logger.info("Cleaning up old certificate verifications")
    
    # Supprimer les logs de vérification de plus d'1 an
    # pour respecter le RGPD et libérer de l'espace
    
    return True

@shared_task
def generate_certificate_for_completed_course(user_id: str, course_id: str):
    """
    Générer automatiquement un certificat quand un cours est complété
    (appelé par enrollments-service via événement RabbitMQ)
    """
    logger.info(f"Auto-generating certificate for user {user_id}, course {course_id}")
    
    service = CertificatesService()
    
    async def _generate():
        await service.connect()
        try:
            # Vérifier si un certificat existe déjà
            existing = await service.db.certificate.find_first(
                where={
                    'userId': user_id,
                    'courseId': course_id
                }
            )
            
            if existing:
                logger.info("Certificate already exists")
                return existing
            
            # Générer le certificat
            certificate = await service.generate_certificate(
                user_id=user_id,
                course_id=course_id,
                completion_date=datetime.utcnow()
            )
            
            logger.info(f"Certificate generated: {certificate['certificateNumber']}")
            return certificate
            
        except Exception as e:
            logger.error(f"Error generating certificate: {str(e)}")
            return None
        finally:
            await service.disconnect()
    
    return run_async(_generate())

@shared_task
def regenerate_certificate_pdf(certificate_id: str, template_id: str = None):
    """Régénérer le PDF d'un certificat avec un nouveau template"""
    logger.info(f"Regenerating PDF for certificate {certificate_id}")
    
    # Similaire à generate_certificate_pdf mais avec template spécifique
    # Utile pour mettre à jour le design de certificats déjà émis
    
    return generate_certificate_pdf(certificate_id)

@shared_task
def validate_certificate_templates():
    """Valider tous les templates de certificats"""
    logger.info("Validating certificate templates")
    
    service = CertificatesService()
    
    async def _validate():
        await service.connect()
        try:
            templates = await service.list_templates(active_only=False)
            
            results = []
            for template in templates:
                errors = []
                
                # Vérifier la présence des placeholders requis
                required_placeholders = [
                    'certificate_number',
                    'student_name',
                    'course_title',
                    'completion_date'
                ]
                
                for placeholder in required_placeholders:
                    if f"{{{{{placeholder}}}}}" not in template['templateHtml']:
                        errors.append(f"Missing placeholder: {placeholder}")
                
                results.append({
                    'templateId': template['id'],
                    'name': template['name'],
                    'valid': len(errors) == 0,
                    'errors': errors
                })
            
            logger.info(f"Template validation completed: {len(results)} templates")
            return results
            
        except Exception as e:
            logger.error(f"Error validating templates: {str(e)}")
            return []
        finally:
            await service.disconnect()
    
    return run_async(_validate())