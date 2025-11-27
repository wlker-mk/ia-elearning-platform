// src/utils/auth.js

// Clés de stockage
const TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';
const USER_KEY = 'user';

// ========== TOKEN MANAGEMENT ==========

/**
 * Sauvegarder le token d'accès
 */
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Récupérer le token d'accès
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Supprimer le token d'accès
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * Vérifier si l'utilisateur est authentifié
 */
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;

  try {
    // Décoder le JWT pour vérifier l'expiration
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expirationTime = payload.exp * 1000;
    return Date.now() < expirationTime;
  } catch (error) {
    console.error('Erreur lors du décodage du token:', error);
    return false;
  }
};

// ========== REFRESH TOKEN ==========

export const setRefreshToken = (token) => {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const removeRefreshToken = () => {
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// ========== USER MANAGEMENT ==========

/**
 * Sauvegarder les données utilisateur
 */
export const setUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

/**
 * Récupérer les données utilisateur
 */
export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;

  try {
    return JSON.parse(userStr);
  } catch (error) {
    console.error('Erreur parsing user:', error);
    return null;
  }
};

/**
 * Supprimer les données utilisateur
 */
export const removeUser = () => {
  localStorage.removeItem(USER_KEY);
};

// ========== SESSION MANAGEMENT ==========

/**
 * Sauvegarder toutes les données de session
 */
export const setAuthData = (data) => {
  setToken(data.token);
  setRefreshToken(data.refreshToken);
  setUser(data.user);
};

/**
 * Effacer toutes les données de session (logout)
 */
export const clearAuthData = () => {
  removeToken();
  removeRefreshToken();
  removeUser();
  localStorage.removeItem('cart');
  sessionStorage.clear();
};

// ========== ROLE CHECKING ==========

/**
 * Vérifier si l'utilisateur a un rôle spécifique
 */
export const hasRole = (role) => {
  const user = getUser();
  if (!user) return false;

  if (Array.isArray(role)) {
    return role.includes(user.role);
  }

  return user.role === role;
};

export const isStudent = () => hasRole('STUDENT');
export const isInstructor = () => hasRole('INSTRUCTOR');
export const isAdmin = () => hasRole(['ADMIN', 'SUPER_ADMIN']);