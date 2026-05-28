import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const mockServices = [
  {
    id: 1,
    name: "Кресло эконом класса",
    description: "Удобное кресло для пассажиров эконом-класса.",
    price: 920000,
    material: "ткань",
    manufacturer: "АвиаКомфорт",
    image_url: "/images/chair_econom.jpg"  // ← исправлено
  },
  {
    id: 2,
    name: "Персональный телевизор (PTV)",
    description: "Современный персональный телевизор для развлечений.",
    price: 62550,
    material: "пластик",
    manufacturer: "АвиаМедиа",
    image_url: "/images/PTV.jpg"  // ← исправлено
  },
  {
    id: 3,
    name: "Потолочный телевизор",
    description: "Высококачественный потолочный телевизор.",
    price: 52110,
    material: "пластик",
    manufacturer: "АвиаМедиа",
    image_url: "/images/PTV_2.jpg"  // ← исправлено
  },
  {
    id: 4,
    name: "Кресло бизнес класса",
    description: "Премиальное кресло для комфорта пассажиров.",
    price: 352180,
    material: "кожа",
    manufacturer: "АвиаЛюкс",
    image_url: "/images/chair_business_1.jpg"  // ← исправлено
  },
  {
    id: 5,
    name: "Кресло бизнес класса (люкс)",
    description: "Премиальное кресло для максимального комфорта.",
    price: 920000,
    material: "кожа премиум",
    manufacturer: "АвиаЛюкс",
    image_url: "/images/chair_business_2.jpg"  // ← исправлено
  }
];

const DEFAULT_IMAGE = 'https://via.placeholder.com/300x200?text=No+Image';

const ServicesList = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredServices, setFilteredServices] = useState(mockServices);
  const [cartMessage, setCartMessage] = useState('');
  const [cartItemsCount, setCartItemsCount] = useState(0);

  useEffect(() => {
    const savedCart = localStorage.getItem('airplane_cart');
    const cart = savedCart ? JSON.parse(savedCart) : [];
    const total = cart.reduce((sum, item) => sum + item.quantity, 0);
    setCartItemsCount(total);
  }, []);

  const handleSearch = () => {
    const filtered = mockServices.filter(service =>
      service.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredServices(filtered);
  };

  const handleReset = () => {
    setSearchTerm('');
    setFilteredServices(mockServices);
  };

  const addToCart = (service, e) => {
    e.stopPropagation();
    const savedCart = localStorage.getItem('airplane_cart');
    let cart = savedCart ? JSON.parse(savedCart) : [];
    const existingItem = cart.find(item => item.id === service.id);
    
    if (existingItem) {
      existingItem.quantity += 1;
    } else {
      cart.push({
        id: service.id,
        name: service.name,
        price: service.price,
        image_url: service.image_url,
        quantity: 1
      });
    }
    
    localStorage.setItem('airplane_cart', JSON.stringify(cart));
    const total = cart.reduce((sum, item) => sum + item.quantity, 0);
    setCartItemsCount(total);
  };

  return (
    <div className="container">
      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Поиск по названию..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="search-button" onClick={handleSearch}>
          🔍 Поиск
        </button>
        <Link to="/cart" className={`cart-icon-link ${cartItemsCount > 0 ? 'active' : ''}`}>
            <img src="/images/button.jpg" alt="Корзина" className="cart-icon" />
            {cartItemsCount > 0 && (
                <span className="cart-badge">{cartItemsCount}</span>
            )}
        </Link>
      </div>

      {cartMessage && (
        <div className="cart-message">
          {cartMessage}
        </div>
      )}

      <div className="products-grid">
        {filteredServices.map(service => (
          <div 
            key={service.id} 
            className="product-card" 
            onClick={() => navigate(`/service/${service.id}`)}
          >
            <img
              src={service.image_url || DEFAULT_IMAGE}
              alt={service.name}
              className="product-image"
            />
            <div className="product-info">
              <div className="product-title">{service.name}</div>
              <div className="product-price">{service.price.toLocaleString()} ₽</div>
              <button 
                className="cart-btn" 
                onClick={(e) => addToCart(service, e)}
              >
                Добавить в заявку
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredServices.length === 0 && (
        <div className="no-products">
          <p>Услуги не найдены</p>
        </div>
      )}
    </div>
  );
};

export default ServicesList;