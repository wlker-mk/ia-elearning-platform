// src/pages/Dashboard/StudentDashboard.jsx
import { useState } from 'react';
import { useSelector } from 'react-redux';
import { selectUser } from '../../store/slices/authSlice';
import '../../styles/studentDashboard.css';

function StudentDashboard() {
  const user = useSelector(selectUser);
  const [selectedCourse, setSelectedCourse] = useState(null);

  // Données des cours
  const courses = [
    {
      id: 1,
      title: "Introduction à l'IA et au Machine Learning",
      description: "Découvrez les fondements de l'intelligence artificielle et du machine learning, de la théorie aux applications pratiques.",
      progress: 75,
      status: 'in-progress',
      imageClass: 'intro-ai'
    },
    {
      id: 2,
      title: 'Deep Learning avec TensorFlow',
      description: "Maîtrisez les réseaux de neurones profonds et développez des modèles complexes avec TensorFlow.",
      progress: 40,
      status: 'in-progress',
      imageClass: 'deep-learning'
    },
    {
      id: 3,
      title: 'Traitement du Langage Naturel (TLN)',
      description: "Apprenez à construire des systèmes qui comprennent et génèrent du langage humain.",
      progress: 90,
      status: 'in-progress',
      imageClass: 'nlp'
    },
    {
      id: 4,
      title: "Éthique de l'IA et Société",
      description: "Explorez les implications éthiques et sociales de l'IA, et comment construire des systèmes responsables.",
      progress: 100,
      status: 'completed',
      imageClass: 'ethics'
    }
  ];

  // Données des réalisations
  const achievements = [
    { id: 1, icon: '🐍', title: "Expert en Python pour l'IA", type: 'Badge', iconClass: 'python' },
    { id: 2, icon: '📊', title: 'Certificat Deep Learning', type: 'Certificat', iconClass: 'deep-cert' },
    { id: 3, icon: '⚙️', title: 'Maître du Machine Learning', type: 'Badge', iconClass: 'ml-master' },
    { id: 4, icon: '⭐', title: "Pionnier de l'IA Africaine", type: 'Badge', iconClass: 'ai-pioneer' },
    { id: 5, icon: '💡', title: 'Innovateur en TLN', type: 'Badge', iconClass: 'nlp-innovator' },
    { id: 6, icon: '👤', title: 'Certificat en Éthique IA', type: 'Certificat', iconClass: 'ethics-cert' }
  ];

  // Données des statistiques (temps par mois)
  const learningTimeData = [
    { month: 'Jan', hours: 120, height: 60 },
    { month: 'Fév', hours: 140, height: 70 },
    { month: 'Mar', hours: 170, height: 85 },
    { month: 'Avr', hours: 180, height: 90 },
    { month: 'Mai', hours: 190, height: 95 },
    { month: 'Jun', hours: 200, height: 100 }
  ];

  // Données des compétences
  const skills = [
    { name: 'Machine Learning', color: '#7B68EE' },
    { name: 'Deep Learning', color: '#e91e63' },
    { name: 'TLN', color: '#FFD700' },
    { name: 'Vision par Ordinateur', color: '#00CED1' },
    { name: 'Éthique IA', color: '#32CD32' }
  ];

  // Recommandations de cours
  const recommendations = [
    {
      id: 1,
      title: 'IA Générative : Principes et Applications',
      tags: [
        { label: 'Innovation', class: 'innovation' },
        { label: 'Avancé', class: 'advanced' }
      ]
    },
    {
      id: 2,
      title: "Déploiement de modèles d'IA en production",
      tags: [
        { label: 'Déploiement', class: 'deployment' },
        { label: 'Intermédiaire', class: 'intermediate' }
      ]
    },
    {
      id: 3,
      title: 'Comprendre les Réseaux de Neurones Convolutifs',
      tags: [
        { label: 'Vision par Ordinateur', class: 'computer-vision' },
        { label: 'Débutant', class: 'beginner' }
      ]
    }
  ];

  const handleContinueCourse = (courseId) => {
    console.log('Continuer le cours:', courseId);
    // Navigation vers le cours
  };

  const handleViewCertificate = (courseId) => {
    console.log('Voir le certificat:', courseId);
    // Ouvrir le certificat
  };

  const handleEditProfile = () => {
    console.log('Modifier le profil');
    // Navigation vers la page de profil
  };

  const handleViewCourse = (courseId) => {
    console.log('Voir le cours recommandé:', courseId);
    // Navigation vers le cours
  };

  return (
    <main className="main-content">
      {/* Welcome Section */}
      <div className="welcome-section">
        <div className="welcome-content">
          <div className="user-info">
            <img 
              src={`data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Ccircle cx='40' cy='40' r='40' fill='%23c47a00'/%3E%3Ctext x='40' y='50' text-anchor='middle' fill='white' font-family='Arial' font-size='28' font-weight='bold'%3E${user?.name?.charAt(0) || 'A'}%3C/text%3E%3C/svg%3E`}
              alt="User Avatar" 
              className="user-avatar-large"
            />
            <div className="user-details">
              <h1 className="user-greeting">Bonjour, {user?.name || 'Apprenant'}!</h1>
              <p className="user-message">Votre voyage dans l'IA continue. Apprenons ensemble!</p>
            </div>
          </div>
          <div className="user-status">
            <p className="last-connection">Dernière connexion: 5 minutes</p>
            <button className="edit-profile-btn" onClick={handleEditProfile}>
              Modifier le profil
            </button>
          </div>
        </div>
      </div>

      {/* My Courses Section */}
      <section className="courses-section">
        <h2 className="section-title">Mes Cours</h2>
        <div className="courses-grid">
          {courses.map((course) => (
            <div key={course.id} className={`course-card ${course.status === 'completed' ? 'completed' : ''}`}>
              <div className={`course-image ${course.imageClass}`}>
                <div className="course-overlay">
                  <h3 className="course-title">{course.title}</h3>
                  {course.status === 'completed' && (
                    <span className="completed-badge">Terminé</span>
                  )}
                </div>
              </div>
              <div className="course-content">
                <p className="course-description">{course.description}</p>
                {course.status === 'in-progress' ? (
                  <>
                    <div className="progress-container">
                      <div className="progress-label">
                        <span>Progression</span>
                        <span>{course.progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${course.progress}%` }}></div>
                      </div>
                    </div>
                    <button 
                      className="continue-btn"
                      onClick={() => handleContinueCourse(course.id)}
                    >
                      Continuer le cours
                    </button>
                  </>
                ) : (
                  <button 
                    className="certificate-btn"
                    onClick={() => handleViewCertificate(course.id)}
                  >
                    Voir le certificat
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Achievements Section */}
      <section className="achievements-section">
        <h2 className="section-title">Mes Réalisations</h2>
        <div className="achievements-grid">
          {achievements.map((achievement) => (
            <div key={achievement.id} className="achievement-item">
              <div className={`achievement-icon ${achievement.iconClass}`}>
                {achievement.icon}
              </div>
              <h4 className="achievement-title">{achievement.title}</h4>
              <span className="achievement-type">{achievement.type}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Statistics Section */}
      <section className="statistics-section">
        <h2 className="section-title">Statistiques de Progression</h2>
        <div className="stats-grid">
          {/* Bar Chart - Temps d'apprentissage */}
          <div className="stat-chart">
            <h3 className="chart-title">Temps passé à apprendre (heures)</h3>
            <div className="bar-chart">
              {learningTimeData.map((data, index) => (
                <div key={index} className="bar-container">
                  <div className="bar" style={{ height: `${data.height}%` }}>
                    <span className="bar-value">{data.hours}</span>
                  </div>
                  <div className="bar-label">{data.month}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Pie Chart - Compétences */}
          <div className="stat-chart">
            <h3 className="chart-title">Compétences acquises</h3>
            <div className="pie-chart">
              <svg viewBox="0 0 42 42" className="donut">
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#e91e63" strokeWidth="3" strokeDasharray="30 70" strokeDashoffset="25"></circle>
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#7B68EE" strokeWidth="3" strokeDasharray="25 75" strokeDashoffset="-5"></circle>
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#FFD700" strokeWidth="3" strokeDasharray="20 80" strokeDashoffset="-30"></circle>
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#00CED1" strokeWidth="3" strokeDasharray="15 85" strokeDashoffset="-50"></circle>
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#32CD32" strokeWidth="3" strokeDasharray="10 90" strokeDashoffset="-65"></circle>
              </svg>
              <div className="chart-legend">
                {skills.map((skill, index) => (
                  <div key={index} className="legend-item">
                    <span className="legend-color" style={{ background: skill.color }}></span>
                    <span className="legend-text">{skill.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Recommendations Section */}
      <section className="recommendations-section">
        <h2 className="section-title">Recommandations pour vous</h2>
        <div className="recommendations-grid">
          {recommendations.map((recommendation) => (
            <div key={recommendation.id} className="recommendation-card">
              <h3 className="recommendation-title">{recommendation.title}</h3>
              <div className="recommendation-tags">
                {recommendation.tags.map((tag, index) => (
                  <span key={index} className={`tag ${tag.class}`}>
                    {tag.label}
                  </span>
                ))}
              </div>
              <button 
                className="view-course-btn"
                onClick={() => handleViewCourse(recommendation.id)}
              >
                Voir le cours
              </button>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default StudentDashboard;