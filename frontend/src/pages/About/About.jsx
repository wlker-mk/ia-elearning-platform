// src/pages/About/About.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/about.css';

function About() {
  const navigate = useNavigate();
  const [activeFaq, setActiveFaq] = useState(null);

  // Animation au scroll
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    document.querySelectorAll('.scroll-animate').forEach(el => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  // Données des statistiques
  const stats = [
    { number: '5000+', label: 'Étudiants formés' },
    { number: '150+', label: 'Cours disponibles' },
    { number: '95%', label: 'Taux de réussite' },
    { number: '20+', label: 'Formateurs experts' }
  ];

  // Données des valeurs
  const values = [
    {
      icon: 'fas fa-universal-access',
      title: 'Accessibilité Universelle',
      description: 'Nous rendons l\'éducation accessible à tous, indépendamment de la localisation géographique, du niveau socio-économique ou des contraintes personnelles.'
    },
    {
      icon: 'fas fa-lightbulb',
      title: 'Innovation Pédagogique',
      description: 'Nos méthodes d\'enseignement intègrent les dernières avancées technologiques et les meilleures pratiques en neurosciences de l\'apprentissage.'
    },
    {
      icon: 'fas fa-users',
      title: 'Apprentissage Collaboratif',
      description: 'Nous favorisons les échanges entre apprenants, créant une communauté d\'entraide qui enrichit l\'expérience éducative de chacun.'
    },
    {
      icon: 'fas fa-target',
      title: 'Excellence & Résultats',
      description: 'Nous nous engageons à maintenir les plus hauts standards de qualité et à mesurer notre succès par la réussite de nos apprenants.'
    }
  ];

  // Données de l'équipe
  const team = [
    {
      id: 1,
      name: 'Dr. Amina Diallo',
      role: 'Experte Data Science & IA',
      description: 'Docteur en informatique avec plus de 12 ans d\'expérience. Spécialisée dans l\'intelligence artificielle appliquée aux défis africains.',
      icon: 'fas fa-user-graduate',
      socials: ['linkedin', 'twitter', 'envelope']
    },
    {
      id: 2,
      name: 'Kwame Asante',
      role: 'Lead Developer & Formateur',
      description: 'Expert en développement logiciel et intelligence artificielle. Accompagne les entreprises dans leur transformation numérique.',
      icon: 'fas fa-code',
      socials: ['github', 'linkedin', 'globe']
    },
    {
      id: 3,
      name: 'Fatou Koné',
      role: 'Consultante Pédagogique',
      description: 'Spécialisée en ingénierie pédagogique et accompagnement personnalisé. Guide les apprenants vers l\'excellence académique et professionnelle.',
      icon: 'fas fa-chalkboard-teacher',
      socials: ['linkedin', 'instagram', 'envelope']
    }
  ];

  // Données FAQ
  const faqs = [
    {
      id: 1,
      question: 'Comment puis-je m\'inscrire aux cours ?',
      answer: 'L\'inscription est simple et rapide. Créez votre compte sur notre plateforme, choisissez vos cours et commencez immédiatement votre parcours d\'apprentissage. Un conseiller pédagogique vous contactera pour personnaliser votre formation.'
    },
    {
      id: 2,
      question: 'Quels sont les domaines de formation disponibles ?',
      answer: 'Nous proposons des formations en Data Science, Intelligence Artificielle, développement web et mobile, cybersécurité, marketing digital, gestion de projet, et bien d\'autres domaines en constante évolution.'
    },
    {
      id: 3,
      question: 'Les certificats sont-ils reconnus professionnellement ?',
      answer: 'Absolument ! Nos certificats sont reconnus par de nombreuses entreprises et organisations. Ils attestent de compétences concrètes et sont valorisés sur le marché de l\'emploi. Nous entretenons des partenariats avec des entreprises leaders pour faciliter l\'insertion professionnelle de nos diplômés.'
    },
    {
      id: 4,
      question: 'Quel est le niveau de support et d\'accompagnement ?',
      answer: 'Chaque apprenant bénéficie d\'un accompagnement personnalisé avec un mentor dédié, des sessions de coaching individuel, un accès 24/7 au support technique, et une communauté d\'entraide active.'
    },
    {
      id: 5,
      question: 'Puis-je suivre les cours à mon rythme ?',
      answer: 'Oui, notre plateforme est conçue pour s\'adapter à votre emploi du temps. Vous pouvez apprendre à votre rythme, avec des cours disponibles 24h/24 et des échéances flexibles pour respecter vos contraintes personnelles et professionnelles.'
    }
  ];

  const toggleFaq = (id) => {
    setActiveFaq(activeFaq === id ? null : id);
  };

  const handleStartNow = () => {
    navigate('/register');
  };

  const handleExploreCourses = () => {
    navigate('/courses');
  };

  return (
    <div className="about-page">
      {/* Hero Section */}
      <section className="hero" id="hero">
        <div className="hero-content">
          <h1>Transformez votre avenir avec l'eLearning</h1>
          <p>
            Une plateforme d'apprentissage innovante qui combine excellence pédagogique 
            et technologies de pointe pour révéler tout votre potentiel.
          </p>
          <div className="hero-cta">
            <button onClick={handleStartNow} className="btn btn-primary">
              <i className="fas fa-rocket"></i> Commencer maintenant
            </button>
            <button onClick={handleExploreCourses} className="btn btn-secondary">
              <i className="fas fa-play"></i> Découvrir notre approche
            </button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats">
        <div className="container">
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div key={index} className="stat-item">
                <span className="stat-number">{stat.number}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="mission scroll-animate">
        <div className="container">
          <div className="mission-content">
            <div className="mission-text">
              <h2>Notre Mission</h2>
              <p>
                Démocratiser l'accès à une éducation de qualité en proposant des parcours 
                d'apprentissage flexibles, personnalisés et adaptés aux défis du monde 
                professionnel moderne.
              </p>
              <ul className="mission-features">
                <li>
                  <i className="fas fa-check-circle"></i> Formation certifiante reconnue
                </li>
                <li>
                  <i className="fas fa-check-circle"></i> Accompagnement personnalisé
                </li>
                <li>
                  <i className="fas fa-check-circle"></i> Méthodes pédagogiques innovantes
                </li>
                <li>
                  <i className="fas fa-check-circle"></i> Communauté d'apprentissage active
                </li>
              </ul>
            </div>
            <div className="mission-visual">
              <img 
                src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80" 
                alt="Mission eLearning" 
              />
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="values scroll-animate">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Nos Valeurs Fondamentales</h2>
            <p className="section-subtitle">
              Les principes qui guident notre approche pédagogique et notre engagement 
              envers vos réussites
            </p>
          </div>
          <div className="values-grid">
            {values.map((value, index) => (
              <div key={index} className="value-card">
                <div className="value-icon">
                  <i className={value.icon}></i>
                </div>
                <h3>{value.title}</h3>
                <p>{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="team scroll-animate">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Notre Équipe d'Experts</h2>
            <p className="section-subtitle">
              Des formateurs passionnés et reconnus dans leur domaine, dédiés à votre réussite
            </p>
          </div>
          <div className="team-grid">
            {team.map((member) => (
              <div key={member.id} className="team-member">
                <div className="member-image">
                  <i className={member.icon}></i>
                </div>
                <div className="member-info">
                  <h3>{member.name}</h3>
                  <div className="member-role">{member.role}</div>
                  <p>{member.description}</p>
                  <div className="social-links">
                    {member.socials.map((social, idx) => (
                      <a key={idx} href="#">
                        <i className={`fab fa-${social}`}></i>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section scroll-animate">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Questions Fréquemment Posées</h2>
            <p className="section-subtitle">
              Trouvez rapidement les réponses à vos questions les plus courantes
            </p>
          </div>
          <div className="faq-container">
            {faqs.map((faq) => (
              <div
                key={faq.id}
                className={`faq-item ${activeFaq === faq.id ? 'active' : ''}`}
              >
                <div className="faq-question" onClick={() => toggleFaq(faq.id)}>
                  <h3>{faq.question}</h3>
                  <span className="faq-toggle">+</span>
                </div>
                <div className="faq-answer">
                  <p>{faq.answer}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta scroll-animate">
        <div className="container">
          <div className="cta-content">
            <h2>Prêt à transformer votre carrière ?</h2>
            <p>
              Rejoignez plus de 5000 apprenants qui ont déjà choisi l'excellence. 
              Votre succès commence maintenant.
            </p>
            <div className="hero-cta">
              <button onClick={handleStartNow} className="btn btn-primary">
                <i className="fas fa-user-plus"></i> S'inscrire gratuitement
              </button>
              <button onClick={handleExploreCourses} className="btn btn-secondary">
                <i className="fas fa-book-open"></i> Explorer nos cours
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default About;