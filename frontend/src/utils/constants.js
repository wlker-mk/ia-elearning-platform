// src/utils/constants.js

// Rôles utilisateurs
export const USER_ROLES = {
  STUDENT: 'STUDENT',
  INSTRUCTOR: 'INSTRUCTOR',
  ADMIN: 'ADMIN',
  SUPER_ADMIN: 'SUPER_ADMIN',
};

// Statuts des cours
export const COURSE_STATUS = {
  DRAFT: 'DRAFT',
  PUBLISHED: 'PUBLISHED',
  ARCHIVED: 'ARCHIVED',
};

// Difficultés des cours
export const COURSE_DIFFICULTY = {
  BEGINNER: 'BEGINNER',
  INTERMEDIATE: 'INTERMEDIATE',
  ADVANCED: 'ADVANCED',
  EXPERT: 'EXPERT',
};

// Statuts d'inscription
export const ENROLLMENT_STATUS = {
  ACTIVE: 'ACTIVE',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
};

// Routes de navigation
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  COURSES: '/courses',
  COURSE_DETAILS: '/courses/:id',
  MY_COURSES: '/my-courses',
  PROFILE: '/profile',
};