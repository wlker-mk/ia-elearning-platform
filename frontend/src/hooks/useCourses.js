// src/hooks/useCourses.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { coursesService } from '../api/services';
import { toast } from 'react-toastify';

// Hook pour récupérer la liste des cours
export const useCourses = (params = {}) => {
  return useQuery({
    queryKey: ['courses', params],
    queryFn: () => coursesService.getCourses(params),
    select: (data) => data.data, // Extraire les données
  });
};

// Hook pour récupérer un cours par ID
export const useCourse = (id) => {
  return useQuery({
    queryKey: ['course', id],
    queryFn: () => coursesService.getCourseById(id),
    enabled: !!id, // Ne lance la requête que si l'ID existe
    select: (data) => data.data,
  });
};

// Hook pour créer un cours
export const useCreateCourse = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (courseData) => coursesService.createCourse(courseData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
      toast.success('Cours créé avec succès !');
    },
    onError: (error) => {
      toast.error('Erreur lors de la création du cours');
    },
  });
};

// Hook pour ajouter à la wishlist
export const useAddToWishlist = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (courseId) => coursesService.addToWishlist(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      toast.success('Ajouté à la wishlist !');
    },
  });
};