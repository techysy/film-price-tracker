import React, { useEffect, useState } from 'react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import ReactECharts from 'echarts-for-react';
import { X, Plus } from 'lucide-react';
import type { Film } from '../data/mockData';

const BrandCompare: React.FC = () => {
  const [films, setFilms] = useState<Film[]>([]);
  const [selectedFilms, setSelectedFilms] = useState<Film[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/films')
      .then((res) => res.json())
      .then((res) => {
        if (res.success) setFilms(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const addFilm = (film: Film) => {
    if (selectedFilms.length < 4 && !selectedFilms.find((f) => f.id === film.id)) {
      setSelectedFilms([...selectedFilms, film]);
    }
    setShowDropdown(false);
  };

  const removeFilm = (id: string) => {
    setSelectedFilms(selectedFilms.filter((f) => f.id !== id));
  };

  const barChartOption = {
    backgroundColor: 'transparent',
    title: {
      text: '价格对比',
      textStyle: { color: '#faf8f5', fontSize: 16, fontFamily: 'Playfair Display' },
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1a1a',
      borderColor: '#f5c542',
      textStyle: { color: '#faf8f5' },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      data: selectedFilms.map((f) => f.name),
      axisLine: { lineStyle: { color: '#f5c54230' } },
      axisLabel: { color: '#faf8f580', fontFamily: 'Source Sans 3', rotate: 15 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f5c54210' } },
      axisLabel: { color: '#faf8f580', formatter: '¥{value}', fontFamily: 'Source Sans 3' },
    },
    series: [
      {
        data: selectedFilms.map((f, i) => ({
          value: f.currentPrice,
          itemStyle: { color: ['#f5c542', '#c44536', '#4a5d23', '#3d2b1f'][i % 4] },
        })),
        type: 'bar',
        barWidth: '50%',
        label: { show: true, color: '#faf8f5', formatter: '¥{c}', fontFamily: 'Source Sans 3' },
      },
    ],
  };

  const radarChartOption = {
    backgroundColor: 'transparent',
    title: {
      text: '性价比分析',
      subtext: '价格越低、稳定性越高，得分越高',
      textStyle: { color: '#faf8f5', fontSize: 16, fontFamily: 'Playfair Display' },
      subtextStyle: { color: '#faf8f580', fontSize: 11, fontFamily: 'Source Sans 3' },
      left: 'center',
    },
    tooltip: { trigger: 'item', backgroundColor: '#1a1a1a', borderColor: '#f5c542', textStyle: { color: '#faf8f5' } },
    radar: {
      indicator: [
        { name: '价格优势', max: 100 },
        { name: '价格稳定', max: 100 },
        { name: '历史最低', max: 100 },
      ],
      axisName: { color: '#faf8f580', fontFamily: 'Source Sans 3' },
      splitLine: { lineStyle: { color: '#f5c54220' } },
      splitArea: { areaStyle: { color: ['#1a1a1a00', '#1a1a1a30'] } },
    },
    series: [
      {
        type: 'radar',
        data: selectedFilms.map((f, i) => ({
          value: [
            Math.round((1 - f.currentPrice / 150) * 100),
            Math.round((1 - (f.highestPrice - f.lowestPrice) / f.lowestPrice) * 100),
            Math.round((1 - (f.currentPrice - f.lowestPrice) / f.lowestPrice) * 100),
          ],
          name: f.name,
          lineStyle: { color: ['#f5c542', '#c44536', '#4a5d23', '#3d2b1f'][i % 4] },
          areaStyle: { color: ['#f5c542', '#c44536', '#4a5d23', '#3d2b1f'][i % 4] + '40' },
        })),
      },
    ],
  };

  if (loading) {
    return (
      <Layout title="品牌对比" subtitle="横向对比不同胶片">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-film-yellow">加载中...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="品牌对比" subtitle="横向对比不同胶片">
      <div className="space-y-6">
        <Card className="p-5">
          <h3 className="font-display text-lg font-semibold text-film-cream mb-4">选择胶片对比（最多4款）</h3>

          <div className="flex flex-wrap gap-2 mb-4">
            {selectedFilms.map((film) => (
              <div
                key={film.id}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-film-yellow/10 border border-film-yellow/30"
              >
                <Badge variant="yellow">{film.brand}</Badge>
                <span className="text-sm text-film-cream font-body">{film.name}</span>
                <button onClick={() => removeFilm(film.id)} className="text-film-cream/50 hover:text-film-red transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}

            {selectedFilms.length < 4 && (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-film-yellow/30 text-film-yellow hover:bg-film-yellow/10 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span className="text-sm font-body">添加胶片</span>
                </button>

                {showDropdown && (
                  <div className="absolute top-full left-0 mt-2 w-72 max-h-64 overflow-y-auto bg-film-dark border border-film-yellow/20 rounded-lg shadow-xl z-50">
                    {films
                      .filter((f) => !selectedFilms.find((s) => s.id === f.id))
                      .map((film) => (
                        <button
                          key={film.id}
                          onClick={() => addFilm(film)}
                          className="w-full px-4 py-2 text-left hover:bg-film-yellow/10 transition-colors flex items-center justify-between"
                        >
                          <div>
                            <div className="text-sm text-film-cream font-body">{film.name}</div>
                            <div className="text-xs text-film-cream/50 font-body">{film.brand}</div>
                          </div>
                          <span className="text-lg font-display font-bold text-film-yellow">¥{film.currentPrice}</span>
                        </button>
                      ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>

        {selectedFilms.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-5">
              <ReactECharts option={barChartOption} style={{ height: 350 }} />
            </Card>
            <Card className="p-5">
              <ReactECharts option={radarChartOption} style={{ height: 350 }} />
            </Card>
          </div>
        ) : (
          <Card className="p-12 text-center">
            <div className="text-film-cream/30 font-display text-6xl mb-4">📷</div>
            <p className="text-film-cream/50 font-body">选择胶片开始对比</p>
          </Card>
        )}

        {selectedFilms.length > 0 && (
          <Card className="p-5">
            <h3 className="font-display text-lg font-semibold text-film-cream mb-4">详细对比</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-film-yellow/10">
                    <th className="text-left py-3 px-4 text-sm text-film-cream/50 font-body font-medium">胶片</th>
                    <th className="text-right py-3 px-4 text-sm text-film-cream/50 font-body font-medium">当前价格</th>
                    <th className="text-right py-3 px-4 text-sm text-film-cream/50 font-body font-medium">最低价</th>
                    <th className="text-right py-3 px-4 text-sm text-film-cream/50 font-body font-medium">最高价</th>
                    <th className="text-right py-3 px-4 text-sm text-film-cream/50 font-body font-medium">波动幅度</th>
                    <th className="text-right py-3 px-4 text-sm text-film-cream/50 font-body font-medium">建议</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedFilms.map((film) => {
                    const volatility = Math.round(((film.highestPrice - film.lowestPrice) / film.lowestPrice) * 100);
                    const isLow =
                      film.currentPrice <= film.lowestPrice * 1.1;
                    return (
                      <tr key={film.id} className="border-b border-film-yellow/5 hover:bg-film-yellow/5 transition-colors">
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <Badge variant="yellow">{film.brand}</Badge>
                            <span className="text-sm text-film-cream font-body">{film.name}</span>
                          </div>
                        </td>
                        <td className="text-right py-3 px-4">
                          <span className="text-lg font-display font-bold text-film-yellow">¥{film.currentPrice}</span>
                        </td>
                        <td className="text-right py-3 px-4">
                          <span className="text-sm text-film-green font-body">¥{film.lowestPrice}</span>
                        </td>
                        <td className="text-right py-3 px-4">
                          <span className="text-sm text-film-red font-body">¥{film.highestPrice}</span>
                        </td>
                        <td className="text-right py-3 px-4">
                          <span className="text-sm text-film-cream/70 font-body">{volatility}%</span>
                        </td>
                        <td className="text-right py-3 px-4">
                          <span
                            className={`text-sm font-body ${isLow ? 'text-film-green' : 'text-film-cream/50'}`}
                          >
                            {isLow ? '推荐购买' : '观望'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default BrandCompare;
