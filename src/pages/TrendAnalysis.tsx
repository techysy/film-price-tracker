import React, { useEffect, useState } from 'react';
import Layout from '../components/layout/Layout';
import FilterBar from '../components/trends/FilterBar';
import PriceChart from '../components/trends/PriceChart';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import { Link } from 'react-router-dom';
import type { Film, Brand } from '../data/mockData';

const TrendAnalysis: React.FC = () => {
  const [films, setFilms] = useState<Film[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedFilm, setSelectedFilm] = useState<Film | null>(null);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetch('/api/films').then((res) => res.json()), fetch('/api/brands').then((res) => res.json())])
      .then(([filmsRes, brandsRes]) => {
        if (filmsRes.success) setFilms(filmsRes.data);
        if (brandsRes.success) setBrands(brandsRes.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredFilms = films.filter((film) => {
    if (selectedBrand && film.brand !== selectedBrand) return false;
    if (selectedFormat && film.format !== selectedFormat) return false;
    return true;
  });

  const formats = [...new Set(films.map((f) => f.format))];

  if (loading) {
    return (
      <Layout title="价格趋势" subtitle="分析胶片价格走势">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-film-yellow">加载中...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="价格趋势" subtitle="分析胶片价格走势">
      <div className="space-y-6">
        <FilterBar
          brands={brands.map((b) => b.name)}
          formats={formats}
          selectedBrand={selectedBrand}
          selectedFormat={selectedFormat}
          onBrandChange={setSelectedBrand}
          onFormatChange={setSelectedFormat}
        />

        {selectedFilm ? (
          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="yellow">{selectedFilm.brand}</Badge>
                  <Badge>{selectedFilm.format}</Badge>
                </div>
                <div className="flex items-center gap-4 mt-2">
                  <div className="text-sm text-film-cream/50 font-body">
                    最低价: <span className="text-film-green">¥{selectedFilm.lowestPrice}</span>
                  </div>
                  <div className="text-sm text-film-cream/50 font-body">
                    最高价: <span className="text-film-red">¥{selectedFilm.highestPrice}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedFilm(null)}
                className="px-4 py-2 rounded-lg bg-film-yellow/10 text-film-yellow hover:bg-film-yellow/20 transition-colors font-body text-sm"
              >
                返回列表
              </button>
            </div>
            <PriceChart film={selectedFilm} />
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredFilms.map((film) => (
              <Card key={film.id} hover className="p-4 cursor-pointer" onClick={() => setSelectedFilm(film)}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <Badge variant="yellow" className="mb-1">
                      {film.brand}
                    </Badge>
                    <h3 className="font-body text-film-cream font-medium">{film.name}</h3>
                  </div>
                  <Badge>{film.format}</Badge>
                </div>

                <div className="flex items-end justify-between">
                  <div>
                    <div className="text-sm text-film-cream/50 font-body">{film.type}</div>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-2xl font-display font-bold text-film-yellow">
                        ¥{film.currentPrice}
                      </span>
                      <span className="text-sm text-film-cream/40 font-body">/卷</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-film-cream/40 font-body">
                      {film.priceHistory[film.priceHistory.length - 1].platform}
                    </div>
                    <div
                      className={`text-xs font-body mt-1 ${
                        film.currentPrice <= film.lowestPrice * 1.1
                          ? 'text-film-green'
                          : film.currentPrice >= film.highestPrice * 0.9
                            ? 'text-film-red'
                            : 'text-film-cream/50'
                      }`}
                    >
                      {film.currentPrice <= film.lowestPrice * 1.1
                        ? '接近低价'
                        : film.currentPrice >= film.highestPrice * 0.9
                          ? '接近高价'
                          : '中等价位'}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default TrendAnalysis;
