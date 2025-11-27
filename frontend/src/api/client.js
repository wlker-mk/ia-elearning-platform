// src/api/client.js
import axios from 'axios';
import { API_CONFIG } from '../config/api.config';
import { getToken, setToken, clearAuthData } from '../utils/auth';
import { toast } from 'react-toastify';

// Créer l'instance Axios
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // ✅ withCredentials: true pour les cookies (pas nécessaire avec JWT pur)
  // Décommenter si le backend utilise des cookies en plus du JWT
  // withCredentials: true,
});

// ========== REQUEST INTERCEPTOR ==========
apiClient.interceptors.request.use(
  (config) => {
    // Ajouter le token JWT Bearer
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log en développement
    if (import.meta.env.DEV) {
      console.log('🚀 API Request:', {
        method: config.method?.toUpperCase(),
        url: `${config.baseURL}${config.url}`,
        data: config.data,
        headers: config.headers,
      });
    }

    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// ========== RESPONSE INTERCEPTOR ==========
apiClient.interceptors.response.use(
  (response) => {
    // Log en développement
    if (import.meta.env.DEV) {
      console.log('✅ API Response:', {
        url: response.config.url,
        status: response.status,
        data: response.data,
      });
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Log en développement
    if (import.meta.env.DEV) {
      console.error('❌ API Error:', {
        url: error.config?.url,
        status: error.response?.status,
        message: error.response?.data?.message || error.message,
        data: error.response?.data,
      });
    }

    // Gestion des erreurs
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Token expiré ou invalide
          if (!originalRequest._retry) {
            originalRequest._retry = true;

            try {
              // Tentative de refresh du token
              const refreshToken = localStorage.getItem('refresh_token');
              
              if (refreshToken) {
                const response = await axios.post(
                  `${API_CONFIG.BASE_URL}/refresh/`,
                  { refresh_token: refreshToken }
                );
                
                // ✅ Backend retourne: session_token, refresh_token
                const { session_token, refresh_token } = response.data;
                setToken(session_token);
                localStorage.setItem('refresh_token', refresh_token);
                
                // Réessayer la requête originale
                originalRequest.headers.Authorization = `Bearer ${session_token}`;
                return apiClient(originalRequest);
              }
            } catch (refreshError) {
              console.error('Refresh token failed:', refreshError);
              clearAuthData();
              window.location.href = '/login';
              toast.error('Session expirée. Veuillez vous reconnecter.');
              return Promise.reject(refreshError);
            }
          }

          clearAuthData();
          window.location.href = '/login';
          toast.error('Session expirée. Veuillez vous reconnecter.');
          break;

        case 403:
          toast.error('Accès refusé. Permissions insuffisantes.');
          break;

        case 404:
          toast.error('Ressource non trouvée.');
          break;

        case 400:
          // Django REST Framework retourne souvent les erreurs de validation dans data
          if (data.non_field_errors) {
            data.non_field_errors.forEach(err => toast.error(err));
          } else if (typeof data === 'object') {
            Object.entries(data).forEach(([field, errors]) => {
              if (Array.isArray(errors)) {
                errors.forEach(err => toast.error(`${field}: ${err}`));
              }
            });
          } else {
            toast.error(data.detail || 'Erreur de validation.');
          }
          break;

        case 422:
          // Erreurs de validation
          if (data.errors) {
            Object.values(data.errors).forEach((errors) => {
              if (Array.isArray(errors)) {
                errors.forEach((error) => toast.error(error));
              }
            });
          } else {
            toast.error(data.message || 'Erreur de validation.');
          }
          break;

        case 429:
          toast.error('Trop de requêtes. Veuillez patienter.');
          break;

        case 500:
          toast.error('Erreur serveur. Veuillez réessayer.');
          break;

        case 503:
          toast.error('Service temporairement indisponible.');
          break;

        default:
          toast.error(data.detail || data.message || 'Une erreur est survenue.');
      }
    } else if (error.request) {
      // Erreur réseau - backend Django inaccessible
      console.error('Network Error - Backend Django non accessible:', error.request);
      toast.error('Erreur réseau. Vérifiez que le backend Django est démarré.');
    } else {
      // Autre erreur
      toast.error('Une erreur inattendue est survenue.');
    }

    return Promise.reject(error);
  }
);

export default apiClient;