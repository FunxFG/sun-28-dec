import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
import PlanEditor from './components/PlanEditor';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://trafficease-3.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    console.log('App.js useEffect - Checking auth state');
    console.log('Token from localStorage:', token ? 'EXISTS' : 'MISSING');
    console.log('User data from localStorage:', userData ? 'EXISTS' : 'MISSING');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        console.log('Setting user state:', parsedUser);
        setUser(parsedUser);
      } catch (e) {
        console.error('Error parsing user data:', e);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = (token, userData) => {
    console.log('App.js login() called');
    console.log('Token:', token);
    console.log('User data:', userData);
    
    try {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      console.log('Auth data saved to localStorage');
      console.log('User state updated:', userData);
    } catch (e) {
      console.error('Error saving auth data:', e);
    }
  };

  const logout = () => {
    console.log('App.js logout() called');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  console.log('App.js rendering with user:', user ? 'LOGGED IN' : 'NOT LOGGED IN');

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/auth" 
            element={
              user ? <Navigate to="/dashboard" replace /> : <AuthPage onLogin={login} />
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              user ? <Dashboard user={user} onLogout={logout} /> : <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/plan/:planId?" 
            element={
              user ? <PlanEditor user={user} onLogout={logout} /> : <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/" 
            element={<Navigate to={user ? "/dashboard" : "/auth"} replace />} 
          />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;