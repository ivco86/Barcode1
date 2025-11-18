import React, { useState } from 'react';
import api from '../services/api';
import './POS.css';

function POS() {
  const [barcode, setBarcode] = useState('');
  const [cart, setCart] = useState([]);
  const [discount, setDiscount] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleBarcodeSubmit = async (e) => {
    e.preventDefault();
    if (!barcode.trim()) return;

    try {
      const response = await api.get(`/products/barcode/${barcode}`);
      const product = response.data;

      // Check if product already in cart
      const existingIndex = cart.findIndex(item => item.id === product.id);

      if (existingIndex >= 0) {
        // Increase quantity
        const newCart = [...cart];
        newCart[existingIndex].quantity += 1;
        setCart(newCart);
      } else {
        // Add new item
        setCart([...cart, { ...product, quantity: 1 }]);
      }

      setBarcode('');
      setError('');
    } catch (err) {
      setError('Product not found');
    }
  };

  const updateQuantity = (index, quantity) => {
    if (quantity < 1) return;

    const newCart = [...cart];
    newCart[index].quantity = quantity;
    setCart(newCart);
  };

  const removeItem = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const calculateTotal = () => {
    const subtotal = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    return subtotal - discount;
  };

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError('Cart is empty');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const items = cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        unit_price: parseFloat(item.price),
        discount: 0
      }));

      await api.post('/sales', {
        items,
        discount: parseFloat(discount),
        tax: 0,
        payment_method: paymentMethod
      });

      setSuccess('Sale completed successfully!');
      setCart([]);
      setDiscount(0);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete sale');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pos">
      <h1>Point of Sale</h1>

      <div className="pos-container">
        <div className="pos-left">
          <form onSubmit={handleBarcodeSubmit} className="barcode-form">
            <input
              type="text"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              placeholder="Scan or enter barcode"
              className="barcode-input"
              autoFocus
            />
            <button type="submit" className="btn-add">Add</button>
          </form>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="cart">
            {cart.length === 0 ? (
              <p className="empty-cart">Cart is empty. Scan products to add.</p>
            ) : (
              <table className="cart-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th>Qty</th>
                    <th>Total</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {cart.map((item, index) => (
                    <tr key={index}>
                      <td>{item.name}</td>
                      <td>{parseFloat(item.price).toFixed(2)} лв</td>
                      <td>
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => updateQuantity(index, parseInt(e.target.value))}
                          min="1"
                          max={item.stock}
                          className="qty-input"
                        />
                      </td>
                      <td>{(parseFloat(item.price) * item.quantity).toFixed(2)} лв</td>
                      <td>
                        <button onClick={() => removeItem(index)} className="btn-remove">×</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="pos-right">
          <div className="checkout-panel">
            <h2>Checkout</h2>

            <div className="form-group">
              <label>Discount (лв)</label>
              <input
                type="number"
                value={discount}
                onChange={(e) => setDiscount(parseFloat(e.target.value) || 0)}
                min="0"
                step="0.01"
              />
            </div>

            <div className="form-group">
              <label>Payment Method</label>
              <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                <option value="cash">Cash</option>
                <option value="card">Card</option>
                <option value="mobile">Mobile Payment</option>
              </select>
            </div>

            <div className="total-section">
              <div className="total-row">
                <span>Subtotal:</span>
                <span>{cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0).toFixed(2)} лв</span>
              </div>
              <div className="total-row">
                <span>Discount:</span>
                <span>-{discount.toFixed(2)} лв</span>
              </div>
              <div className="total-row final">
                <span>TOTAL:</span>
                <span>{calculateTotal().toFixed(2)} лв</span>
              </div>
            </div>

            <button
              onClick={handleCheckout}
              disabled={loading || cart.length === 0}
              className="btn-checkout"
            >
              {loading ? 'Processing...' : 'Complete Sale'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default POS;
