import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useFirebaseAuth.jsx';
import AuthPage from './components/auth/AuthPage';
import OnboardingOriginal from './pages/OnboardingOriginal';
import DashboardPage from './pages/DashboardPage';
import LoadingSpinner from './components/ui/LoadingSpinner';
import './App.css';

// Componente para proteger rotas que precisam de autenticação
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/auth" replace />;
  }
  
  return children;
};

// Componente para redirecionar usuários logados
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }
  
  if (user) {
    // Se o usuário não completou o onboarding, redireciona para lá
    if (!user.profile?.onboardingCompleted) {
      return <Navigate to="/onboarding" replace />;
    }
    // Senão, vai para o dashboard
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

// Componente principal das rotas
const AppRoutes = () => {
  return (
    <Routes>
      {/* Rota pública - Login/Cadastro */}
      <Route 
        path="/auth" 
        element={
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        } 
      />
      
      {/* Rota protegida - Onboarding */}
      <Route 
        path="/onboarding" 
        element={
          <ProtectedRoute>
            <OnboardingOriginal />
          </ProtectedRoute>
        } 
      />
      
      {/* Rota protegida - Dashboard */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      
      {/* Rota raiz - redireciona baseado no estado do usuário */}
      <Route 
        path="/" 
        element={<Navigate to="/auth" replace />} 
      />
      
      {/* Rota 404 - redireciona para auth */}
      <Route 
        path="*" 
        element={<Navigate to="/auth" replace />} 
      />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-background">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

