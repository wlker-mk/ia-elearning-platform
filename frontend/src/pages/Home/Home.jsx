// src/pages/Home/Home.jsx
import { Link } from 'react-router-dom';
import '../../styles/home.css';

function Home() {
  // Données des modules
  const modules = [
    {
      id: 1,
      title: 'Apprentissage Automatique Fondamental',
      description: 'Maîtrisez les bases de l\'apprentissage automatique, des algorithmes aux modèles prédictifs, avec des applications pratiques.',
      image: '/src/assets/images/autofondamental.jpeg',
    },
    {
      id: 2,
      title: 'Vision par Ordinateur Avancée',
      description: 'Découvrez les techniques de détection d\'objets, de reconnaissance faciale et de traitement d\'images pour des systèmes visuels intelligents.',
      image: '/src/assets/images/voision_avance.jpeg',
    },
    {
      id: 3,
      title: 'Traitement du Langage Naturel (TLN)',
      description: 'Plongez dans l\'analyse de texte, la traduction automatique et les chatbots pour créer des interactions vocales et textuelles.',
      image: '/src/assets/images/langage.jpeg',
    },
    {
      id: 4,
      title: 'Éthique de l\'IA et IA Responsable',
      description: 'Examinez les dilemmes éthiques de l\'IA et apprenez à développer des systèmes justes, transparents et responsables.',
      image: '/src/assets/images/ethique_IA.jpeg',
    },
    {
      id: 5,
      title: 'Deep Learning avec TensorFlow',
      description: 'Construisez et entraînez des réseaux neuronaux profonds pour vos applications complexes en utilisant TensorFlow et Keras.',
      image: '/src/assets/images/deep_learning.jpeg',
    },
    {
      id: 6,
      title: 'IA pour l\'Analyse Commerciale',
      description: 'Apprenez à appliquer l\'IA pour l\'analyse de données, l\'optimisation des processus et la prise de décision stratégique en entreprise.',
      image: '/src/assets/images/analyse_commercial.jpeg',
    },
  ];

  // Données des témoignages
  const testimonials = [
    {
      id: 1,
      name: 'Fatima Diallo',
      role: 'Développeuse IA Junior',
      message: 'AfroAI Learn m\'a ouvert les portes de l\'IA. Les cours sont pertinents et les instructeurs sont incroyables.',
      avatar: '/src/assets/images/profil_elearn5.jpeg',
    },
    {
      id: 2,
      name: 'Kwame Nsanzek',
      role: 'Analyste de Données',
      message: 'Le contenu est de haute qualité et l\'approche pratique m\'a vraiment aidé à progresser rapidement. Je recommande vivement !',
      avatar: '/src/assets/images/profil_elearn1.jpeg',
    },
  ];

  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1>Propulsez Votre Avenir avec l'IA en Afrique</h1>
              <p>
                AfroAI Learn est votre plateforme d'e-learning dédiée à l'intelligence artificielle, 
                conçue pour vous doter des compétences de demain.
              </p>
              <div className="hero-buttons">
                <Link to="/register" className="btn-primary">
                  S'inscrire Maintenant
                </Link>
                <Link to="/courses" className="btn-secondary">
                  Découvrir les Cours
                </Link>
              </div>
            </div>
            <div className="hero-image">
              <img 
                src="/src/assets/images/apprentissage_IA.jpeg" 
                alt="Illustration d'apprentissage IA en Afrique"
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/500x400/3B82F6/FFFFFF?text=AI+Learning';
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Modules Section */}
      <section className="modules">
        <div className="container">
          <h2 className="section-title">Modules d'IA en Vedette</h2>
          <div className="modules-grid">
            {modules.map((module) => (
              <div key={module.id} className="module-card">
                <div className="module-image">
                  <img 
                    src={module.image} 
                    alt={module.title}
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/350x200/8B5CF6/FFFFFF?text=Course';
                    }}
                  />
                </div>
                <div className="module-content">
                  <h3>{module.title}</h3>
                  <p>{module.description}</p>
                  <button className="btn-outline">En Savoir Plus</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Section */}
      <section className="why-choose">
        <div className="container">
          <h2 className="section-title">Pourquoi Choisir AfroAI Learn ?</h2>
          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">
                <div className="icon-circle">⚡</div>
              </div>
              <h3>Approche Pratique</h3>
              <p>
                Apprenez au travers avec des projets réels et des études de cas qui 
                renforcent vos compétences.
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">
                <div className="icon-circle">💬</div>
              </div>
              <h3>Mentors Experts</h3>
              <p>
                Bénéficiez des conseils d'experts de l'industrie avec une expérience 
                africaine pertinente.
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">
                <div className="icon-circle">👥</div>
              </div>
              <h3>Communauté Engagée</h3>
              <p>
                Rejoignez un réseau dynamique d'apprenants et de professionnels 
                passionnés par l'IA.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <div className="container">
          <h2 className="section-title">Ce que Disent Nos Apprenants</h2>
          <div className="testimonials-grid">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="testimonial">
                <div className="testimonial-avatar">
                  <img 
                    src={testimonial.avatar} 
                    alt={`Photo de ${testimonial.name}`} 
                    className="avatar-img"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/60/9333EA/FFFFFF?text=' + testimonial.name.charAt(0);
                    }}
                  />
                </div>
                <div className="testimonial-content">
                  <p>"{testimonial.message}"</p>
                  <div className="testimonial-author">
                    <strong>{testimonial.name}</strong>
                    <span>{testimonial.role}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

export default Home;