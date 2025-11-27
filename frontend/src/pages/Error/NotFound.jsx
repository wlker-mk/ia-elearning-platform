// src/pages/Error/NotFound.jsx
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-gray-300 mb-4">404</h1>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Page non trouvée
        </h2>
        <p className="text-gray-600 mb-8 text-lg">
          Désolé, la page que vous recherchez n'existe pas ou a été déplacée.
        </p>
        
        <div className="flex gap-4 justify-center flex-wrap">
          <Link
            to="/"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Retour à l'accueil
          </Link>
          <Link
            to="/courses"
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Voir les cours
          </Link>
        </div>

        <div className="mt-12 text-6xl">
          🤔
        </div>
      </div>
    </div>
  );
}

export default NotFound;