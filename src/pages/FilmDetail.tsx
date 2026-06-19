import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import ReactECharts from 'echarts-for-react';
import { ArrowLeft, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { Film } from '../data/mockData';

const FilmDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [film, setFilm] = useState<Film | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetch(`/api/films/${id}`)
        .then((res) => res.json())
        .then((res) => {
          if (res.success) setFilm(res.data);
        })
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return (
      <Layout title="胶片详情">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-film-yellow">加载中...</div>
        </div>
      </Layout>
    );
  }

  if (!film) {
    return (
      <Layout title="胶片详情">
        <div className="flex items-center justify-center h-64">
          <div className="text-film-cream/50">胶片不存在</div>
        </div>
      </Layout>
    );
  }

  const priceChange = film.priceHistory.length >= 2 ? film.priceHistory[film.priceHistory.length - 1].price - film.priceHistory[film.priceHistory.length - 2].price : 0;
  const changePercent = film.priceHistory.length >= 2 ? ((priceChange / film.priceHistory[film.priceHistory.length - 2].price) * 100).toFixed(1) : '0';

  const chartOption = {
    backgroundColor: 'transparent',
    title: {
      text: '价格历史走势',
      textStyle: { color: '#faf8f5', fontSize: 16, fontFamily: 'Playfair Display' },
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1a1a',
      borderColor: '#f5c542',
      textStyle: { color: '#faf8f5' },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: film.priceHistory.map((p) => p.date.slice(5)),
      axisLine: { lineStyle: { color: '#f5c54230' } },
      axisLabel: { color: '#faf8f580', fontFamily: 'Source Sans 3' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f5c54210' } },
      axisLabel: { color: '#faf8f580', formatter: '¥{value}', fontFamily: 'Source Sans 3' },
    },
    visualMap: {
      show: false,
      pieces: [
        { lte: film.lowestPrice * 1.05, color: '#4a5d23' },
        { gt: film.lowestPrice * 1.05, lte: film.highestPrice * 0.95, color: '#f5c542' },
        { gt: film.highestPrice * 0.95, color: '#c44536' },
      ],
    },
    series: [
      {
        data: film.priceHistory.map((p) => p.price),
        type: 'line',
        smooth: true,
        lineStyle: { width: 2, color: '#f5c542' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#f5c54230' },
              { offset: 1, color: '#f5c54200' },
            ],
          },
        },
        markLine: {
          silent: true,
          lineStyle: { color: '#4a5d2380', type: 'dashed' },
          data: [
            { yAxis: film.lowestPrice, label: { formatter: '最低', color: '#4a5d23' } },
            { yAxis: film.highestPrice, label: { formatter: '最高', color: '#c44536' } },
          ],
        },
      },
    ],
  };

  const platformData = film.priceHistory.reduce((acc, p) => {
    if (!acc[p.platform]) acc[p.platform] = { count: 0, prices: [] };
    acc[p.platform].count++;
    acc[p.platform].prices.push(p.price);
    return acc;
  }, {} as Record<string, { count: number; prices: number[] }>);

  return (
    <Layout title={film.name} subtitle={`${film.brand} · ${film.type}`}>
      <div className="space-y-6">
        <Link
          to="/trends"
          className="inline-flex items-center gap-2 text-film-cream/50 hover:text-film-yellow transition-colors font-body"
        >
          <ArrowLeft className="w-4 h-4" /> 返回趋势分析
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <Badge variant="yellow" className="mb-2">{film.brand}</Badge>
                <h2 className="font-display text-2xl font-bold text-film-cream">{film.name}</h2>
                <p className="text-film-cream/50 font-body mt-1">{film.type} · {film.format}格式</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-sm text-film-cream/50 font-body">当前价格</p>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-4xl font-display font-bold text-film-yellow">¥{film.currentPrice}</span>
                    <span className="text-film-cream/40 font-body">/卷</span>
                  </div>
                </div>
                <div className={`flex items-center gap-1 ${priceChange > 0 ? 'text-film-red' : priceChange < 0 ? 'text-film-green' : 'text-film-cream/50'}`}>
                  {priceChange > 0 ? <TrendingUp className="w-4 h-4" /> : priceChange < 0 ? <TrendingDown className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                  <span className="text-sm font-body">{priceChange > 0 ? '+' : ''}{changePercent}%</span>
                </div>
              </div>

              <div className="pt-4 border-t border-film-yellow/10">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-film-cream/50 font-body">历史最低</p>
                    <p className="text-lg font-display font-bold text-film-green mt-1">¥{film.lowestPrice}</p>
                  </div>
                  <div>
                    <p className="text-xs text-film-cream/50 font-body">历史最高</p>
                    <p className="text-lg font-display font-bold text-film-red mt-1">¥{film.highestPrice}</p>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-film-yellow/10">
                <div className="flex items-center gap-2 text-film-cream/50 font-body">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs">最后更新: {new Date(film.updateTime).toLocaleDateString('zh-CN')}</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-5 lg:col-span-2">
            <ReactECharts option={chartOption} style={{ height: 350 }} />
          </Card>
        </div>

        <Card className="p-5">
          <h3 className="font-display text-lg font-semibold text-film-cream mb-4">价格来源分布</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(platformData).map(([platform, data]) => (
              <div key={platform} className="p-4 rounded-lg bg-film-dark/60 border border-film-yellow/5">
                <p className="text-sm text-film-cream/50 font-body">{platform}</p>
                <p className="text-2xl font-display font-bold text-film-yellow mt-1">{data.count}次</p>
                <p className="text-xs text-film-cream/40 font-body mt-1">
                  均價 ¥{Math.round(data.prices.reduce((a, b) => a + b, 0) / data.prices.length)}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default FilmDetail;
