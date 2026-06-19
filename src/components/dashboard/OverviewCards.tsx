import React from 'react';
import Card from '../common/Card';
import { Film, Building2, TrendingUp, Clock } from 'lucide-react';

interface OverviewCardsProps {
  data: {
    totalFilms: number;
    totalBrands: number;
    avgPrice: number;
  };
}

const OverviewCards: React.FC<OverviewCardsProps> = ({ data }) => {
  const cards = [
    {
      icon: Film,
      label: '在售胶片',
      value: data.totalFilms,
      suffix: '款',
      color: 'text-film-yellow',
    },
    {
      icon: Building2,
      label: '涉及品牌',
      value: data.totalBrands,
      suffix: '个',
      color: 'text-film-green',
    },
    {
      icon: TrendingUp,
      label: '平均价格',
      value: data.avgPrice,
      prefix: '¥',
      suffix: '',
      color: 'text-film-red',
    },
    {
      icon: Clock,
      label: '数据更新',
      value: '今日',
      suffix: '',
      color: 'text-film-cream/60',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((item, index) => (
        <Card key={index} className="p-5 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-film-yellow/5 to-transparent rounded-bl-full" />
          <div className="relative">
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg bg-film-yellow/10 ${item.color}`}>
                <item.icon className="w-5 h-5" />
              </div>
              <span className="text-sm text-film-cream/50 font-body">{item.label}</span>
            </div>
            <div className="flex items-baseline gap-1">
              {item.prefix && <span className="text-lg text-film-cream/60 font-body">{item.prefix}</span>}
              <span className="text-3xl font-display font-bold text-film-cream">{item.value}</span>
              {item.suffix && <span className="text-lg text-film-cream/60 font-body ml-1">{item.suffix}</span>}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default OverviewCards;
