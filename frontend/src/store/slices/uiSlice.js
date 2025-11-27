// src/store/slices/uiSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  sidebarOpen: false,
  modalOpen: false,
  modalContent: null,
  theme: localStorage.getItem('theme') || 'light',
  language: localStorage.getItem('language') || 'fr',
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Toggle sidebar
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },

    // Ouvrir modal
    openModal: (state, action) => {
      state.modalOpen = true;
      state.modalContent = action.payload;
    },

    // Fermer modal
    closeModal: (state) => {
      state.modalOpen = false;
      state.modalContent = null;
    },

    // Changer le thème
    setTheme: (state, action) => {
      state.theme = action.payload;
      localStorage.setItem('theme', action.payload);
    },

    // Changer la langue
    setLanguage: (state, action) => {
      state.language = action.payload;
      localStorage.setItem('language', action.payload);
    },
  },
});

export const {
  toggleSidebar,
  openModal,
  closeModal,
  setTheme,
  setLanguage,
} = uiSlice.actions;

export default uiSlice.reducer;

// Sélecteurs
export const selectSidebarOpen = (state) => state.ui.sidebarOpen;
export const selectModalOpen = (state) => state.ui.modalOpen;
export const selectModalContent = (state) => state.ui.modalContent;
export const selectTheme = (state) => state.ui.theme;
export const selectLanguage = (state) => state.ui.language;