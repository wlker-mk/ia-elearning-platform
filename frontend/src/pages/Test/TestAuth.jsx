// src/pages/Test/TestAuth.jsx
import { useState } from 'react';
import { authService } from '../../api/services';
import apiClient from '../../api/client';

function TestAuth() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);

  // Test de connexion au backend
  const testConnection = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/auth/health/');
      setResults(prev => ({
        ...prev,
        connection: { success: true, data: response.data }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        connection: { success: false, error: error.message }
      }));
    }
    setLoading(false);
  };

  // Test d'inscription
  const testRegister = async () => {
    setLoading(true);
    try {
      const userData = {
        firstName: 'Test',
        lastName: 'User',
        email: `test_${Date.now()}@example.com`,
        password: 'TestPassword123!',
        role: 'STUDENT'
      };
      
      const response = await authService.register(userData);
      setResults(prev => ({
        ...prev,
        register: { success: true, data: response }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        register: { 
          success: false, 
          error: error.response?.data || error.message 
        }
      }));
    }
    setLoading(false);
  };

  // Test de connexion
  const testLogin = async () => {
    setLoading(true);
    try {
      const credentials = {
        email: 'test@example.com',
        password: 'TestPassword123!'
      };
      
      const response = await authService.login(credentials);
      setResults(prev => ({
        ...prev,
        login: { success: true, data: response }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        login: { 
          success: false, 
          error: error.response?.data || error.message 
        }
      }));
    }
    setLoading(false);
  };

  // Test de déconnexion
  const testLogout = async () => {
    setLoading(true);
    try {
      await authService.logout();
      setResults(prev => ({
        ...prev,
        logout: { success: true }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        logout: { 
          success: false, 
          error: error.response?.data || error.message 
        }
      }));
    }
    setLoading(false);
  };

  // Test route protégée
  const testProtectedRoute = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/users/profile');
      setResults(prev => ({
        ...prev,
        protected: { success: true, data: response.data }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        protected: { 
          success: false, 
          error: error.response?.data || error.message 
        }
      }));
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '30px', color: '#2c3e50' }}>
        🧪 Tests d'Authentification - Backend Django
      </h1>

      <div style={{ display: 'grid', gap: '20px', marginBottom: '40px' }}>
        <button
          onClick={testConnection}
          disabled={loading}
          style={{
            padding: '15px 30px',
            backgroundColor: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          1️⃣ Test Connexion Backend
        </button>

        <button
          onClick={testRegister}
          disabled={loading}
          style={{
            padding: '15px 30px',
            backgroundColor: '#27ae60',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          2️⃣ Test Inscription (Register)
        </button>

        <button
          onClick={testLogin}
          disabled={loading}
          style={{
            padding: '15px 30px',
            backgroundColor: '#e67e22',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          3️⃣ Test Connexion (Login)
        </button>

        <button
          onClick={testProtectedRoute}
          disabled={loading}
          style={{
            padding: '15px 30px',
            backgroundColor: '#9b59b6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          4️⃣ Test Route Protégée
        </button>

        <button
          onClick={testLogout}
          disabled={loading}
          style={{
            padding: '15px 30px',
            backgroundColor: '#e74c3c',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          5️⃣ Test Déconnexion (Logout)
        </button>

        <button
          onClick={() => setResults({})}
          style={{
            padding: '10px 20px',
            backgroundColor: '#95a5a6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          🗑️ Effacer les résultats
        </button>
      </div>

      {/* Résultats */}
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '30px', 
        borderRadius: '12px',
        fontFamily: 'monospace',
        fontSize: '14px'
      }}>
        <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>
          📊 Résultats des tests
        </h2>
        
        {Object.keys(results).length === 0 ? (
          <p style={{ color: '#7f8c8d' }}>Aucun test exécuté pour le moment</p>
        ) : (
          <pre style={{ 
            whiteSpace: 'pre-wrap', 
            wordWrap: 'break-word',
            backgroundColor: '#2c3e50',
            color: '#ecf0f1',
            padding: '20px',
            borderRadius: '8px',
            overflow: 'auto'
          }}>
            {JSON.stringify(results, null, 2)}
          </pre>
        )}
      </div>

      {/* Informations de configuration */}
      <div style={{ 
        marginTop: '30px',
        padding: '20px',
        backgroundColor: '#fff3cd',
        border: '1px solid #ffc107',
        borderRadius: '8px'
      }}>
        <h3 style={{ marginBottom: '10px', color: '#856404' }}>
          ⚙️ Configuration actuelle
        </h3>
        <p style={{ margin: '5px 0', color: '#856404' }}>
          <strong>Backend URL:</strong> {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}
        </p>
        <p style={{ margin: '5px 0', color: '#856404' }}>
          <strong>Mode:</strong> {import.meta.env.DEV ? 'Développement' : 'Production'}
        </p>
      </div>
    </div>
  );
}

export default TestAuth;