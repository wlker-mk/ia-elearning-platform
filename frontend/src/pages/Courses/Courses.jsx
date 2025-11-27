// src/pages/Courses/Courses.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/courses.css';

function Courses() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Données des cours
  const allCourses = [
    {
      id: 1,
      title: 'Introduction au Machine Learning',
      description: 'Découvrez les bases fondamentaux du Machine Learning, les algorithmes et modèles prédictifs.',
      subject: 'Machine Learning',
      level: 'Débutant',
      duration: '6 semaines',
      image: '/src/assets/images/introduction.jpeg',
      imageClass: 'course-img-1'
    },
    {
      id: 2,
      title: 'Maîtrise du Deep Learning avec TensorFlow',
      description: 'Apprenez à construire et entraîner des réseaux de neurones profonds.',
      subject: 'Deep Learning',
      level: 'Intermédiaire',
      duration: '10 semaines',
      image: '/src/assets/images/deep_learning.jpeg',
      imageClass: 'course-img-2'
    },
    {
      id: 3,
      title: 'Traitement du Langage Naturel pour Débutants',
      description: 'Explorez les bases du TLN, des embeddings de mots aux chatbots.',
      subject: 'Traitement du Langage Naturel',
      level: 'Débutant',
      duration: '8 semaines',
      image: '/src/assets/images/debutantLangage.jpeg',
      imageClass: 'course-img-3'
    },
    {
      id: 4,
      title: 'Vision par Ordinateur : Fondamentaux et Applications',
      description: 'Acquérez les compétences pour l\'analyse d\'images et la reconnaissance.',
      subject: 'Vision par Ordinateur',
      level: 'Intermédiaire',
      duration: '12 semaines',
      image: '/src/assets/images/visionparordinateur.jpeg',
      imageClass: 'course-img-4'
    },
    {
      id: 5,
      title: 'Éthique de l\'IA et IA Responsable',
      description: 'Comprenez les implications éthiques de l\'IA et apprenez à développer des solutions responsables.',
      subject: 'Éthique de l\'IA',
      level: 'Avancé',
      duration: '4 semaines',
      image: '/src/assets/images/ethique_IA.jpeg',
      imageClass: 'course-img-5'
    },
    {
      id: 6,
      title: 'Développement d\'Applications IA avec Python',
      description: 'Construisez des applications intelligentes de bout en bout, de l\'idée au déploiement.',
      subject: 'Développement d\'Applications IA',
      level: 'Avancé',
      duration: '14 semaines',
      image: '/src/assets/images/python.jpeg',
      imageClass: 'course-img-6'
    },
    {
      id: 7,
      title: 'Apprentissage Renforcé : Théorie et Pratique',
      description: 'Plongez dans l\'apprentissage renforcé, de Q-learning aux algorithmes avancés.',
      subject: 'Machine Learning',
      level: 'Intermédiaire',
      duration: '10 semaines',
      image: '/src/assets/images/theorie_pratique.jpeg',
      imageClass: 'course-img-7'
    },
    {
      id: 8,
      title: 'Génération de Texte avec GPT et Transformers',
      description: 'Créez des modèles de langage avancés pour la génération de texte intelligente.',
      subject: 'Traitement du Langage Naturel',
      level: 'Avancé',
      duration: '9 semaines',
      image: '/src/assets/images/gpt_transforme.jpeg',
      imageClass: 'course-img-8'
    }
  ];

  // Options de filtres
  const subjects = [
    'Machine Learning',
    'Deep Learning',
    'Vision par Ordinateur',
    'Traitement du Langage Naturel',
    'Éthique de l\'IA',
    'Développement d\'Applications IA'
  ];

  const levels = ['Débutant', 'Intermédiaire', 'Avancé'];

  // Filtrage des cours
  const filteredCourses = allCourses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         course.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSubject = !selectedSubject || course.subject === selectedSubject;
    const matchesLevel = !selectedLevel || course.level === selectedLevel;
    
    return matchesSearch && matchesSubject && matchesLevel;
  });

  // Pagination
  const coursesPerPage = 8;
  const totalPages = Math.ceil(filteredCourses.length / coursesPerPage);
  const startIndex = (currentPage - 1) * coursesPerPage;
  const endIndex = startIndex + coursesPerPage;
  const currentCourses = filteredCourses.slice(startIndex, endIndex);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedSubject('');
    setSelectedLevel('');
    setCurrentPage(1);
  };

  const handleApplyFilters = () => {
    setCurrentPage(1);
    console.log('Filtres appliqués:', { searchQuery, selectedSubject, selectedLevel });
  };

  const handleStartCourse = (courseId) => {
    console.log('Commencer le cours:', courseId);
    navigate(`/courses/${courseId}`);
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <main className="main-content">
      <div className="container">
        {/* Page Title */}
        <section className="page-header">
          <h1>Découvrez nos Cours d'Intelligence Artificielle</h1>
        </section>

        {/* Filters Section */}
        <section className="filters-section">
          <h2>Filtrez vos Cours</h2>
          <div className="filters-container">
            <div className="search-filter">
              <input
                type="text"
                placeholder="Rechercher par mot-clé..."
                className="filter-search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="select-filters">
              <select
                className="filter-select"
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
              >
                <option value="">Sélectionner un Sujet</option>
                {subjects.map((subject, index) => (
                  <option key={index} value={subject}>
                    {subject}
                  </option>
                ))}
              </select>
              <select
                className="filter-select"
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
              >
                <option value="">Sélectionner un Niveau</option>
                {levels.map((level, index) => (
                  <option key={index} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-actions">
              <button className="btn-reset" onClick={handleResetFilters}>
                Réinitialiser
              </button>
              <button className="btn-apply" onClick={handleApplyFilters}>
                Appliquer les filtres
              </button>
            </div>
          </div>
        </section>

        {/* Courses Grid */}
        <section className="courses-section">
          {filteredCourses.length === 0 ? (
            <div className="no-results">
              <p>Aucun cours trouvé avec ces critères. Essayez de modifier vos filtres.</p>
            </div>
          ) : (
            <div className="courses-grid">
              {currentCourses.map((course, index) => (
                <div
                  key={course.id}
                  className="course-card"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className={`course-image ${course.imageClass}`}>
                    <img
                      src={course.image}
                      alt={course.title}
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/400x200/c47a00/FFFFFF?text=Course';
                      }}
                    />
                    <div className="course-overlay">
                      <div className="course-tags">
                        <span className="tag tag-subject">{course.subject}</span>
                        <span className="tag tag-level">{course.level}</span>
                      </div>
                    </div>
                  </div>
                  <div className="course-content">
                    <h3>{course.title}</h3>
                    <p>{course.description}</p>
                    <div className="course-meta">
                      <span className="duration">⏱ {course.duration}</span>
                    </div>
                    <button
                      className="btn-course"
                      onClick={() => handleStartCourse(course.id)}
                    >
                      Commencer
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Pagination */}
        {filteredCourses.length > coursesPerPage && (
          <section className="pagination-section">
            <div className="pagination">
              <button
                className="page-btn page-prev"
                onClick={handlePreviousPage}
                disabled={currentPage === 1}
              >
                ‹
              </button>
              <button className="page-btn page-active">
                Page {currentPage} sur {totalPages}
              </button>
              <button
                className="page-btn page-next"
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
              >
                ›
              </button>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

export default Courses;