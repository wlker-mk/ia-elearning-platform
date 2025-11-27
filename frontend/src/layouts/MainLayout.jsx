// src/layouts/MainLayout.jsx
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import '../styles/layout.css';

function MainLayout({ children }) {
  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        {children}
      </main>
      <Footer />
    </div>
  );
}

export default MainLayout;