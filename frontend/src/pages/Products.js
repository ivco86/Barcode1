import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Products.css';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    barcode: '',
    name: '',
    price: '',
    cost: '',
    stock: '',
    category: '',
    min_stock: '5'
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingProduct) {
        await api.put(`/products/${editingProduct.id}`, formData);
      } else {
        await api.post('/products', formData);
      }

      setShowModal(false);
      setEditingProduct(null);
      setFormData({ barcode: '', name: '', price: '', cost: '', stock: '', category: '', min_stock: '5' });
      loadProducts();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      barcode: product.barcode,
      name: product.name,
      price: product.price,
      cost: product.cost || '',
      stock: product.stock,
      category: product.category || '',
      min_stock: product.min_stock
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      await api.delete(`/products/${id}`);
      loadProducts();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete product');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="products">
      <div className="page-header">
        <h1>Products</h1>
        <button onClick={() => { setShowModal(true); setEditingProduct(null); }} className="btn-primary">
          + Add Product
        </button>
      </div>

      <table className="products-table">
        <thead>
          <tr>
            <th>Barcode</th>
            <th>Name</th>
            <th>Category</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id} className={product.stock <= product.min_stock ? 'low-stock' : ''}>
              <td>{product.barcode}</td>
              <td>{product.name}</td>
              <td>{product.category || '-'}</td>
              <td>{parseFloat(product.price).toFixed(2)} лв</td>
              <td>
                {product.stock}
                {product.stock <= product.min_stock && <span className="stock-warning">⚠️</span>}
              </td>
              <td>
                <button onClick={() => handleEdit(product)} className="btn-edit">Edit</button>
                <button onClick={() => handleDelete(product.id)} className="btn-delete">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editingProduct ? 'Edit Product' : 'Add Product'}</h2>

            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>Barcode *</label>
                  <input
                    type="text"
                    value={formData.barcode}
                    onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Price *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Cost</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.cost}
                    onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Stock *</label>
                  <input
                    type="number"
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Min Stock</label>
                  <input
                    type="number"
                    value={formData.min_stock}
                    onChange={(e) => setFormData({ ...formData, min_stock: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-cancel">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingProduct ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Products;
