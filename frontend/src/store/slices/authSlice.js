// src/store/slices/authSlice.js
import { createSlice } from '@reduxjs/toolkit';
import { getToken, getUser, isAuthenticated } from '../../utils/auth';

const initialState = {
  isAuthenticated: isAuthenticated(),
  user: getUser(),
  token: getToken(),
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Connexion réussie
    loginSuccess: (state, action) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.loading = false;
      state.error = null;
    },

    // Connexion en cours
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },

    // Échec de connexion
    loginFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },

    // Déconnexion
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.loading = false;
      state.error = null;
    },

    // Mettre à jour l'utilisateur
    updateUser: (state, action) => {
      state.user = { ...state.user, ...action.payload };
    },

    // Réinitialiser l'erreur
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  loginSuccess,
  loginStart,
  loginFailure,
  logout,
  updateUser,
  clearError,
} = authSlice.actions;

export default authSlice.reducer;

// Sélecteurs
export const selectAuth = (state) => state.auth;
export const selectUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;