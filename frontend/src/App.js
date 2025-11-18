import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import POS from './pages/POS';
import Products from './pages/Products';
import Sales from './pages/Sales';
import Customers from './pages/Customers';
import Layout from './components/Layout';
import { isAuthenticated } from './services/auth';

function App() {
  const [auth, setAuth] = useState(isAuthenticated());

  useEffect(() => {
    const checkAuth = () => {
      setAuth(isAuthenticated());
    };

    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, []);

  const ProtectedRoute = ({ children }) => {
    return auth ? children : <Navigate to="/login" />;
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={() => setAuth(true)} />} />

        <Route path="/" element={
          <ProtectedRoute>
            <Layout onLogout={() => setAuth(false)}>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        } />

        <Route path="/pos" element={
          <ProtectedRoute>
            <Layout onLogout={() => setAuth(false)}>
              <POS />
            </Layout>
          </ProtectedRoute>
        } />

        <Route path="/products" element={
          <ProtectedRoute>
            <Layout onLogout={() => setAuth(false)}>
              <Products />
            </Layout>
          </ProtectedRoute>
        } />

        <Route path="/sales" element={
          <ProtectedRoute>
            <Layout onLogout={() => setAuth(false)}>
              <Sales />
            </Layout>
          </ProtectedRoute>
        } />

        <Route path="/customers" element={
          <ProtectedRoute>
            <Layout onLogout={() => setAuth(false)}>
              <Customers />
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
