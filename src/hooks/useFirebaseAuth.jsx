import React, { useState, useEffect, createContext, useContext } from 'react';
import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  sendPasswordResetEmail,
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { 
  doc, 
  setDoc, 
  getDoc, 
  updateDoc,
  serverTimestamp 
} from 'firebase/firestore';
import { auth, db } from '../config/firebase';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Monitorar estado de autenticação
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Buscar dados do perfil no Firestore
          const userDocRef = doc(db, 'users', firebaseUser.uid);
          const userDoc = await getDoc(userDocRef);
          
          let userData = {
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            displayName: firebaseUser.displayName,
            photoURL: firebaseUser.photoURL,
            emailVerified: firebaseUser.emailVerified
          };

          if (userDoc.exists()) {
            userData.profile = userDoc.data();
          } else {
            // Criar perfil inicial se não existir
            const initialProfile = {
              createdAt: serverTimestamp(),
              onboardingCompleted: false,
              anamneseCompleted: false
            };
            await setDoc(userDocRef, initialProfile);
            userData.profile = initialProfile;
          }

          setUser(userData);
        } catch (error) {
          console.error('Erro ao carregar perfil do usuário:', error);
          setError('Erro ao carregar dados do usuário');
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email, password) => {
    try {
      setError('');
      setLoading(true);
      
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result.user;
    } catch (error) {
      let errorMessage = 'Erro ao fazer login';
      
      switch (error.code) {
        case 'auth/user-not-found':
          errorMessage = 'Usuário não encontrado';
          break;
        case 'auth/wrong-password':
          errorMessage = 'Senha incorreta';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Email inválido';
          break;
        case 'auth/too-many-requests':
          errorMessage = 'Muitas tentativas. Tente novamente mais tarde';
          break;
        default:
          errorMessage = error.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password, userData = {}) => {
    try {
      setError('');
      setLoading(true);
      
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Atualizar perfil do Firebase Auth
      if (userData.name) {
        await updateProfile(result.user, {
          displayName: userData.name
        });
      }

      // Criar documento do usuário no Firestore
      const userDocRef = doc(db, 'users', result.user.uid);
      await setDoc(userDocRef, {
        email: result.user.email,
        displayName: userData.name || result.user.email.split('@')[0],
        createdAt: serverTimestamp(),
        onboardingCompleted: false,
        anamneseCompleted: false,
        ...userData
      });

      return result.user;
    } catch (error) {
      let errorMessage = 'Erro ao criar conta';
      
      switch (error.code) {
        case 'auth/email-already-in-use':
          errorMessage = 'Este email já está em uso';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Email inválido';
          break;
        case 'auth/weak-password':
          errorMessage = 'Senha muito fraca. Use pelo menos 6 caracteres';
          break;
        default:
          errorMessage = error.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    try {
      setError('');
      setLoading(true);
      
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      
      // Verificar se é primeira vez do usuário
      const userDocRef = doc(db, 'users', result.user.uid);
      const userDoc = await getDoc(userDocRef);
      
      if (!userDoc.exists()) {
        // Criar perfil para novo usuário Google
        await setDoc(userDocRef, {
          email: result.user.email,
          displayName: result.user.displayName,
          photoURL: result.user.photoURL,
          createdAt: serverTimestamp(),
          onboardingCompleted: false,
          anamneseCompleted: false,
          provider: 'google'
        });
      }

      return result.user;
    } catch (error) {
      let errorMessage = 'Erro ao fazer login com Google';
      
      switch (error.code) {
        case 'auth/popup-closed-by-user':
          errorMessage = 'Login cancelado pelo usuário';
          break;
        case 'auth/popup-blocked':
          errorMessage = 'Popup bloqueado. Permita popups para este site';
          break;
        default:
          errorMessage = error.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setError('');
      await signOut(auth);
    } catch (error) {
      setError('Erro ao fazer logout');
      throw error;
    }
  };

  const resetPassword = async (email) => {
    try {
      setError('');
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      let errorMessage = 'Erro ao enviar email de recuperação';
      
      switch (error.code) {
        case 'auth/user-not-found':
          errorMessage = 'Usuário não encontrado';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Email inválido';
          break;
        default:
          errorMessage = error.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const updateUserProfile = async (updates) => {
    try {
      if (!user) throw new Error('Usuário não autenticado');
      
      const userDocRef = doc(db, 'users', user.uid);
      await updateDoc(userDocRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });

      // Atualizar estado local
      setUser(prevUser => ({
        ...prevUser,
        profile: {
          ...prevUser.profile,
          ...updates
        }
      }));
    } catch (error) {
      setError('Erro ao atualizar perfil');
      throw error;
    }
  };

  const clearError = () => setError('');

  const value = {
    user,
    loading,
    error,
    login,
    signup,
    loginWithGoogle,
    logout,
    resetPassword,
    updateUserProfile,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

