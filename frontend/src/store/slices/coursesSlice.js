// src/store/slices/coursesSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  list: [],
  featured: [],
  categories: [],
  selectedCourse: null,
  filters: {
    category: null,
    difficulty: null,
    price: null,
    search: '',
  },
  pagination: {
    page: 1,
    perPage: 12,
    total: 0,
  },
  loading: false,
  error: null,
};

const coursesSlice = createSlice({
  name: 'courses',
  initialState,
  reducers: {
    // Définir la liste des cours
    setCourses: (state, action) => {
      state.list = action.payload;
      state.loading = false;
    },

    // Définir les cours mis en avant
    setFeaturedCourses: (state, action) => {
      state.featured = action.payload;
    },

    // Définir les catégories
    setCategories: (state, action) => {
      state.categories = action.payload;
    },

    // Sélectionner un cours
    setSelectedCourse: (state, action) => {
      state.selectedCourse = action.payload;
    },

    // Mettre à jour les filtres
    updateFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },

    // Réinitialiser les filtres
    resetFilters: (state) => {
      state.filters = initialState.filters;
    },

    // Mettre à jour la pagination
    updatePagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
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
  },
});

export const {
  setCourses,
  setFeaturedCourses,
  setCategories,
  setSelectedCourse,
  updateFilters,
  resetFilters,
  updatePagination,
  setLoading,
  setError,
} = coursesSlice.actions;

export default coursesSlice.reducer;

// Sélecteurs
export const selectCourses = (state) => state.courses.list;
export const selectFeaturedCourses = (state) => state.courses.featured;
export const selectCategories = (state) => state.courses.categories;
export const selectSelectedCourse = (state) => state.courses.selectedCourse;
export const selectFilters = (state) => state.courses.filters;