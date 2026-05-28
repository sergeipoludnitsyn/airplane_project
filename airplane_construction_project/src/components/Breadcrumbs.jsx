import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

const mockServices = [
  { id: 1, name: "Кресло эконом класса" },
  { id: 2, name: "Персональный телевизор (PTV)" },
  { id: 3, name: "Потолочный телевизор" },
  { id: 4, name: "Кресло бизнес класса" },
  { id: 5, name: "Кресло бизнес класса (люкс)" }
];

const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(x => x);
  
  const [serviceName, setServiceName] = useState('');

  useEffect(() => {
    // Если текущий путь содержит id услуги
    const serviceId = pathnames.find(name => !isNaN(parseInt(name)));
    if (serviceId) {
      const service = mockServices.find(s => s.id === parseInt(serviceId));
      setServiceName(service ? service.name : 'Услуга');
    } else {
      setServiceName('');
    }
  }, [location]);

  return (
    <div className="breadcrumbs">
      <Link to="/">Главная</Link>
      {pathnames.map((name, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;
        
        let displayName = name;
        if (name === 'service') {
          displayName = serviceName || 'Услуга';
        } else if (name === 'cart') {
          displayName = 'Корзина';
        } else if (!isNaN(parseInt(name))) {
          return null; // Не показываем id
        }
        
        return (
          <span key={routeTo}>
            {' / '}
            {isLast ? (
              <span className="active">{displayName}</span>
            ) : (
              <Link to={routeTo}>{displayName}</Link>
            )}
          </span>
        );
      })}
    </div>
  );
};

export default Breadcrumbs;