import React, { useState, useEffect, createContext, useContext } from 'react';

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

  useEffect(() => {
    // Simular verificação de usuário logado
    const savedUser = localStorage.getItem('evolveyou_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      setError('');
      setLoading(true);
      
      // Simular login para demonstração
      if (email === 'teste@evolveyou.com' && password === '123456') {
        const mockUser = {
          uid: 'demo-user-123',
          email: 'teste@evolveyou.com',
          displayName: 'Usuário Demo',
          name: 'Usuário Demo',
          profile: {
            onboardingCompleted: false,
            anamneseCompleted: false
          }
        };
        
        localStorage.setItem('evolveyou_user', JSON.stringify(mockUser));
        setUser(mockUser);
        return mockUser;
      } else {
        throw new Error('Credenciais inválidas');
      }
    } catch (error) {
      setError(error.message || 'Erro ao fazer login');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password, userData = {}) => {
    try {
      setError('');
      setLoading(true);
      
      // Simular cadastro
      const mockUser = {
        uid: 'new-user-' + Date.now(),
        email: email,
        displayName: userData.name || email.split('@')[0],
        name: userData.name || email.split('@')[0],
        profile: {
          onboardingCompleted: false,
          anamneseCompleted: false,
          ...userData
        }
      };
      
      localStorage.setItem('evolveyou_user', JSON.stringify(mockUser));
      setUser(mockUser);
      return mockUser;
    } catch (error) {
      setError(error.message || 'Erro ao criar conta');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    try {
      setError('');
      setLoading(true);
      
      // Simular login com Google
      const mockUser = {
        uid: 'google-user-123',
        email: 'usuario@gmail.com',
        displayName: 'Usuário Google',
        name: 'Usuário Google',
        profile: {
          onboardingCompleted: false,
          anamneseCompleted: false
        }
      };
      
      localStorage.setItem('evolveyou_user', JSON.stringify(mockUser));
      setUser(mockUser);
      return mockUser;
    } catch (error) {
      setError(error.message || 'Erro ao fazer login com Google');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setError('');
      localStorage.removeItem('evolveyou_user');
      setUser(null);
    } catch (error) {
      setError(error.message || 'Erro ao fazer logout');
      throw error;
    }
  };

  const resetPassword = async (email) => {
    try {
      setError('');
      // Simular envio de email
      console.log('Email de recuperação enviado para:', email);
    } catch (error) {
      setError(error.message || 'Erro ao enviar email');
      throw error;
    }
  };

  const updateUserProfile = async (updates) => {
    try {
      if (!user) throw new Error('Usuário não autenticado');
      
      const updatedUser = { ...user, ...updates };
      localStorage.setItem('evolveyou_user', JSON.stringify(updatedUser));
      setUser(updatedUser);
    } catch (error) {
      setError(error.message || 'Erro ao atualizar perfil');
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

