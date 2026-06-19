import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TrendAnalysis from './pages/TrendAnalysis';
import BrandCompare from './pages/BrandCompare';
import FilmDetail from './pages/FilmDetail';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trends" element={<TrendAnalysis />} />
        <Route path="/compare" element={<BrandCompare />} />
        <Route path="/detail/:id" element={<FilmDetail />} />
      </Routes>
    </Router>
  );
}
