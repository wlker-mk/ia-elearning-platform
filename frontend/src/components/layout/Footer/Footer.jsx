// src/components/layout/Footer/Footer.jsx
import { Link } from 'react-router-dom';
import '../../../styles/layout.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Colonne 1 : À propos */}
        <div className="footer-about">
          <p>Votre passerelle de conseil en IA de qualité.</p>
          <div className="social-icons">
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-facebook"></i>
            </a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-linkedin"></i>
            </a>
            <a href="https://youtube.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-youtube"></i>
            </a>
          </div>
        </div>

        {/* Colonne 2 : Liens rapides */}
        <div className="footer-links">
          <h4>Liens Rapides</h4>
          <ul>
            <li><Link to="/">Accueil</Link></li>
            <li><Link to="/courses">Catalogue de Cours</Link></li>
            <li><Link to="/payment">Paiement</Link></li>
            <li><Link to="/blog">Blog</Link></li>
          </ul>
        </div>

        {/* Colonne 3 : Ressources */}
        <div className="footer-links">
          <h4>Ressources</h4>
          <ul>
            <li><Link to="/documentation">Documentation</Link></li>
            <li><Link to="/api">API</Link></li>
            <li><Link to="/support">Support</Link></li>
            <li><Link to="/faq">FAQ</Link></li>
          </ul>
        </div>

        {/* Colonne 4 : Entreprise */}
        <div className="footer-links">
          <h4>Entreprise</h4>
          <ul>
            <li><Link to="/about">À Propos</Link></li>
            <li><Link to="/careers">Carrières</Link></li>
            <li><Link to="/partners">Partenaires</Link></li>
            <li><Link to="/rgpd">RGPD</Link></li>
          </ul>
        </div>

        {/* Colonne 5 : Contact */}
        <div className="footer-links">
          <h4>Contact</h4>
          <div className="contact-icons">
            <a href="https://wa.me/" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-whatsapp"></i>
            </a>
            <a href="https://tiktok.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-tiktok"></i>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="https://t.me/" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-telegram"></i>
            </a>
            <a href="https://m.me/" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-facebook-messenger"></i>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;