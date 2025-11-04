// Vite uses import.meta.env instead of process.env
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
};

export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme',
};

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  CHAT: '/chat',
  HOME: '/',
};

export const MESSAGES = {
  WELCOME: 'Hi {username}, how can I help you today?',
  ERROR: 'Something went wrong. Please try again.',
  NO_DOCUMENTS: 'Please upload documents to start chatting.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
};

export const SUGGESTED_PROMPTS = [
  {
    icon: '📄',
    title: 'Summarize',
    description: 'Get a quick summary of the documents',
    prompt: 'Can you provide a summary of the key points in the documents?',
  },
  {
    icon: '🔍',
    title: 'Search',
    description: 'Find specific information',
    prompt: 'What are the main topics covered in the documents?',
  },
  {
    icon: '💡',
    title: 'Explain',
    description: 'Get detailed explanations',
    prompt: 'Can you explain the key concepts mentioned?',
  },
  {
    icon: '📊',
    title: 'Analyze',
    description: 'Deep dive into the content',
    prompt: 'What insights can you provide from the documents?',
  },
];

export const APP_CONFIG = {
  NAME: import.meta.env.VITE_APP_NAME || 'DocuChat AI',
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
};