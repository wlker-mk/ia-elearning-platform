// src/routes/AppRoutes.jsx
import { Routes, Route } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import ProtectedRoute from './ProtectedRoute';
import PublicRoute from './PublicRoute';

// Pages
import Home from '../pages/Home/Home';
import Login from '../pages/Auth/Login';
import Register from '../pages/Auth/Register';
import Courses from '../pages/Courses/Courses';
import Instructors from '../pages/Instructors/Instructors';
import About from '../pages/About/About';
import Community from '../pages/Community/Community';
import Dashboard from '../pages/Dashboard/Dashboard';
import NotFound from '../pages/Error/NotFound';

// Page de test (à supprimer en production)
import TestAuth from '../pages/Test/TestAuth';

function AppRoutes() {
  return (
    <Routes>
      {/* Routes publiques avec Header + Footer */}
      <Route path="/" element={<MainLayout><Home /></MainLayout>} />
      <Route path="/courses" element={<MainLayout><Courses /></MainLayout>} />
      <Route path="/instructors" element={<MainLayout><Instructors /></MainLayout>} />
      <Route path="/about" element={<MainLayout><About /></MainLayout>} />
      <Route path="/community" element={<MainLayout><Community /></MainLayout>} />

      {/* Routes d'authentification (SANS Header/Footer) */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Routes protégées avec Header + Footer */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* 🧪 ROUTE DE TEST - À supprimer en production */}
      <Route 
        path="/test-auth" 
        element={
          <MainLayout>
            <TestAuth />
          </MainLayout>
        } 
      />

      {/* Route 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default AppRoutes;