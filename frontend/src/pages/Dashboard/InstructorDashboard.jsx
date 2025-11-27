// src/pages/Dashboard/InstructorDashboard.jsx
import { useState } from 'react';
import { useSelector } from 'react-redux';
import { selectUser } from '../../store/slices/authSlice';
import '../../styles/instructorDashboard.css';

function InstructorDashboard() {
  const user = useSelector(selectUser);
  const [activeNav, setActiveNav] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');

  // Données des cours
  const courses = [
    {
      id: 1,
      title: 'Introduction à la Programmation',
      students: 45,
      average: 82,
      imageClass: 'programming'
    },
    {
      id: 2,
      title: 'Mathématiques Appliquées',
      students: 38,
      average: 75,
      imageClass: 'math'
    },
    {
      id: 3,
      title: 'Histoire Moderne',
      students: 52,
      average: 90,
      imageClass: 'history'
    },
    {
      id: 4,
      title: 'Science Économique',
      students: 30,
      average: 68,
      imageClass: 'economics'
    }
  ];

  // Données des étudiants
  const students = [
    {
      id: 1,
      name: 'Alice Dupont',
      avatar: '👩‍💻',
      course: 'Introduction à la Programmation',
      progress: 85,
      status: 'active'
    },
    {
      id: 2,
      name: 'Jean Martin',
      avatar: '👨‍🎓',
      course: 'Mathématiques Appliquées',
      progress: 65,
      status: 'completed'
    },
    {
      id: 3,
      name: 'Sophie Dubois',
      avatar: '👩‍🔬',
      course: 'Histoire Moderne',
      progress: 30,
      status: 'pending'
    },
    {
      id: 4,
      name: 'Marc Lefèvre',
      avatar: '👨‍💼',
      course: 'Introduction à la Programmation',
      progress: 90,
      status: 'active'
    },
    {
      id: 5,
      name: 'Laura Petit',
      avatar: '👩‍🎨',
      course: 'Science Économique',
      progress: 45,
      status: 'active'
    }
  ];

  // Données des quiz
  const quizzes = [
    { id: 1, title: 'Quiz 1: Variables', date: '15/05/2024', status: 'publié' },
    { id: 2, title: 'Quiz 2: Fonctions', date: '20/05/2024', status: 'brouillon' },
    { id: 3, title: 'Examen Final', date: '01/06/2024', status: 'brouillon' },
    { id: 4, title: 'Quiz 3: Boucles', date: '25/04/2024', status: 'terminé' }
  ];

  // Données des ressources
  const resources = [
    { id: 1, icon: '📄', title: 'Guide de style CSS', type: 'PDF - 10/05/2024' },
    { id: 2, icon: '🎥', title: 'Tutoriel React', type: 'Vidéo - 08/05/2024' },
    { id: 3, icon: '📊', title: 'Exercices SQL', type: 'Document - 01/05/2024' }
  ];

  // Données des notifications
  const notifications = [
    { id: 1, icon: 'ℹ️', title: 'Nouveau devoir soumis pour "Programmation"', date: '12/05/2024' },
    { id: 2, icon: '⚠️', title: 'Rappel: Le délai pour le "Quiz 2" approche.', date: '11/05/2024' },
    { id: 3, icon: '📋', title: 'Évaluation requise pour "Alice Dupont".', date: '10/05/2024' },
    { id: 4, icon: '🔄', title: 'Mise à jour du programme "Histoire Moderne".', date: '09/05/2024' }
  ];

  const getStatusLabel = (status) => {
    const labels = {
      active: 'En cours',
      completed: 'Terminé',
      pending: 'En Retard'
    };
    return labels[status] || status;
  };

  const handleNavClick = (nav) => {
    setActiveNav(nav);
    console.log('Navigation vers:', nav);
  };

  return (
    <div className="instructor-dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">✦</span>
            <span className="logo-text">AfroAI</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <ul className="nav-list">
            <li className={`nav-item ${activeNav === 'dashboard' ? 'active' : ''}`}>
              <a href="#" className="nav-link" onClick={() => handleNavClick('dashboard')}>
                <span className="nav-icon">📊</span>
                <span className="nav-text">Tableau de bord</span>
              </a>
            </li>
            <li className={`nav-item ${activeNav === 'courses' ? 'active' : ''}`}>
              <a href="#" className="nav-link" onClick={() => handleNavClick('courses')}>
                <span className="nav-icon">📚</span>
                <span className="nav-text">Cours</span>
              </a>
            </li>
            <li className={`nav-item ${activeNav === 'students' ? 'active' : ''}`}>
              <a href="#" className="nav-link" onClick={() => handleNavClick('students')}>
                <span className="nav-icon">👥</span>
                <span className="nav-text">Étudiants</span>
              </a>
            </li>
            <li className={`nav-item ${activeNav === 'quiz' ? 'active' : ''}`}>
              <a href="#" className="nav-link" onClick={() => handleNavClick('quiz')}>
                <span className="nav-icon">📝</span>
                <span className="nav-text">Quiz</span>
              </a>
            </li>
            <li className={`nav-item ${activeNav === 'resources' ? 'active' : ''}`}>
              <a href="#" className="nav-link" onClick={() => handleNavClick('resources')}>
                <span className="nav-icon">📖</span>
                <span className="nav-text">Ressources</span>
              </a>
            </li>
            <li className={`nav-item ${activeNav === 'notifications' ? 'active' : ''}`}>
              <a href="#" className="nav-link" onClick={() => handleNavClick('notifications')}>
                <span className="nav-icon">🔔</span>
                <span className="nav-text">Notifications</span>
              </a>
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-item">
            <a href="#" className="nav-link" onClick={() => handleNavClick('settings')}>
              <span className="nav-icon">⚙️</span>
              <span className="nav-text">Paramètres</span>
            </a>
          </div>
          <div className="sidebar-item">
            <a href="#" className="nav-link" onClick={() => handleNavClick('profile')}>
              <span className="nav-icon">👤</span>
              <span className="nav-text">Profil</span>
            </a>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Top Header */}
        <header className="top-header">
          <div className="search-container">
            <input
              type="text"
              className="search-input"
              placeholder="Rechercher des cours, étudiants..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <span className="search-icon">🔍</span>
          </div>
          <div className="header-actions">
            <button className="btn-primary">Créer</button>
            <div className="user-avatar">
              {user?.name?.charAt(0) || '👤'}
            </div>
          </div>
        </header>

        <div className="content-wrapper">
          {/* Welcome Section */}
          <section className="welcome-section">
            <div className="welcome-content">
              <h1>Bonjour, {user?.name || 'Enseignant'}!</h1>
              <p>Vous avez <strong>3 notifications urgentes</strong> à consulter.</p>
              <button className="btn-notifications">Voir les notifications</button>
            </div>
            <div className="welcome-image">
              <img
                src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 200'%3E%3Crect fill='%23f0f0f0' width='300' height='200' rx='12'/%3E%3Cg fill='%23ccc'%3E%3Crect x='20' y='20' width='60' height='80' rx='8'/%3E%3Crect x='100' y='40' width='80' height='60' rx='8'/%3E%3Crect x='200' y='30' width='70' height='70' rx='8'/%3E%3Cpath fill='%23ddd' d='M250,150 Q270,130 290,150 L290,180 L250,180 Z'/%3E%3C/g%3E%3C/svg%3E"
                alt="Illustration dashboard"
              />
            </div>
          </section>

          {/* Courses Overview */}
          <section className="courses-section">
            <h2>Aperçu des Cours Enseignés</h2>
            <div className="courses-grid">
              {courses.map((course) => (
                <div key={course.id} className="course-card">
                  <div className={`course-image ${course.imageClass}`}>
                    <img
                      src={`data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 200'%3E%3Crect fill='%23c47a00' width='300' height='200' rx='8'/%3E%3C/svg%3E`}
                      alt={course.title}
                    />
                  </div>
                  <div className="course-info">
                    <h3>{course.title}</h3>
                    <div className="course-stats">
                      <span className="students">Étudiants: <strong>{course.students}</strong></span>
                      <span className="average">Moyenne: <strong>{course.average}%</strong></span>
                    </div>
                    <button className="btn-course">Voir le cours</button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Dashboard Management */}
          <section className="dashboard-section">
            <h2>Gestion du Tableau de Bord</h2>

            {/* Students Progress Table */}
            <div className="table-container">
              <div className="table-header">
                <h3>Progression des Étudiants</h3>
                <button className="btn-secondary">Gérer</button>
              </div>
              <div className="table-wrapper">
                <table className="students-table">
                  <thead>
                    <tr>
                      <th>Étudiant</th>
                      <th>Cours</th>
                      <th>Progression</th>
                      <th>Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr key={student.id}>
                        <td>
                          <div className="student-info">
                            <div className="student-avatar">{student.avatar}</div>
                            <span>{student.name}</span>
                          </div>
                        </td>
                        <td>{student.course}</td>
                        <td>
                          <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${student.progress}%` }}></div>
                          </div>
                        </td>
                        <td>
                          <span className={`status-badge ${student.status}`}>
                            {getStatusLabel(student.status)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Analytics Grid */}
            <div className="analytics-grid">
              {/* Class Performance */}
              <div className="analytics-card">
                <h3>Performance des Classes</h3>
                <p className="analytics-subtitle">Moyenne des scores par classe</p>
                <div className="chart-container">
                  <div className="chart-placeholder">📊 Graphique de performance</div>
                </div>
              </div>

              {/* Student Engagement */}
              <div className="analytics-card">
                <h3>Engagement Étudiant</h3>
                <p className="analytics-subtitle">Statut général des étudiants</p>
                <div className="chart-container">
                  <div className="chart-placeholder">📈 Graphique d'engagement</div>
                </div>
              </div>

              {/* Quiz Management */}
              <div className="analytics-card quiz-management">
                <h3>Gestion des Quiz</h3>
                <button className="btn-create-quiz">Créer un quiz</button>
                <div className="quiz-list">
                  {quizzes.map((quiz) => (
                    <div key={quiz.id} className="quiz-item">
                      <div className="quiz-info">
                        <h4>{quiz.title}</h4>
                        <span className="quiz-date">{quiz.date}</span>
                      </div>
                      <span className={`quiz-status ${quiz.status}`}>{quiz.status}</span>
                    </div>
                  ))}
                </div>
                <button className="btn-view-all">Voir tous les quiz</button>
              </div>
            </div>
          </section>

          {/* Bottom Sections */}
          <div className="bottom-sections">
            {/* Resources Section */}
            <section className="resources-section">
              <div className="section-header">
                <h2>Ressources Pédagogiques</h2>
                <button className="btn-add">Ajouter</button>
              </div>
              <div className="resources-list">
                {resources.map((resource) => (
                  <div key={resource.id} className="resource-item">
                    <div className="resource-icon">{resource.icon}</div>
                    <div className="resource-info">
                      <h4>{resource.title}</h4>
                      <span className="resource-type">{resource.type}</span>
                    </div>
                  </div>
                ))}
              </div>
              <button className="btn-view-all">Voir toutes</button>
            </section>

            {/* Notifications Section */}
            <section className="notifications-section">
              <h2>Notifications Importantes</h2>
              <div className="notifications-list">
                {notifications.map((notification) => (
                  <div key={notification.id} className="notification-item">
                    <div className="notification-icon">{notification.icon}</div>
                    <div className="notification-content">
                      <h4>{notification.title}</h4>
                      <span className="notification-date">{notification.date}</span>
                    </div>
                  </div>
                ))}
              </div>
              <button className="btn-view-all">Voir toutes</button>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}

export default InstructorDashboard;