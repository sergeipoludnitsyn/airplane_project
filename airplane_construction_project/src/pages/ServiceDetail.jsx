import { useParams, useNavigate } from 'react-router-dom';

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

const DEFAULT_IMAGE = 'https://via.placeholder.com/600x400?text=No+Image';

const ServiceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const service = mockServices.find(s => s.id === Number(id));

  if (!service) {
    return (
      <div className="container">
        <div className="product-container">
          <h2>Услуга не найдена</h2>
          <button className="back-button" onClick={() => navigate('/')}>Назад к списку</button>
        </div>
      </div>
    );
  }

  return (
    <div className="product-page">
      <div className="product-container">
        <h1 className="product-title">{service.name}</h1>
        
        <div className="video-wrapper">
          <img src={service.image_url || DEFAULT_IMAGE} alt={service.name} />
        </div>
        
        <div className="specs-list">
          <div className="spec-item">
            <span className="spec-label">Описание:</span>
            <span className="spec-value">{service.description}</span>
          </div>
          <div className="spec-item">
            <span className="spec-label">Производитель:</span>
            <span className="spec-value">{service.manufacturer}</span>
          </div>
          <div className="spec-item">
            <span className="spec-label">Материал:</span>
            <span className="spec-value">{service.material}</span>
          </div>
          {service.width && service.width !== "-" && (
            <div className="spec-item">
              <span className="spec-label">Ширина:</span>
              <span className="spec-value">{service.width} мм</span>
            </div>
          )}
          {service.height && service.height !== "-" && (
            <div className="spec-item">
              <span className="spec-label">Высота:</span>
              <span className="spec-value">{service.height} мм</span>
            </div>
          )}
          {service.depth && service.depth !== "-" && (
            <div className="spec-item">
              <span className="spec-label">Глубина:</span>
              <span className="spec-value">{service.depth} мм</span>
            </div>
          )}
        </div>
        
        <div className="price">{service.price.toLocaleString()} ₽</div>
        
        <div className="action-buttons">
        </div>
      </div>
    </div>
  );
};

export default ServiceDetail;