// src/api/services/auth.service.js
import apiClient from '../client';
import { API_ENDPOINTS } from '../../config/api.config';
import { setAuthData, clearAuthData } from '../../utils/auth';

const authService = {
  /**
   * Connexion
   * Backend retourne: { user, access_token, refresh_token, expires_at, message }
   * Ou si MFA: { requires_mfa: true, user_id, message }
   */
  login: async (credentials) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
        email: credentials.email,
        password: credentials.password,
        remember_me: credentials.remember_me || false
      });
      
      // Cas 1: MFA requis
      if (response.data.requires_mfa) {
        return {
          requiresMFA: true,
          userId: response.data.user_id,
          message: response.data.message
        };
      }
      
      // Cas 2: Connexion réussie
      if (response.data.access_token) {
        setAuthData({
          token: response.data.access_token,
          refreshToken: response.data.refresh_token,
          user: response.data.user,
        });
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Connexion avec MFA
   */
  loginWithMFA: async (email, password, mfaCode) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN_MFA, {
        email,
        password,
        mfa_code: mfaCode
      });
      
      if (response.data.access_token) {
        setAuthData({
          token: response.data.access_token,
          refreshToken: response.data.refresh_token,
          user: response.data.user,
        });
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Inscription
   * Backend attend: { email, username, password, password_confirm, role }
   */
  register: async (userData) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, {
        email: userData.email,
        username: userData.username || userData.email.split('@')[0],
        password: userData.password,
        password_confirm: userData.password_confirm || userData.password,
        role: userData.role || 'STUDENT'
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Déconnexion
   */
  logout: async () => {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
      clearAuthData();
    } catch (error) {
      // Même en cas d'erreur, on déconnecte localement
      clearAuthData();
      throw error;
    }
  },

  /**
   * Vérifier l'email
   */
  verifyEmail: async (token) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.VERIFY_EMAIL, { 
        token 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Mot de passe oublié
   */
  forgotPassword: async (email) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, { 
        email 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Réinitialiser le mot de passe
   */
  resetPassword: async (token, newPassword, newPasswordConfirm) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, {
        token,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Changer le mot de passe (connecté)
   */
  changePassword: async (currentPassword, newPassword, newPasswordConfirm) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, {
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Obtenir l'utilisateur actuel
   */
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.AUTH.ME);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Rafraîchir le token
   */
  refreshToken: async (refreshToken) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH, {
        refresh_token: refreshToken
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // ========== MFA ==========

  /**
   * Activer MFA (Étape 1)
   * Retourne: { secret, qr_code, backup_codes, message }
   */
  enableMFA: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.MFA_ENABLE);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Vérifier et activer MFA (Étape 2)
   */
  verifyMFA: async (code) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.MFA_VERIFY, {
        code
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Désactiver MFA
   */
  disableMFA: async (password) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.MFA_DISABLE, {
        password
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Régénérer les codes de backup
   */
  regenerateBackupCodes: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.MFA_BACKUP_CODES);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // ========== SESSIONS ==========

  /**
   * Obtenir toutes les sessions actives
   */
  getSessions: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.AUTH.SESSIONS.LIST);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Révoquer une session spécifique
   */
  revokeSession: async (sessionId) => {
    try {
      const response = await apiClient.delete(
        API_ENDPOINTS.AUTH.SESSIONS.DELETE(sessionId)
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Révoquer toutes les sessions sauf la courante
   */
  revokeAllSessions: async () => {
    try {
      const response = await apiClient.delete(
        API_ENDPOINTS.AUTH.SESSIONS.DELETE_ALL
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // ========== OAUTH ==========

  /**
   * Connexion Google
   */
  loginWithGoogle: async (code, redirectUri) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.OAUTH_GOOGLE, {
        code,
        redirect_uri: redirectUri
      });
      
      if (response.data.access_token) {
        setAuthData({
          token: response.data.access_token,
          refreshToken: response.data.refresh_token,
          user: response.data.user,
        });
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Connexion GitHub
   */
  loginWithGitHub: async (code) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.OAUTH_GITHUB, {
        code
      });
      
      if (response.data.access_token) {
        setAuthData({
          token: response.data.access_token,
          refreshToken: response.data.refresh_token,
          user: response.data.user,
        });
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Lier un compte OAuth
   */
  linkOAuthAccount: async (provider, code, redirectUri) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.OAUTH_LINK, {
        provider,
        code,
        redirect_uri: redirectUri
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Délier un compte OAuth
   */
  unlinkOAuthAccount: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.OAUTH_UNLINK);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default authService;