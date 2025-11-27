// src/pages/Dashboard/AdminDashboard.jsx
import { useState } from 'react';
import { useSelector } from 'react-redux';
import { selectUser } from '../../store/slices/authSlice';
import '../../styles/dashboard.css';

function AdminDashboard() {
  const user = useSelector(selectUser);
  const [selectedReport, setSelectedReport] = useState('');

  // Statistiques
  const stats = [
    {
      icon: '👥',
      number: '15,345',
      label: 'Total Utilisateurs',
      change: '+25% depuis le mois dernier',
    },
    {
      icon: '📚',
      number: '120',
      label: 'Total Cours',
      change: '+5 nouveaux cours',
    },
    {
      icon: '✏️',
      number: '250',
      label: 'Inscriptions Cette Semaine',
      change: '+12% par rapport à la semaine dernière',
    },
  ];

  // Actions administratives
  const actions = [
    {
      icon: '👥',
      title: 'Gestion des Utilisateurs',
      description: 'Gérez les comptes utilisateurs, les rôles, les permissions et surveillez l\'activité.',
      buttonText: 'Voir les Utilisateurs',
      onClick: () => console.log('Navigation vers gestion utilisateurs'),
    },
    {
      icon: '📚',
      title: 'Gestion des Cours',
      description: 'Ajoutez, modifiez ou supprimez des modules de cours, gérez le contenu et les instructeurs.',
      buttonText: 'Gérer les Cours',
      onClick: () => console.log('Navigation vers gestion cours'),
    },
  ];

  // Options de rapports
  const reportOptions = [
    { value: '', label: 'Sélectionner un rapport' },
    { value: 'users', label: 'Rapport d\'activité utilisateurs' },
    { value: 'courses', label: 'Statistiques des cours' },
    { value: 'financial', label: 'Rapport financier' },
  ];

  const handleGenerateReport = () => {
    if (!selectedReport) {
      alert('Veuillez sélectionner un type de rapport');
      return;
    }
    console.log('Génération du rapport:', selectedReport);
    alert(`Génération du rapport : ${reportOptions.find(r => r.value === selectedReport)?.label}`);
  };

  return (
    <main className="main-content">
      <h1 className="page-title">Tableau de Bord Administratif</h1>

      {/* Statistiques */}
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-content">
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
              <div className="stat-change">{stat.change}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Actions rapides */}
      <div className="action-grid">
        {actions.map((action, index) => (
          <div key={index} className="action-card">
            <div className="action-icon">{action.icon}</div>
            <div className="action-content">
              <h3 className="action-title">{action.title}</h3>
              <p className="action-description">{action.description}</p>
              <button className="action-btn" onClick={action.onClick}>
                {action.buttonText}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Graphiques */}
      <div className="charts-grid">
        <div className="chart-container">
          <h3 className="chart-title">Croissance des Utilisateurs</h3>
          <div className="chart-placeholder">
            📊 Graphique de croissance
            <br />
            <small>(Chart.js sera intégré ici)</small>
          </div>
        </div>

        <div className="chart-container">
          <h3 className="chart-title">Inscriptions aux Cours</h3>
          <div className="chart-placeholder">
            📈 Graphique d'inscriptions
            <br />
            <small>(Chart.js sera intégré ici)</small>
          </div>
        </div>
      </div>

      {/* Section Rapports */}
      <div className="reports-section">
        <h3 className="reports-title">Générer des Rapports</h3>
        <p className="reports-description">
          Sélectionnez un type de rapport pour exporter les données de la plateforme.
        </p>
        <div className="reports-controls">
          <select
            className="report-select"
            value={selectedReport}
            onChange={(e) => setSelectedReport(e.target.value)}
          >
            {reportOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button className="generate-btn" onClick={handleGenerateReport}>
            Générer le Rapport
          </button>
        </div>
      </div>
    </main>
  );
}

export default AdminDashboard;