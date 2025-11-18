import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Today's Sales</h3>
          <p className="stat-value">{stats?.total_sales_today?.toFixed(2)} лв</p>
          <p className="stat-label">{stats?.total_sales_count_today} transactions</p>
        </div>

        <div className="stat-card">
          <h3>Products</h3>
          <p className="stat-value">{stats?.total_products}</p>
          <p className="stat-label">Total products</p>
        </div>

        <div className="stat-card warning">
          <h3>Low Stock</h3>
          <p className="stat-value">{stats?.low_stock_products}</p>
          <p className="stat-label">Products need restock</p>
        </div>

        <div className="stat-card">
          <h3>Customers</h3>
          <p className="stat-value">{stats?.total_customers}</p>
          <p className="stat-label">Registered customers</p>
        </div>
      </div>

      <div className="revenue-chart">
        <h2>Revenue Last 7 Days</h2>
        <div className="chart">
          {stats?.revenue_last_7_days?.map((day, index) => {
            const maxRevenue = Math.max(...stats.revenue_last_7_days.map(d => d.revenue));
            const height = maxRevenue > 0 ? (day.revenue / maxRevenue * 200) : 0;

            return (
              <div key={index} className="chart-bar">
                <div className="bar" style={{ height: `${height}px` }}>
                  <span className="bar-value">{day.revenue.toFixed(0)}</span>
                </div>
                <span className="bar-label">{new Date(day.date).toLocaleDateString('bg-BG', { weekday: 'short' })}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
