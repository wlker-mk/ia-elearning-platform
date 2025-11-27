// src/store/slices/cartSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  items: JSON.parse(localStorage.getItem('cart')) || [],
  total: 0,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    // Ajouter au panier
    addToCart: (state, action) => {
      const existingItem = state.items.find(item => item.id === action.payload.id);
      
      if (!existingItem) {
        state.items.push(action.payload);
        localStorage.setItem('cart', JSON.stringify(state.items));
      }
      
      // Calculer le total
      state.total = state.items.reduce((sum, item) => sum + item.price, 0);
    },

    // Retirer du panier
    removeFromCart: (state, action) => {
      state.items = state.items.filter(item => item.id !== action.payload);
      localStorage.setItem('cart', JSON.stringify(state.items));
      
      // Calculer le total
      state.total = state.items.reduce((sum, item) => sum + item.price, 0);
    },

    // Vider le panier
    clearCart: (state) => {
      state.items = [];
      state.total = 0;
      localStorage.removeItem('cart');
    },
  },
});

export const { addToCart, removeFromCart, clearCart } = cartSlice.actions;

export default cartSlice.reducer;

// Sélecteurs
export const selectCartItems = (state) => state.cart.items;
export const selectCartTotal = (state) => state.cart.total;
export const selectCartCount = (state) => state.cart.items.length;