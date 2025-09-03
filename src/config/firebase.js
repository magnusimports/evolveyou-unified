import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// Configuração do Firebase - evolveyou-prod
const firebaseConfig = {
  apiKey: "AIzaSyBYtWJKn8fGkGkGkGkGkGkGkGkGkGkGkGk",
  authDomain: "evolveyou-prod.firebaseapp.com",
  projectId: "evolveyou-prod",
  storageBucket: "evolveyou-prod.firebasestorage.app",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456789012345678"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Inicializar serviços
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app;

