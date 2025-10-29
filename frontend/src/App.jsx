import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import Chat from './components/Chat';

function getToken() {
  return localStorage.getItem('token');
}

export default function App() {
  const token = getToken();
  return (
    <Routes>
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/chat"
        element={token ? <Chat /> : <Navigate to="/login" replace />}
      />
      <Route path="*" element={<Navigate to={token ? '/chat' : '/login'} replace />} />
    </Routes>
  );
}
