import { useSelector, useDispatch } from 'react-redux';
import { useMutation } from '@tanstack/react-query';
import { authService } from '../api/services';
import { 
  loginStart, 
  loginSuccess, 
  loginFailure, 
  logout as logoutAction 
} from '../store/slices/authSlice';
import { setAuthData, clearAuthData } from '../utils/auth';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);

  // Hook de connexion
  const loginMutation = useMutation({
    mutationFn: (credentials) => authService.login(credentials),
    onMutate: () => {
      dispatch(loginStart());
    },
    onSuccess: (data) => {
      dispatch(loginSuccess(data));
      setAuthData(data);
      toast.success('Connexion réussie !');
      navigate('/dashboard');
    },
    onError: (error) => {
      dispatch(loginFailure(error.message));
      toast.error('Échec de la connexion');
    },
  });

  // Hook de déconnexion
  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      dispatch(logoutAction());
      clearAuthData();
      toast.info('Déconnexion réussie');
      navigate('/login');
    },
  });

  return {
    ...auth,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
  };
};