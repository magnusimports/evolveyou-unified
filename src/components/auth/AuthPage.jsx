import React, { useState } from 'react';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';
import ForgotPasswordForm from './ForgotPasswordForm';

const AuthPage = () => {
  const [mode, setMode] = useState('login'); // 'login', 'signup', 'forgot-password'

  const handleToggleMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login');
  };

  const handleForgotPassword = () => {
    setMode('forgot-password');
  };

  const handleBackToLogin = () => {
    setMode('login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      {/* Main Content */}
      <div className="relative z-10 w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-bold">E</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            EvolveYou
          </h1>
          <p className="text-gray-600">
            Sua jornada para uma vida mais saudável
          </p>
        </div>

        {/* Auth Forms */}
        {mode === 'login' && (
          <LoginForm 
            onToggleMode={handleToggleMode}
            onForgotPassword={handleForgotPassword}
          />
        )}
        
        {mode === 'signup' && (
          <SignupForm 
            onToggleMode={handleToggleMode}
          />
        )}
        
        {mode === 'forgot-password' && (
          <ForgotPasswordForm 
            onBack={handleBackToLogin}
          />
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>
            © 2025 EvolveYou. Todos os direitos reservados.
          </p>
          <div className="flex justify-center space-x-4 mt-2">
            <button className="hover:text-gray-700 transition-colors">
              Termos de Uso
            </button>
            <button className="hover:text-gray-700 transition-colors">
              Privacidade
            </button>
            <button className="hover:text-gray-700 transition-colors">
              Suporte
            </button>
          </div>
        </div>
      </div>

      {/* Demo Info */}
      <div className="absolute bottom-4 right-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 max-w-xs">
        <div className="text-xs text-yellow-800">
          <p className="font-semibold mb-1">🚀 Demo Mode</p>
          <p>Login: teste@evolveyou.com</p>
          <p>Senha: 123456</p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;

