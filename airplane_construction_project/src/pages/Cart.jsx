import { useState, useEffect } from 'react';

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);

  // Функция загрузки корзины
  const loadCart = () => {
    const savedCart = localStorage.getItem('airplane_cart');
    if (savedCart) {
      setCartItems(JSON.parse(savedCart));
    } else {
      setCartItems([]);
    }
  };

  // Загрузка при монтировании компонента
  useEffect(() => {
    loadCart();
  }, []);

  // Слушаем изменения localStorage (если корзина обновляется на другой вкладке)
  useEffect(() => {
    const handleStorageChange = () => {
      loadCart();
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const updateQuantity = (id, newQuantity) => {
    if (newQuantity < 1) return;
    const updatedCart = cartItems.map(item =>
      item.id === id ? { ...item, quantity: newQuantity } : item
    );
    setCartItems(updatedCart);
    localStorage.setItem('airplane_cart', JSON.stringify(updatedCart));
  };

  const removeItem = (id) => {
    const updatedCart = cartItems.filter(item => item.id !== id);
    setCartItems(updatedCart);
    localStorage.setItem('airplane_cart', JSON.stringify(updatedCart));
  };

  const clearCart = () => {
    setCartItems([]);
    localStorage.setItem('airplane_cart', JSON.stringify([]));
  };

  const totalSum = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);

  if (cartItems.length === 0) {
    return (
      <div className="container">
        <div className="cart-empty">
          🛒 Корзина пуста
          <p style={{ marginTop: '10px', fontSize: '14px' }}>
            Добавьте товары из каталога
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="cart-container">
        <h2 style={{ color: '#6A747C', marginBottom: '20px' }}>Корзина</h2>
        
        <div className="cart-items">
          {cartItems.map(item => (
            <div key={item.id} className="cart-item">
              <img
                src={item.image_url || 'https://via.placeholder.com/60x60?text=No+Image'}
                alt={item.name}
                className="cart-item-image"
              />
              <div className="cart-item-info">
                <div className="cart-item-title">{item.name}</div>
                <div className="cart-item-price">{item.price.toLocaleString()} ₽</div>
              </div>
              <input
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => updateQuantity(item.id, parseInt(e.target.value))}
                className="cart-item-quantity"
              />
              <div className="cart-item-total">
                {(item.price * item.quantity).toLocaleString()} ₽
              </div>
              <button
                className="cart-item-remove"
                onClick={() => removeItem(item.id)}
                title="Удалить"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        <div className="cart-total">
          <span>Итого: </span>
          <span className="total-amount">{totalSum.toLocaleString()} ₽</span>
        </div>

        <button className="clear-cart-btn" onClick={clearCart}>
          Очистить корзину
        </button>
      </div>
    </div>
  );
};

export default Cart;