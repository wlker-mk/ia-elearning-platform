// src/store/slices/userSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  profile: null,
  preferences: {
    theme: 'light',
    language: 'fr',
    notifications: true,
  },
  stats: {
    coursesEnrolled: 0,
    coursesCompleted: 0,
    totalPoints: 0,
    currentStreak: 0,
  },
  loading: false,
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    // Charger le profil
    setProfile: (state, action) => {
      state.profile = action.payload;
      state.loading = false;
    },

    // Mettre à jour le profil
    updateProfile: (state, action) => {
      state.profile = { ...state.profile, ...action.payload };
    },

    // Mettre à jour les préférences
    updatePreferences: (state, action) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },

    // Mettre à jour les stats
    updateStats: (state, action) => {
      state.stats = { ...state.stats, ...action.payload };
    },

    // Loading
    setLoading: (state, action) => {
      state.loading = action.payload;
    },

    // Erreur
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },

    // Réinitialiser
    resetUser: (state) => {
      return initialState;
    },
  },
});

export const {
  setProfile,
  updateProfile,
  updatePreferences,
  updateStats,
  setLoading,
  setError,
  resetUser,
} = userSlice.actions;

export default userSlice.reducer;

// Sélecteurs
export const selectProfile = (state) => state.user.profile;
export const selectPreferences = (state) => state.user.preferences;
export const selectStats = (state) => state.user.stats;
export const selectTheme = (state) => state.user.preferences.theme;