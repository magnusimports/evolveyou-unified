import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Onboarding from './pages/Onboarding';
import Workouts from './pages/Workouts';
import Diet from './pages/Diet';
import Progress from './pages/Progress';
import './App.css';

// Componente para proteger rotas que requerem autenticação
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Componente para redirecionar usuários autenticados
const PublicRoute = ({ children }) => {
  const { isAuthenticated, user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    // Se o usuário está autenticado mas não completou o onboarding
    if (!user?.onboarding_completed) {
      return <Navigate to="/onboarding" />;
    }
    // Se já completou o onboarding, vai para o dashboard
    return <Navigate to="/dashboard" />;
  }
  
  return children;
};

// Componente para verificar se precisa fazer onboarding
const OnboardingRoute = ({ children }) => {
  const { isAuthenticated, user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (user?.onboarding_completed) {
    return <Navigate to="/dashboard" />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Rotas públicas */}
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          } />
          
          {/* Rota de onboarding */}
          <Route path="/onboarding" element={
            <OnboardingRoute>
              <Onboarding />
            </OnboardingRoute>
          } />
          
          {/* Rotas protegidas */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/workouts" element={<Workouts />} />
            <Route path="/diet" element={<Diet />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Route>
          
          {/* Rota padrão */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
