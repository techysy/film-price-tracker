import React from 'react';
import { Link } from 'react-router-dom';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { ArrowRight } from 'lucide-react';
import type { Film } from '../../data/mockData';

interface HotFilmsProps {
  films: Film[];
}

const HotFilms: React.FC<HotFilmsProps> = ({ films }) => {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display text-lg font-semibold text-film-cream">热门胶片</h3>
        <Link
          to="/trends"
          className="flex items-center gap-1 text-sm text-film-yellow hover:text-film-yellow/80 transition-colors font-body"
        >
          查看更多 <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {films.slice(0, 8).map((film) => (
          <Link
            key={film.id}
            to={`/detail/${film.id}`}
            className="group p-3 rounded-lg bg-film-dark/60 border border-film-yellow/5 hover:border-film-yellow/30 transition-all duration-200"
          >
            <div className="flex items-start justify-between mb-2">
              <Badge variant="yellow">{film.brand}</Badge>
              <span className="text-xs text-film-cream/40 font-body">{film.format}</span>
            </div>
            <h4 className="font-body text-sm text-film-cream group-hover:text-film-yellow transition-colors line-clamp-1">
              {film.name}
            </h4>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="text-lg font-display font-bold text-film-yellow">¥{film.currentPrice}</span>
              <span className="text-xs text-film-cream/40 font-body">/卷</span>
            </div>
          </Link>
        ))}
      </div>
    </Card>
  );
};

export default HotFilms;
