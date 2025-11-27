// src/components/layout/Header/Header.jsx
import { Link, NavLink } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectIsAuthenticated, selectUser } from '../../../store/slices/authSlice';
import { useAuth } from '../../../hooks/useAuth';
import logo from '../../../assets/images/logo.png';
import '../../../styles/layout.css';

function Header() {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);
  const { logout } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Voulez-vous vraiment vous déconnecter ?')) {
      logout();
    }
  };

  return (
    <header className="header-container">
      {/* Logo */}
      <Link to="/" className="header-logo">
        <img src={logo} alt="Logo Ubongo" />
        <span>| Ubongo</span>
      </Link>

      {/* Navigation */}
      <nav className="header-nav">
        <ul>
          <li>
            <NavLink 
              to="/" 
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Accueil
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/courses" 
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Catalogue de Cours
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/instructors" 
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Nos Enseignants
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/about" 
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              À propos
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/community" 
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Communauté
            </NavLink>
          </li>
        </ul>
      </nav>

      {/* Auth Section */}
      <div className="header-auth">
        <input 
          type="text" 
          placeholder="Rechercher cours, experts…"
        />
        
        {isAuthenticated ? (
          <div className="user-menu">
            <button onClick={handleLogout} className="btn-login">
              Déconnexion
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn-login">
            Connexion / Inscription
          </Link>
        )}
      </div>
    </header>
  );
}

export default Header;