// src/pages/Community/Community.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/community.css';

function Community() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  // Données des catégories
  const categories = [
    { id: 1, icon: '📚', title: 'Tutoriels & Guides', description: 'Apprenez les bases et les astuces de l\'IA.' },
    { id: 2, icon: '💻', title: 'Projets & Code', description: 'Partagez vos projets et obtenez de l\'aide.' },
    { id: 3, icon: '💡', title: 'Idées & Innovations', description: 'Discutez des dernières tendances de l\'IA.' },
    { id: 4, icon: '❓', title: 'Questions Générales', description: 'Posez vos questions et échangez avec la communauté.' },
    { id: 5, icon: '📈', title: 'Carrières en IA', description: 'Conseils et opportunités dans le domaine de l\'IA.' },
    { id: 6, icon: '🏆', title: 'Défis & Compétitions', description: 'Relevez nos hackathons et défis d\'apprentissage.' }
  ];

  // Données des discussions
  const discussions = [
    {
      id: 1,
      avatar: '👨‍💻',
      title: 'Comment démarrer avec le Machine Learning ?',
      author: 'Alex',
      category: 'Tutoriels & Guides',
      time: '2 heures',
      likes: 15,
      comments: 7
    },
    {
      id: 2,
      avatar: '👩‍🔬',
      title: 'Optimisation des modèles GPT-3 pour les langues africaines',
      author: 'Sarah',
      category: 'Projets & Code',
      time: 'Hier',
      likes: 32,
      comments: 12
    },
    {
      id: 3,
      avatar: '👨‍🎓',
      title: 'Meilleures bibliothèques Python pour l\'analyse de données',
      author: 'Mohamed',
      category: 'Questions Générales',
      time: '3 jours',
      likes: 21,
      comments: 5
    },
    {
      id: 4,
      avatar: '👩‍💼',
      title: 'L\'éthique de l\'IA en Afrique: Défis et opportunités',
      author: 'Fatima',
      category: 'Idées & Innovations',
      time: '5 jours',
      likes: 45,
      comments: 18
    }
  ];

  // Données du leaderboard
  const leaderboard = [
    { rank: 1, avatar: '👑', username: 'Ngozi Okafor', points: 1250, rankClass: 'rank-1', trophy: '🏆' },
    { rank: 2, avatar: '🥈', username: 'Chukwuma Eze', points: 1120, rankClass: 'rank-2' },
    { rank: 3, avatar: '🥉', username: 'Zola Ndlovu', points: 980, rankClass: 'rank-3' },
    { rank: 4, avatar: '👨‍💼', username: 'Amara Okoro', points: 870, rankClass: '' },
    { rank: 5, avatar: '👩‍🔬', username: 'Tariq Hassan', points: 750, rankClass: '' }
  ];

  // Données des badges
  const badges = [
    { id: 1, icon: '🔍', title: 'Explorateur IA', description: 'Termine 5 cours d\'introduction', earned: true },
    { id: 2, icon: '⚙️', title: 'Maître du Code', description: 'Contribue à 10 projets open source', earned: true },
    { id: 3, icon: '🧠', title: 'Génie de l\'Apprentissage', description: 'Obtiens un score de 90%+ dans 5 modules avancés', earned: false },
    { id: 4, icon: '🤝', title: 'Collaborateur Communautaire', description: 'Participe à 30 discussions sur le forum', earned: false }
  ];

  // Données des challenges
  const challenges = [
    {
      id: 1,
      title: 'Hackathon IA pour le Climat',
      description: 'Développez des solutions d\'IA pour lutter contre le changement climatique en Afrique. Prix à gagner !',
      buttonText: 'Participer au défi',
      color: '#4A90E2'
    },
    {
      id: 2,
      title: 'Défi de Reconnaissance d\'Images',
      description: 'Améliorez la précision des modèles de reconnaissance d\'images pour la faune africaine',
      buttonText: 'Voir les détails',
      color: '#FF9500'
    }
  ];

  const handleStartDiscussion = () => {
    console.log('Démarrer une discussion');
    // Logique pour créer une discussion
  };

  const handleAskQuestion = () => {
    console.log('Poser une question');
    // Logique pour poser une question
  };

  const handleCategoryClick = (categoryId) => {
    console.log('Catégorie cliquée:', categoryId);
    // Navigation vers la catégorie
  };

  const handleDiscussionClick = (discussionId) => {
    console.log('Discussion cliquée:', discussionId);
    // Navigation vers la discussion
  };

  const handleChallengeClick = (challengeId) => {
    console.log('Challenge cliqué:', challengeId);
    // Navigation vers le challenge
  };

  return (
    <div className="community-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>Engagez-vous, apprenez et gagnez!</h1>
            <p>
              Rejoignez notre communauté dynamique, participez à des discussions stimulantes, 
              testez vos compétences et suivez votre progression sur le tableau de bord de gamification.
            </p>
            <div className="hero-actions">
              <div className="search-bar">
                <input
                  type="text"
                  placeholder="Rechercher des discussions ou des défis..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <span className="search-icon">🔍</span>
              </div>
              <button className="btn-primary" onClick={handleStartDiscussion}>
                Démarrer une discussion
              </button>
              <button className="btn-secondary" onClick={handleAskQuestion}>
                Poser une question
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          <div className="content-layout">
            {/* Left Column */}
            <div className="left-column">
              {/* Discussion Categories */}
              <section className="categories">
                <h2>Catégories de discussion</h2>
                <div className="categories-grid">
                  {categories.map((category) => (
                    <div
                      key={category.id}
                      className="category-card"
                      onClick={() => handleCategoryClick(category.id)}
                    >
                      <div className="category-icon">{category.icon}</div>
                      <h3>{category.title}</h3>
                      <p>{category.description}</p>
                    </div>
                  ))}
                </div>
              </section>

              {/* Recent Discussions */}
              <section className="recent-discussions">
                <h2>Discussions récentes</h2>
                <div className="discussion-list">
                  {discussions.map((discussion) => (
                    <div
                      key={discussion.id}
                      className="discussion-item"
                      onClick={() => handleDiscussionClick(discussion.id)}
                    >
                      <div className="discussion-avatar">{discussion.avatar}</div>
                      <div className="discussion-content">
                        <h3>{discussion.title}</h3>
                        <p className="discussion-meta">
                          <span className="author">Par {discussion.author}</span>
                          <span className="category">dans {discussion.category}</span>
                          <span className="time">{discussion.time}</span>
                        </p>
                        <div className="discussion-stats">
                          <span>👍 {discussion.likes}</span>
                          <span>💬 {discussion.comments}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* Right Column */}
            <div className="right-column">
              {/* Leaderboard */}
              <section className="leaderboard">
                <h2>Classement des apprenants</h2>
                <div className="leaderboard-list">
                  {leaderboard.map((user) => (
                    <div key={user.rank} className={`leaderboard-item ${user.rankClass}`}>
                      <span className="rank">{user.rank}.</span>
                      <div className="user-avatar">{user.avatar}</div>
                      <div className="user-info">
                        <span className="username">{user.username}</span>
                        <span className="points">
                          {user.points} points {user.trophy || ''}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Badges Section */}
              <section className="badges">
                <h2>Vos Badges</h2>
                <div className="badges-grid">
                  {badges.map((badge) => (
                    <div key={badge.id} className={`badge-item ${badge.earned ? 'earned' : ''}`}>
                      <div className="badge-icon">{badge.icon}</div>
                      <div className="badge-info">
                        <h4>{badge.title}</h4>
                        <p>{badge.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Challenges Section */}
              <section className="challenges">
                <h2>Défis et Compétitions</h2>
                <div className="challenges-list">
                  {challenges.map((challenge) => (
                    <div key={challenge.id} className="challenge-card">
                      <div className="challenge-image">
                        <img
                          src={`data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 150'%3E%3Crect fill='${encodeURIComponent(challenge.color)}' width='300' height='150' rx='8'/%3E%3C/svg%3E`}
                          alt={challenge.title}
                        />
                      </div>
                      <div className="challenge-content">
                        <h3>{challenge.title}</h3>
                        <p>{challenge.description}</p>
                        <button
                          className="btn-challenge"
                          onClick={() => handleChallengeClick(challenge.id)}
                        >
                          {challenge.buttonText}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Community;