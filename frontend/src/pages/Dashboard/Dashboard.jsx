// src/pages/Dashboard/Dashboard.jsx
import { useSelector } from 'react-redux';
import { selectUser } from '../../store/slices/authSlice';
import AdminDashboard from './AdminDashboard';
import StudentDashboard from './StudentDashboard';
import InstructorDashboard from './InstructorDashboard';

function Dashboard() {
  const user = useSelector(selectUser);

  // Rediriger selon le rôle
  const renderDashboard = () => {
    if (!user) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-lg text-gray-600">Chargement...</p>
        </div>
      );
    }

    // Switch basé sur le rôle
    switch (user.role) {
      case 'ADMIN':
      case 'SUPER_ADMIN':
        return <AdminDashboard />;
      
      case 'INSTRUCTOR':
        return <InstructorDashboard />;
      
      case 'STUDENT':
      default:
        return <StudentDashboard />;
    }
  };

  return renderDashboard();
}

export default Dashboard;