import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
import PlanEditor from './components/PlanEditor';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://roadworksai.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

// Create AuthContext for global auth state management
const AuthContext = React.createContext(null);

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

function AppContent() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  // Initialize user state from localStorage with better error handling
  // Using lazy initialization to prevent re-reading on every render
  const [user, setUser] = useState(() => {
    try {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      console.log('=== INITIAL AUTH STATE (Mount) ===');
      console.log('Token exists:', !!token);
      console.log('User data exists:', !!userData);
      
      if (token && userData) {
        const parsed = JSON.parse(userData);
        console.log('Loaded user from localStorage:', parsed.email);
        return parsed;
      }
    } catch (e) {
      console.error('Error loading auth state:', e);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return null;
  });
  
  // Track if we've already persisted to avoid double-writes in StrictMode
  const persistedRef = React.useRef(false);
  
  // Persist auth state changes to localStorage
  // Use ref to prevent double-persistence in React.StrictMode
  useEffect(() => {
    // Skip the first effect call in StrictMode (cleanup phase)
    if (!persistedRef.current) {
      persistedRef.current = true;
      return;
    }
    
    if (user) {
      console.log('User state updated, persisting to localStorage:', user.email);
      const currentUser = localStorage.getItem('user');
      const newUser = JSON.stringify(user);
      
      // Only update if changed to prevent unnecessary writes
      if (currentUser !== newUser) {
        localStorage.setItem('user', newUser);
      }
    } else {
      console.log('User state cleared');
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
  }, [user]);

  const login = (token, userData) => {
    console.log('=== LOGIN FUNCTION CALLED ===');
    console.log('Token received:', token?.substring(0, 20) + '...');
    console.log('User data:', userData);
    
    try {
      // Validate inputs
      if (!token || !userData) {
        throw new Error('Invalid token or user data');
      }
      
      // Save to localStorage immediately
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      console.log('✅ Auth data saved to localStorage');
      
      // Update state - this will trigger re-render and navigation
      setUser(userData);
      
      console.log('✅ User state updated');
      console.log('Navigating to dashboard...');
      
      // Use setTimeout to ensure state update completes before navigation
      // This helps with React.StrictMode double-mount behavior
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 50);
      
    } catch (e) {
      console.error('❌ Error in login function:', e);
      // Clean up on error
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      alert('Failed to save login session: ' + e.message);
    }
  };

  // Guest mode for demo/testing
  const loginAsGuest = () => {
    console.log('=== GUEST LOGIN ===');
    const guestUser = {
      id: 'guest-user-' + Date.now(),
      email: 'guest@demo.com',
      company_name: 'Demo User',
      role: 'guest'
    };
    const guestToken = 'guest-demo-token-' + Date.now();
    
    console.log('Guest user created:', guestUser);
    login(guestToken, guestUser);
  };

  const logout = () => {
    console.log('=== LOGOUT ===');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/auth', { replace: true });
  };

  const authValue = {
    user,
    loading,
    login,
    loginAsGuest,
    logout
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={authValue}>
      <div className="App">
        <Routes>
          <Route 
            path="/auth" 
            element={
              user ? <Navigate to="/dashboard" replace /> : <AuthPage onLogin={login} onGuestLogin={loginAsGuest} />
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
          {/* Demo/Testing Route - Direct Access without Auth */}
          <Route 
            path="/demo" 
            element={
              <PlanEditor 
                user={{ 
                  id: 'demo-user', 
                  email: 'demo@trafficease.com', 
                  company_name: 'Demo User',
                  role: 'demo'
                }} 
                onLogout={logout} 
              />
            } 
          />
          <Route 
            path="/" 
            element={<Navigate to={user ? "/dashboard" : "/auth"} replace />} 
          />
        </Routes>
        <Toaster />
      </div>
    </AuthContext.Provider>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;