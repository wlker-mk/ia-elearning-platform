from typing import List, Optional, Dict, Any
from prisma import Prisma
from datetime import datetime, timedelta
import hashlib
import secrets

class CertificatesService:
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        await self.db.connect()
    
    async def disconnect(self):
        await self.db.disconnect()
    
    def _generate_certificate_number(
        self,
        user_id: str,
        course_id: str
    ) -> str:
        """Générer un numéro de certificat unique et sécurisé"""
        # Format: CERT-YYYYMM-XXXXX
        now = datetime.utcnow()
        prefix = f"CERT-{now.strftime('%Y%m')}"
        
        # Créer un hash sécurisé et unique
        data = f"{user_id}{course_id}{now.isoformat()}{secrets.token_hex(8)}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()[:10].upper()
        
        return f"{prefix}-{hash_value}"
    
    # ========== CERTIFICATES ==========
    
    async def generate_certificate(
        self,
        user_id: str,
        course_id: str,
        completion_date: datetime,
        grade: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Générer un certificat"""
        # Vérifier si un certificat existe déjà
        existing = await self.db.certificate.find_first(
            where={
                'userId': user_id,
                'courseId': course_id
            }
        )
        
        if existing:
            return existing
        
        # Générer le numéro unique
        cert_number = self._generate_certificate_number(user_id, course_id)
        
        # Créer le certificat
        certificate = await self.db.certificate.create(
            data={
                'userId': user_id,
                'courseId': course_id,
                'certificateNumber': cert_number,
                'issuedAt': datetime.utcnow(),
                'completionDate': completion_date,
                'grade': grade,
                'metadata': metadata or {},
                'verificationUrl': f"https://platform.com/verify/{cert_number}"
            }
        )
        
        # Lancer la génération du PDF en tâche asynchrone
        from .tasks import generate_certificate_pdf
        generate_certificate_pdf.delay(certificate['id'])
        
        # Publier un événement
        from apps.courses.courses.signals import publish_event
        publish_event('certificate.issued', {
            'certificateId': certificate['id'],
            'userId': user_id,
            'courseId': course_id,
            'certificateNumber': cert_number
        })
        
        return certificate
    
    async def get_certificate_by_id(self, certificate_id: str) -> Optional[Dict]:
        """Récupérer un certificat par ID"""
        certificate = await self.db.certificate.find_unique(
            where={'id': certificate_id}
        )
        return certificate
    
    async def get_certificate_by_number(
        self,
        certificate_number: str
    ) -> Optional[Dict]:
        """Récupérer un certificat par numéro"""
        certificate = await self.db.certificate.find_unique(
            where={'certificateNumber': certificate_number}
        )
        return certificate
    
    async def get_user_certificates(self, user_id: str) -> List[Dict]:
        """Récupérer tous les certificats d'un utilisateur"""
        certificates = await self.db.certificate.find_many(
            where={'userId': user_id},
            order_by={'issuedAt': 'desc'}
        )
        
        # Enrichir avec les infos de cours
        for cert in certificates:
            course = await self.db.course.find_unique(
                where={'id': cert['courseId']}
            )
            cert['course'] = course
        
        return certificates
    
    async def get_course_certificates(self, course_id: str) -> List[Dict]:
        """Récupérer tous les certificats d'un cours"""
        certificates = await self.db.certificate.find_many(
            where={'courseId': course_id},
            order_by={'issuedAt': 'desc'}
        )
        return certificates
    
    async def verify_certificate(
        self,
        certificate_number: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        """Vérifier un certificat"""
        certificate = await self.get_certificate_by_number(certificate_number)
        
        if not certificate:
            return {
                'certificateNumber': certificate_number,
                'isValid': False,
                'message': 'Certificate not found',
                'verifiedAt': datetime.utcnow()
            }
        
        # Vérifier l'expiration
        if certificate.get('expiresAt'):
            if certificate['expiresAt'] < datetime.utcnow():
                return {
                    'certificateNumber': certificate_number,
                    'isValid': False,
                    'certificate': certificate,
                    'message': 'Certificate has expired',
                    'verifiedAt': datetime.utcnow()
                }
        
        # Vérifier si révoqué
        if certificate.get('metadata', {}).get('revoked'):
            return {
                'certificateNumber': certificate_number,
                'isValid': False,
                'certificate': certificate,
                'message': 'Certificate has been revoked',
                'verifiedAt': datetime.utcnow()
            }
        
        # Logger la vérification
        await self.db.certificateverification.create(
            data={
                'certificateId': certificate['id'],
                'verifiedAt': datetime.utcnow(),
                'ipAddress': ip_address,
                'userAgent': user_agent
            }
        )
        
        # Enrichir avec les infos
        course = await self.db.course.find_unique(
            where={'id': certificate['courseId']}
        )
        certificate['course'] = course
        
        return {
            'certificateNumber': certificate_number,
            'isValid': True,
            'certificate': certificate,
            'message': 'Certificate is valid',
            'verifiedAt': datetime.utcnow()
        }
    
    async def update_certificate_pdf(
        self,
        certificate_id: str,
        pdf_url: str
    ) -> Dict:
        """Mettre à jour l'URL du PDF"""
        certificate = await self.db.certificate.update(
            where={'id': certificate_id},
            data={'pdfUrl': pdf_url}
        )
        return certificate
    
    async def revoke_certificate(
        self,
        certificate_id: str,
        reason: Optional[str] = None
    ) -> Dict:
        """Révoquer un certificat"""
        certificate = await self.db.certificate.update(
            where={'id': certificate_id},
            data={
                'expiresAt': datetime.utcnow(),
                'metadata': {
                    'revoked': True,
                    'revokedAt': datetime.utcnow().isoformat(),
                    'revokeReason': reason
                }
            }
        )
        
        # Publier un événement
        from apps.courses.courses.signals import publish_event
        publish_event('certificate.revoked', {
            'certificateId': certificate_id,
            'reason': reason
        })
        
        return certificate
    
    async def renew_certificate(
        self,
        certificate_id: str,
        new_expiry_date: Optional[datetime] = None
    ) -> Dict:
        """Renouveler un certificat"""
        certificate = await self.db.certificate.update(
            where={'id': certificate_id},
            data={'expiresAt': new_expiry_date}
        )
        return certificate
    
    # ========== TEMPLATES ==========
    
    async def create_template(self, data: Dict[str, Any]) -> Dict:
        """Créer un template"""
        template = await self.db.certificatetemplate.create(
            data={
                'name': data['name'],
                'description': data.get('description'),
                'templateHtml': data['templateHtml'],
                'templateCss': data.get('templateCss'),
                'isDefault': data.get('isDefault', False),
                'isActive': data.get('isActive', True)
            }
        )
        
        # Si défini comme template par défaut, désactiver les autres
        if template['isDefault']:
            await self.db.certificatetemplate.update_many(
                where={
                    'id': {'not': template['id']},
                    'isDefault': True
                },
                data={'isDefault': False}
            )
        
        return template
    
    async def get_template(self, template_id: str) -> Optional[Dict]:
        """Récupérer un template"""
        template = await self.db.certificatetemplate.find_unique(
            where={'id': template_id}
        )
        return template
    
    async def get_default_template(self) -> Optional[Dict]:
        """Récupérer le template par défaut"""
        template = await self.db.certificatetemplate.find_first(
            where={
                'isDefault': True,
                'isActive': True
            }
        )
        
        # Si pas de template par défaut, prendre le premier actif
        if not template:
            template = await self.db.certificatetemplate.find_first(
                where={'isActive': True}
            )
        
        return template
    
    async def list_templates(self, active_only: bool = True) -> List[Dict]:
        """Lister les templates"""
        where = {}
        if active_only:
            where['isActive'] = True
        
        templates = await self.db.certificatetemplate.find_many(
            where=where,
            order_by={'createdAt': 'desc'}
        )
        return templates
    
    async def update_template(
        self,
        template_id: str,
        data: Dict[str, Any]
    ) -> Dict:
        """Mettre à jour un template"""
        template = await self.db.certificatetemplate.update(
            where={'id': template_id},
            data=data
        )
        
        # Si devenu template par défaut
        if data.get('isDefault'):
            await self.db.certificatetemplate.update_many(
                where={
                    'id': {'not': template_id},
                    'isDefault': True
                },
                data={'isDefault': False}
            )
        
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """Supprimer un template"""
        # Vérifier qu'il n'est pas le template par défaut
        template = await self.get_template(template_id)
        if template and template['isDefault']:
            raise ValueError('Cannot delete default template')
        
        await self.db.certificatetemplate.delete(
            where={'id': template_id}
        )
        return True
    
    # ========== STATISTICS ==========
    
    async def get_certificate_statistics(
        self,
        course_id: Optional[str] = None,
        instructor_id: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """Récupérer les statistiques"""
        where = {}
        
        if course_id:
            where['courseId'] = course_id
        elif instructor_id:
            # Récupérer les cours de l'instructeur
            courses = await self.db.course.find_many(
                where={'instructorId': instructor_id}
            )
            course_ids = [c['id'] for c in courses]
            where['courseId'] = {'in': course_ids}
        
        # Total émis
        total_issued = await self.db.certificate.count(where=where)
        
        # Vérifications
        if where:
            certs = await self.db.certificate.find_many(where=where)
            cert_ids = [c['id'] for c in certs]
            total_verifications = await self.db.certificateverification.count(
                where={'certificateId': {'in': cert_ids}}
            )
        else:
            total_verifications = await self.db.certificateverification.count()
        
        # Période récente
        now = datetime.utcnow()
        
        # Ce mois
        month_start = datetime(now.year, now.month, 1)
        issued_this_month = await self.db.certificate.count(
            where={**where, 'issuedAt': {'gte': month_start}}
        )
        
        # Cette semaine
        week_start = now - timedelta(days=now.weekday())
        week_start = datetime(week_start.year, week_start.month, week_start.day)
        issued_this_week = await self.db.certificate.count(
            where={**where, 'issuedAt': {'gte': week_start}}
        )
        
        # Aujourd'hui
        today_start = datetime(now.year, now.month, now.day)
        issued_today = await self.db.certificate.count(
            where={**where, 'issuedAt': {'gte': today_start}}
        )
        
        # Temps moyen de complétion (estimation)
        certificates = await self.db.certificate.find_many(
            where=where,
            take=100,
            order_by={'issuedAt': 'desc'}
        )
        
        if certificates:
            # Calculer la différence entre création du cours et émission certificat
            total_days = 0
            count = 0
            
            for cert in certificates:
                # Différence entre completion_date et création du cours
                course = await self.db.course.find_unique(
                    where={'id': cert['courseId']}
                )
                if course:
                    days_to_complete = (
                        cert['completionDate'] - course['createdAt']
                    ).days
                    if days_to_complete > 0:
                        total_days += days_to_complete
                        count += 1
            
            avg_time = total_days / count if count > 0 else 0
        else:
            avg_time = 0
        
        return {
            'totalIssued': total_issued,
            'totalVerifications': total_verifications,
            'issuedThisMonth': issued_this_month,
            'issuedThisWeek': issued_this_week,
            'issuedToday': issued_today,
            'averageTimeToComplete': int(avg_time)
        }
    
    async def get_top_certified_courses(self, limit: int = 10) -> List[Dict]:
        """Récupérer les cours avec le plus de certificats émis"""
        # Grouper par courseId et compter
        certificates = await self.db.certificate.find_many()
        
        course_counts = {}
        for cert in certificates:
            course_id = cert['courseId']
            course_counts[course_id] = course_counts.get(course_id, 0) + 1
        
        # Trier par nombre de certificats
        sorted_courses = sorted(
            course_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Enrichir avec les infos de cours
        result = []
        for course_id, count in sorted_courses:
            course = await self.db.course.find_unique(
                where={'id': course_id}
            )
            if course:
                result.append({
                    'course': course,
                    'certificateCount': count
                })
        
        return result
    
    async def bulk_generate_certificates(
        self,
        certificates_data: List[Dict]
    ) -> List[Dict]:
        """Générer plusieurs certificats en batch"""
        results = []
        
        for data in certificates_data:
            try:
                cert = await self.generate_certificate(
                    user_id=data['userId'],
                    course_id=data['courseId'],
                    completion_date=data['completionDate'],
                    grade=data.get('grade'),
                    metadata=data.get('metadata')
                )
                results.append({'success': True, 'certificate': cert})
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'data': data
                })
        
        return results