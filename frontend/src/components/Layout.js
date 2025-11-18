import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { logout, getCurrentUser, getCurrentTenant } from '../services/auth';
import './Layout.css';

function Layout({ children, onLogout }) {
  const location = useLocation();
  const user = getCurrentUser();
  const tenant = getCurrentTenant();

  const handleLogout = () => {
    logout();
    onLogout();
  };

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>POS System</h1>
          <span className="tenant-name">{tenant?.name}</span>
        </div>

        <div className="navbar-menu">
          <Link to="/" className={isActive('/')}>Dashboard</Link>
          <Link to="/pos" className={isActive('/pos')}>POS</Link>
          <Link to="/products" className={isActive('/products')}>Products</Link>
          <Link to="/sales" className={isActive('/sales')}>Sales</Link>
          <Link to="/customers" className={isActive('/customers')}>Customers</Link>
        </div>

        <div className="navbar-user">
          <span>{user?.username} ({user?.role})</span>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </nav>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;
