// src/config/app.config.js
export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'AI E-Learning',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  features: {
    chatbot: import.meta.env.VITE_ENABLE_CHATBOT === 'true',
    gamification: import.meta.env.VITE_ENABLE_GAMIFICATION === 'true',
  },
  
  pagination: {
    defaultPageSize: 12,
    pageSizeOptions: [12, 24, 48],
  },
};