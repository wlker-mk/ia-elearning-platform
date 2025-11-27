// src/pages/Instructors/Instructors.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/instructors.css';

function Instructors() {
  const navigate = useNavigate();

  // Données des professeurs
  const professors = [
    {
      id: 1,
      name: 'Dr. Elara N\'Doye',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b15c2e4c?w=80&h=80&fit=crop&crop=face',
      tags: ['Mathématiques', 'Algèbre Linéaire'],
      rating: 4.9
    },
    {
      id: 2,
      name: 'Prof. Kwame Nkrumah',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=80&h=80&fit=crop&crop=face',
      tags: ['Histoire Africaine', 'Géopolitique'],
      rating: 4.8
    },
    {
      id: 3,
      name: 'Mme. Zola Mbatha',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face',
      tags: ['Littérature Africaine', 'Rhétorique Écrite'],
      rating: 4.9
    },
    {
      id: 4,
      name: 'Dr. Amara Diallo',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face',
      tags: ['Relations Internationales'],
      rating: 4.8
    },
    {
      id: 5,
      name: 'Dr. Aisha Suleiman',
      avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop&crop=face',
      tags: ['Biologie Marine', 'Écologie'],
      rating: 4.9
    },
    {
      id: 6,
      name: 'Prof. Ken Saro-Wiwa',
      avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=80&h=80&fit=crop&crop=face',
      tags: ['Environnement', 'Droits de l\'Homme'],
      rating: 4.7
    },
    {
      id: 7,
      name: 'Mme. Nala Zulu',
      avatar: 'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=80&h=80&fit=crop&crop=face',
      tags: ['Art Visuel', 'Design Graphique'],
      rating: 4.8
    },
    {
      id: 8,
      name: 'M. Jomo Kenyatta',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=80&h=80&fit=crop&crop=face',
      tags: ['Sciences Agricoles', 'Économie'],
      rating: 4.6
    }
  ];

  // Données des témoignages
  const testimonials = [
    {
      id: 1,
      message: 'J\'ai trouvé les cours de AfroAI Learn exceptionnellement enrichissants et pertinents. Les professeurs sont passionnés et très compétents.',
      author: 'Fatima Diallo',
      role: 'Étudiante en Histoire',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b15c2e4c?w=50&h=50&fit=crop&crop=face'
    },
    {
      id: 2,
      message: 'La plateforme est intuitive et l\'approche pédagogique qui permet de progresser rapidement en Mathématiques. Une expérience remarquable.',
      author: 'Omar Diabou',
      role: 'Étudiant en Ingénierie',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50&h=50&fit=crop&crop=face'
    },
    {
      id: 3,
      message: 'AfroAI Learn a transformé ma manière d\'apprendre. La qualité des ressources et le soutien des professeurs sont inégalés.',
      author: 'Aissata Kone',
      role: 'Étudiante en Littérature',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50&h=50&fit=crop&crop=face'
    }
  ];

  const handleStartAdventure = () => {
    navigate('/courses');
  };

  const handleViewProfile = (professorId) => {
    console.log('Voir le profil de:', professorId);
    // navigate(`/instructors/${professorId}`);
  };

  const handleExploreCourses = () => {
    navigate('/courses');
  };

  return (
    <div className="instructors-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1>L'Apprentissage Inspiré par l'Afrique</h1>
              <p>
                Découvrez des professeurs exceptionnels et des cours qui célèbrent 
                la richesse de la culture et du savoir africain.
              </p>
              <button className="btn-cta" onClick={handleStartAdventure}>
                Commencer l'Aventure
              </button>
            </div>
            <div className="hero-image">
              <div className="african-patterns">
                <div className="pattern pattern-1"></div>
                <div className="pattern pattern-2"></div>
                <div className="pattern pattern-3"></div>
                <div className="pattern pattern-4"></div>
                <div className="pattern pattern-5"></div>
                <div className="pattern pattern-6"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="mission">
        <div className="container">
          <h2>Notre Mission : Élever les Talents</h2>
          <p>
            AfroAI Learn s'engage à offrir une éducation de qualité, accessible à tous, 
            en mettant en avant l'expertise de professeurs inspirants et des programmes 
            pédagogiques innovants, ancrés dans les traditions et les aspirations de l'Afrique.
          </p>
        </div>
      </section>

      {/* Professors Section */}
      <section className="professors">
        <div className="container">
          <h2>Nos Professeurs Exceptionnels</h2>
          <div className="professors-grid">
            {professors.map((professor, index) => (
              <div
                key={professor.id}
                className="professor-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="professor-avatar">
                  <img src={professor.avatar} alt={professor.name} />
                </div>
                <h3>{professor.name}</h3>
                <div className="professor-tags">
                  {professor.tags.map((tag, idx) => (
                    <span key={idx} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="rating">⭐ {professor.rating}</div>
                <button
                  className="btn-profile"
                  onClick={() => handleViewProfile(professor.id)}
                >
                  Voir le profil
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <div className="container">
          <h2>Ce que Disent nos Étudiants</h2>
          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div
                key={testimonial.id}
                className="testimonial-card"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <p>"{testimonial.message}"</p>
                <div className="testimonial-author">
                  <img src={testimonial.avatar} alt={testimonial.author} />
                  <div className="author-info">
                    <h4>{testimonial.author}</h4>
                    <span>{testimonial.role}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="container">
          <h2>Prêt à Commencer Votre Voyage d'Apprentissage ?</h2>
          <p>
            Rejoignez la communauté AfroAI Learn et accédez à une multitude de 
            connaissances et d'opportunités.
          </p>
          <button className="btn-cta-large" onClick={handleExploreCourses}>
            Explorer les Cours
          </button>
        </div>
      </section>
    </div>
  );
}

export default Instructors;