// src/api/services/courses.service.js
import apiClient from '../client';
import { API_ENDPOINTS } from '../../config/api.config';

const coursesService = {
  /**
   * Récupérer la liste des cours
   */
  getCourses: async (params = {}) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.COURSES.LIST, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Récupérer les détails d'un cours
   */
  getCourseById: async (id) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.COURSES.DETAILS(id));
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Créer un cours
   */
  createCourse: async (courseData) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.COURSES.LIST, courseData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Mettre à jour un cours
   */
  updateCourse: async (id, courseData) => {
    try {
      const response = await apiClient.put(
        API_ENDPOINTS.COURSES.DETAILS(id),
        courseData
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Supprimer un cours
   */
  deleteCourse: async (id) => {
    try {
      const response = await apiClient.delete(API_ENDPOINTS.COURSES.DETAILS(id));
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Récupérer les catégories
   */
  getCategories: async () => {
    try {
      const response = await apiClient.get('/courses/categories');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Ajouter à la wishlist
   */
  addToWishlist: async (courseId) => {
    try {
      const response = await apiClient.post('/courses/wishlist', { courseId });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Retirer de la wishlist
   */
  removeFromWishlist: async (courseId) => {
    try {
      const response = await apiClient.delete(`/courses/wishlist/${courseId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default coursesService;