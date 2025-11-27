// src/store/store.js
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';
import coursesReducer from './slices/coursesSlice';
import cartReducer from './slices/cartSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    courses: coursesReducer,
    cart: cartReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignorer ces actions pour les données non-sérialisables
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: import.meta.env.DEV, // DevTools uniquement en développement
});

export default store;