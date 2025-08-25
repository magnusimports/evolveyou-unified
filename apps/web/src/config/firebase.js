// Firebase Configuration for EvolveYou Dashboard
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import { getAnalytics } from 'firebase/analytics';
import { getFunctions } from 'firebase/functions';

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
export const functions = getFunctions(app);

// Initialize Analytics only in production
export const analytics = import.meta.env.VITE_ENABLE_ANALYTICS === 'true' 
  ? getAnalytics(app) 
  : null;

// Export the app instance
export default app;

// Helper functions for common operations
export const isProduction = import.meta.env.VITE_APP_ENVIRONMENT === 'production';
export const isDevelopment = import.meta.env.VITE_APP_ENVIRONMENT === 'development';
export const debugMode = import.meta.env.VITE_DEBUG_MODE === 'true';

// API endpoints
export const API_ENDPOINTS = {
  base: import.meta.env.VITE_API_BASE_URL,
  functions: import.meta.env.VITE_FUNCTIONS_BASE_URL,
  auth: `${import.meta.env.VITE_API_BASE_URL}/auth`,
  users: `${import.meta.env.VITE_API_BASE_URL}/users`,
  workouts: `${import.meta.env.VITE_API_BASE_URL}/workouts`,
  nutrition: `${import.meta.env.VITE_API_BASE_URL}/nutrition`,
  analytics: `${import.meta.env.VITE_API_BASE_URL}/analytics`
};

