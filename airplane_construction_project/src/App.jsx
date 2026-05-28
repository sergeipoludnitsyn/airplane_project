import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Breadcrumbs from './components/Breadcrumbs';
import ServicesList from './pages/ServicesList';
import ServiceDetail from './pages/ServiceDetail';
import Cart from './pages/Cart';
import './App.css';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={
          <>
            <div className="container">
              <Breadcrumbs />
            </div>
            <ServicesList />
          </>
        } />
        <Route path="/service/:id" element={
          <>
            <div className="container">
              <Breadcrumbs />
            </div>
            <ServiceDetail />
          </>
        } />
        <Route path="/cart" element={
          <>
            <div className="container">
              <Breadcrumbs />
            </div>
            <Cart />
          </>
        } />
      </Routes>
    </Router>
  );
}

export default App;