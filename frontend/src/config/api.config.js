// src/config/api.config.js
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/auth',
  TIMEOUT: 30000,
};

// ✅ ENDPOINTS CONFIRMÉS PAR LE BACKEND
export const API_ENDPOINTS = {
  AUTH: {
    // Base endpoints
    LOGIN: '/login/',
    REGISTER: '/register/',
    LOGOUT: '/logout/',
    REFRESH: '/refresh/',
    VERIFY_EMAIL: '/verify-email/',
    ME: '/me/',
    
    // Password management
    FORGOT_PASSWORD: '/password/request-reset/',
    RESET_PASSWORD: '/password/reset/',
    CHANGE_PASSWORD: '/password/change/',
    
    // MFA
    MFA_ENABLE: '/mfa/enable/',
    MFA_VERIFY: '/mfa/verify/',
    MFA_DISABLE: '/mfa/disable/',
    MFA_BACKUP_CODES: '/mfa/backup-codes/',
    
    // Login with MFA
    LOGIN_MFA: '/login/mfa/',
    
    // OAuth
    OAUTH_GOOGLE: '/oauth/google/',
    OAUTH_GITHUB: '/oauth/github/',
    OAUTH_LINK: '/oauth/link/',
    OAUTH_UNLINK: '/oauth/unlink/',
  },
  
  // Sessions management
  SESSIONS: {
    LIST: '/sessions/',
    DELETE: (id) => `/sessions/${id}/`,
    DELETE_ALL: '/sessions/',
  },
  
  // Login history
  LOGIN_HISTORY: '/login-history/',
  LOGIN_STATISTICS: '/login-statistics/',
  
  // Health check
  HEALTH: '/health/',
  
  COURSES: {
    LIST: '/courses/',
    DETAILS: (id) => `/courses/${id}/`,
    CATEGORIES: '/courses/categories/',
    WISHLIST: '/courses/wishlist/',
  },
  
  USERS: {
    PROFILE: '/users/profile/',
    UPDATE_PROFILE: '/users/profile/',
  },
  
  ENROLLMENTS: {
    ENROLL: '/enrollments/',
    MY_COURSES: '/enrollments/my-courses/',
  },
};

/**
 * ❌ CSRF Token non nécessaire avec JWT
 * Le backend utilise JWT Bearer Token, pas de CSRF protection
 */