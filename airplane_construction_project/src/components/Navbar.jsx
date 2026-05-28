import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <header>
      <Link to="/" className="logo-link">
        <img src="/images/logo.jpg" alt="Логотип" className="logo" />
      </Link>
      <h1>Комплектация самолета</h1>
    </header>
  );
};

export default Navbar;