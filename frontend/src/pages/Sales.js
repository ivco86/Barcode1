import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Sales.css';

function Sales() {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSale, setSelectedSale] = useState(null);

  useEffect(() => {
    loadSales();
  }, []);

  const loadSales = async () => {
    try {
      const response = await api.get('/sales');
      setSales(response.data);
    } catch (error) {
      console.error('Failed to load sales:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewDetails = async (saleId) => {
    try {
      const response = await api.get(`/sales/${saleId}`);
      setSelectedSale(response.data);
    } catch (error) {
      console.error('Failed to load sale details:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="sales">
      <h1>Sales History</h1>

      <table className="sales-table">
        <thead>
          <tr>
            <th>Sale #</th>
            <th>Date</th>
            <th>Total</th>
            <th>Payment</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sales.map(sale => (
            <tr key={sale.id}>
              <td>{sale.sale_number}</td>
              <td>{new Date(sale.created_at).toLocaleString('bg-BG')}</td>
              <td>{parseFloat(sale.total).toFixed(2)} лв</td>
              <td>{sale.payment_method}</td>
              <td>
                <span className={`status-badge ${sale.payment_status}`}>
                  {sale.payment_status}
                </span>
              </td>
              <td>
                <button onClick={() => viewDetails(sale.id)} className="btn-view">
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedSale && (
        <div className="modal" onClick={() => setSelectedSale(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="sale-detail-header">
              <h2>Sale {selectedSale.sale_number}</h2>
              <button onClick={() => setSelectedSale(null)} className="btn-close">×</button>
            </div>

            <div className="sale-detail-info">
              <div>
                <strong>Date:</strong> {new Date(selectedSale.created_at).toLocaleString('bg-BG')}
              </div>
              <div>
                <strong>Payment:</strong> {selectedSale.payment_method}
              </div>
              <div>
                <strong>Status:</strong> {selectedSale.payment_status}
              </div>
            </div>

            <table className="items-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {selectedSale.items?.map(item => (
                  <tr key={item.id}>
                    <td>Product ID: {item.product_id}</td>
                    <td>{item.quantity}</td>
                    <td>{parseFloat(item.unit_price).toFixed(2)} лв</td>
                    <td>{parseFloat(item.total).toFixed(2)} лв</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="sale-detail-totals">
              <div className="total-row">
                <span>Subtotal:</span>
                <span>{parseFloat(selectedSale.subtotal).toFixed(2)} лв</span>
              </div>
              <div className="total-row">
                <span>Discount:</span>
                <span>-{parseFloat(selectedSale.discount).toFixed(2)} лв</span>
              </div>
              <div className="total-row">
                <span>Tax:</span>
                <span>{parseFloat(selectedSale.tax).toFixed(2)} лв</span>
              </div>
              <div className="total-row final">
                <span>TOTAL:</span>
                <span>{parseFloat(selectedSale.total).toFixed(2)} лв</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sales;
