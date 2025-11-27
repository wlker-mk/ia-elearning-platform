// src/pages/Auth/Login.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import '../../styles/auth.css';

function Login() {
  const { login, isLoggingIn } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    remember: false,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login({
        email: formData.email,
        password: formData.password,
      });
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  return (
    <div className="login-container">
      {/* Left Side - Illustration */}
      <div className="illustration-section">
        <div className="illustration-background">
          {/* Sun Rays */}
          <div className="sun-rays">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className={`ray ray-${i}`}></div>
            ))}
          </div>

          {/* Robots */}
          <div className="robot-containers">
            <div className="robot-container left-robot">
              <div className="robot-head">
                <div className="robot-face">
                  <div className="robot-eye left-eye"></div>
                  <div className="robot-eye right-eye"></div>
                  <div className="robot-antenna"></div>
                </div>
              </div>
            </div>

            <div className="robot-container right-robot">
              <div className="robot-head">
                <div className="robot-face">
                  <div className="robot-eye left-eye"></div>
                  <div className="robot-eye right-eye"></div>
                  <div className="robot-antenna"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Central Logo */}
          <div className="central-logo">
            <div className="logo-circle">
              <div className="logo-content">
                <h1 className="logo-title">Ubongo<br />Learn</h1>
                <p className="logo-subtitle">Votre portail vers l'avenir de l'IA</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="form-section">
        <div className="form-container">
          <div className="form-header">
            <h2>Bienvenue sur Ubongo Learn</h2>
            <p>Entrez vos informations pour accéder à votre espace d'apprentissage.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-form-group">
              <label htmlFor="email">Adresse e-mail</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="votre.email@exemple.com"
                required
              />
            </div>

            <div className="auth-form-group">
              <label htmlFor="password">Mot de passe</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="form-options">
              <div className="remember-me">
                <input
                  type="checkbox"
                  id="remember"
                  name="remember"
                  checked={formData.remember}
                  onChange={handleChange}
                />
                <label htmlFor="remember">Se souvenir de moi</label>
              </div>
              <Link to="/forgot-password" className="forgot-password">
                Mot de passe oublié ?
              </Link>
            </div>

            <button type="submit" className="btn-auth" disabled={isLoggingIn}>
              {isLoggingIn ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <div className="divider">
            <span>OU CONTINUEZ AVEC</span>
          </div>

          <div className="social-login">
            <button className="social-btn google-btn">
              <span>🔍</span> Google
            </button>
            <button className="social-btn linkedin-btn">
              <span>💼</span> LinkedIn
            </button>
          </div>

          <div className="signup-link">
            <span>Pas encore de compte ? </span>
            <Link to="/register" className="signup-btn">
              S'inscrire en tant qu'Enseignant ou Apprenant
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;