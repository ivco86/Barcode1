import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Customers.css';

function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingCustomer) {
        await api.put(`/customers/${editingCustomer.id}`, formData);
      } else {
        await api.post('/customers', formData);
      }

      setShowModal(false);
      setEditingCustomer(null);
      setFormData({ name: '', email: '', phone: '' });
      loadCustomers();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save customer');
    }
  };

  const handleEdit = (customer) => {
    setEditingCustomer(customer);
    setFormData({
      name: customer.name,
      email: customer.email || '',
      phone: customer.phone || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this customer?')) return;

    try {
      await api.delete(`/customers/${id}`);
      loadCustomers();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete customer');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="customers">
      <div className="page-header">
        <h1>Customers</h1>
        <button onClick={() => { setShowModal(true); setEditingCustomer(null); }} className="btn-primary">
          + Add Customer
        </button>
      </div>

      <table className="customers-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Loyalty Points</th>
            <th>Total Spent</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {customers.map(customer => (
            <tr key={customer.id}>
              <td>{customer.name}</td>
              <td>{customer.phone || '-'}</td>
              <td>{customer.email || '-'}</td>
              <td>{customer.loyalty_points}</td>
              <td>{parseFloat(customer.total_spent).toFixed(2)} лв</td>
              <td>
                <button onClick={() => handleEdit(customer)} className="btn-edit">Edit</button>
                <button onClick={() => handleDelete(customer.id)} className="btn-delete">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editingCustomer ? 'Edit Customer' : 'Add Customer'}</h2>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingCustomer ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Customers;
