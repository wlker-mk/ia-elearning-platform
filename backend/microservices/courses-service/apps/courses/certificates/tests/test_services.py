import pytest
from apps.courses.certificates.services import CertificatesService
from datetime import datetime, timedelta
import uuid

@pytest.fixture
async def certificates_service():
    """Fixture pour le service certificates"""
    service = CertificatesService()
    await service.connect()
    yield service
    await service.disconnect()

@pytest.fixture
async def sample_course(courses_service):
    """Créer un cours de test"""
    course_data = {
        'title': 'Test Course',
        'description': 'Test description',
        'categoryId': str(uuid.uuid4()),
        'difficulty': 'BEGINNER',
        'type': 'VIDEO_COURSE',
        'price': 99.99,
        'estimatedDuration': 3600
    }
    
    instructor_id = str(uuid.uuid4())
    course = await courses_service.create_course(course_data, instructor_id)
    return course

@pytest.mark.asyncio
class TestCertificatesService:
    """Tests pour le service des certificats"""
    
    async def test_generate_certificate(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test génération de certificat"""
        user_id = str(uuid.uuid4())
        
        certificate = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow(),
            grade='A'
        )
        
        assert certificate is not None
        assert certificate['userId'] == user_id
        assert certificate['courseId'] == sample_course['id']
        assert certificate['certificateNumber'].startswith('CERT-')
        assert certificate['grade'] == 'A'
    
    async def test_certificate_number_unique(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test unicité du numéro de certificat"""
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())
        
        cert1 = await certificates_service.generate_certificate(
            user_id=user1_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        cert2 = await certificates_service.generate_certificate(
            user_id=user2_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        assert cert1['certificateNumber'] != cert2['certificateNumber']
    
    async def test_prevent_duplicate_certificate(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test prévention des certificats dupliqués"""
        user_id = str(uuid.uuid4())
        
        cert1 = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        # Tenter de créer un second certificat
        cert2 = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        # Devrait retourner le même certificat
        assert cert1['id'] == cert2['id']
    
    async def test_get_certificate_by_id(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test récupération par ID"""
        user_id = str(uuid.uuid4())
        
        created = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        certificate = await certificates_service.get_certificate_by_id(
            created['id']
        )
        
        assert certificate is not None
        assert certificate['id'] == created['id']
    
    async def test_get_certificate_by_number(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test récupération par numéro"""
        user_id = str(uuid.uuid4())
        
        created = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        certificate = await certificates_service.get_certificate_by_number(
            created['certificateNumber']
        )
        
        assert certificate is not None
        assert certificate['certificateNumber'] == created['certificateNumber']
    
    async def test_get_user_certificates(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test récupération des certificats d'un utilisateur"""
        user_id = str(uuid.uuid4())
        
        # Créer plusieurs certificats
        for i in range(3):
            await certificates_service.generate_certificate(
                user_id=user_id,
                course_id=str(uuid.uuid4()),
                completion_date=datetime.utcnow()
            )
        
        certificates = await certificates_service.get_user_certificates(user_id)
        
        assert len(certificates) == 3
    
    async def test_verify_certificate_valid(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test vérification de certificat valide"""
        user_id = str(uuid.uuid4())
        
        cert = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        result = await certificates_service.verify_certificate(
            cert['certificateNumber'],
            ip_address='127.0.0.1'
        )
        
        assert result['isValid'] is True
        assert result['message'] == 'Certificate is valid'
        assert result['certificate']['id'] == cert['id']
    
    async def test_verify_certificate_not_found(self, certificates_service):
        """Test vérification de certificat inexistant"""
        result = await certificates_service.verify_certificate(
            'CERT-999999-INVALID'
        )
        
        assert result['isValid'] is False
        assert result['message'] == 'Certificate not found'
    
    async def test_verify_certificate_expired(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test vérification de certificat expiré"""
        user_id = str(uuid.uuid4())
        
        cert = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        # Définir une date d'expiration dans le passé
        await certificates_service.db.certificate.update(
            where={'id': cert['id']},
            data={'expiresAt': datetime.utcnow() - timedelta(days=1)}
        )
        
        result = await certificates_service.verify_certificate(
            cert['certificateNumber']
        )
        
        assert result['isValid'] is False
        assert 'expired' in result['message'].lower()
    
    async def test_revoke_certificate(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test révocation de certificat"""
        user_id = str(uuid.uuid4())
        
        cert = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        revoked = await certificates_service.revoke_certificate(
            cert['id'],
            reason='Test revocation'
        )
        
        assert revoked['metadata']['revoked'] is True
        assert revoked['metadata']['revokeReason'] == 'Test revocation'
        
        # Vérifier que le certificat est maintenant invalide
        result = await certificates_service.verify_certificate(
            cert['certificateNumber']
        )
        assert result['isValid'] is False
    
    async def test_create_template(self, certificates_service):
        """Test création de template"""
        template_data = {
            'name': 'Classic Template',
            'description': 'A classic certificate template',
            'templateHtml': '<html><body>{{certificate_number}}</body></html>',
            'templateCss': 'body { font-family: Arial; }',
            'isDefault': True
        }
        
        template = await certificates_service.create_template(template_data)
        
        assert template is not None
        assert template['name'] == 'Classic Template'
        assert template['isDefault'] is True
    
    async def test_get_default_template(self, certificates_service):
        """Test récupération du template par défaut"""
        # Créer un template par défaut
        await certificates_service.create_template({
            'name': 'Default Template',
            'templateHtml': '<html></html>',
            'isDefault': True
        })
        
        template = await certificates_service.get_default_template()
        
        assert template is not None
        assert template['isDefault'] is True
    
    async def test_only_one_default_template(self, certificates_service):
        """Test qu'il ne peut y avoir qu'un seul template par défaut"""
        # Créer un premier template par défaut
        template1 = await certificates_service.create_template({
            'name': 'Template 1',
            'templateHtml': '<html></html>',
            'isDefault': True
        })
        
        # Créer un second template par défaut
        template2 = await certificates_service.create_template({
            'name': 'Template 2',
            'templateHtml': '<html></html>',
            'isDefault': True
        })
        
        # Vérifier que le premier n'est plus par défaut
        updated_template1 = await certificates_service.get_template(
            template1['id']
        )
        
        assert updated_template1['isDefault'] is False
        assert template2['isDefault'] is True
    
    async def test_list_templates(self, certificates_service):
        """Test listage des templates"""
        # Créer plusieurs templates
        for i in range(3):
            await certificates_service.create_template({
                'name': f'Template {i}',
                'templateHtml': '<html></html>',
                'isActive': i < 2  # 2 actifs, 1 inactif
            })
        
        # Lister uniquement les actifs
        active_templates = await certificates_service.list_templates(
            active_only=True
        )
        assert len(active_templates) == 2
        
        # Lister tous
        all_templates = await certificates_service.list_templates(
            active_only=False
        )
        assert len(all_templates) == 3
    
    async def test_get_certificate_statistics(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test statistiques"""
        # Générer quelques certificats
        for i in range(5):
            await certificates_service.generate_certificate(
                user_id=str(uuid.uuid4()),
                course_id=sample_course['id'],
                completion_date=datetime.utcnow()
            )
        
        stats = await certificates_service.get_certificate_statistics(
            course_id=sample_course['id']
        )
        
        assert stats['totalIssued'] == 5
        assert stats['issuedToday'] == 5
    
    async def test_bulk_generate_certificates(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test génération en batch"""
        certificates_data = [
            {
                'userId': str(uuid.uuid4()),
                'courseId': sample_course['id'],
                'completionDate': datetime.utcnow(),
                'grade': 'A'
            }
            for _ in range(3)
        ]
        
        results = await certificates_service.bulk_generate_certificates(
            certificates_data
        )
        
        assert len(results) == 3
        assert all(r['success'] for r in results)
    
    async def test_update_certificate_pdf(
        self, 
        certificates_service, 
        sample_course
    ):
        """Test mise à jour de l'URL du PDF"""
        user_id = str(uuid.uuid4())
        
        cert = await certificates_service.generate_certificate(
            user_id=user_id,
            course_id=sample_course['id'],
            completion_date=datetime.utcnow()
        )
        
        pdf_url = 'https://cdn.platform.com/cert.pdf'
        updated = await certificates_service.update_certificate_pdf(
            cert['id'],
            pdf_url
        )
        
        assert updated['pdfUrl'] == pdf_url