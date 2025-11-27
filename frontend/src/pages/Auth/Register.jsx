// src/pages/Auth/Register.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../../styles/auth.css';

function Register() {
  const [activeTab, setActiveTab] = useState('enseignant');
  const [formData, setFormData] = useState({
    firstName: '',
    email: '',
    password: '',
    confirmPassword: '',
    niveauEtude: '',
    cv: null,
  });

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    // Réinitialiser le formulaire
    setFormData({
      firstName: '',
      email: '',
      password: '',
      confirmPassword: '',
      niveauEtude: '',
      cv: null,
    });
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData({
      ...formData,
      [name]: files ? files[0] : value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert('Les mots de passe ne correspondent pas !');
      return;
    }

    console.log('Inscription:', {
      role: activeTab,
      ...formData,
    });
  };

  return (
    <div className="register-container">
      <div className="register-form-container">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">
          Créer un compte
        </h1>

        {/* Tabs */}
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'enseignant' ? 'active' : ''}`}
            onClick={() => handleTabClick('enseignant')}
          >
            Enseignant
          </button>
          <button
            className={`tab-btn ${activeTab === 'etudiant' ? 'active' : ''}`}
            onClick={() => handleTabClick('etudiant')}
          >
            Étudiant
          </button>
        </div>

        {/* Formulaire Enseignant */}
        <form
          className={`register-form ${activeTab === 'enseignant' ? 'active' : ''}`}
          onSubmit={handleSubmit}
        >
          <input
            type="text"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            placeholder="Nom complet"
            required
          />
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email professionnel"
            required
          />
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Mot de passe"
            required
          />
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="Confirmer le mot de passe"
            required
          />

          <div className="file-upload">
            <label htmlFor="cv">Télécharger votre CV (PDF)</label>
            <input
              type="file"
              id="cv"
              name="cv"
              accept=".pdf"
              onChange={handleChange}
            />
          </div>

          <button type="submit" className="btn-auth">
            S'inscrire en tant qu'Enseignant
          </button>
        </form>

        {/* Formulaire Étudiant */}
        <form
          className={`register-form ${activeTab === 'etudiant' ? 'active' : ''}`}
          onSubmit={handleSubmit}
        >
          <input
            type="text"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            placeholder="Nom complet"
            required
          />
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email étudiant"
            required
          />
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Mot de passe"
            required
          />
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="Confirmer le mot de passe"
            required
          />
          <input
            type="text"
            name="niveauEtude"
            value={formData.niveauEtude}
            onChange={handleChange}
            placeholder="Niveau d'étude"
            required
          />

          <button type="submit" className="btn-auth">
            S'inscrire en tant qu'Étudiant
          </button>
        </form>

        <div className="signup-link mt-4">
          <span>Déjà un compte ? </span>
          <Link to="/login" className="signup-btn">
            Se connecter
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;