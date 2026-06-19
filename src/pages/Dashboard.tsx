import React, { useEffect, useState } from 'react';
import Layout from '../components/layout/Layout';
import OverviewCards from '../components/dashboard/OverviewCards';
import HotFilms from '../components/dashboard/HotFilms';
import Card from '../components/common/Card';
import TrendMini from '../components/dashboard/TrendMini';
import ReactECharts from 'echarts-for-react';
import type { Film } from '../data/mockData';

interface DashboardData {
  totalFilms: number;
  totalBrands: number;
  avgPrice: number;
  hotFilms: Film[];
  priceTrends: { name: string; data: number[] }[];
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/dashboard')
      .then((res) => res.json())
      .then((res) => {
        if (res.success) {
          setData(res.data);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Layout title="仪表盘" subtitle="胶片价格一览">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-film-yellow">加载中...</div>
        </div>
      </Layout>
    );
  }

  if (!data) {
    return (
      <Layout title="仪表盘" subtitle="胶片价格一览">
        <div className="flex items-center justify-center h-64">
          <div className="text-film-cream/50">暂无数据</div>
        </div>
      </Layout>
    );
  }

  const chartOption = {
    backgroundColor: 'transparent',
    title: {
      text: '热门胶片 7 日价格走势',
      textStyle: {
        color: '#faf8f5',
        fontSize: 16,
        fontFamily: 'Playfair Display',
      },
      left: 0,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1a1a',
      borderColor: '#f5c542',
      textStyle: { color: '#faf8f5' },
    },
    legend: {
      data: data.priceTrends.map((t) => t.name),
      textStyle: { color: '#faf8f5', fontFamily: 'Source Sans 3' },
      top: 0,
      right: 0,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: '#f5c54230' } },
      axisLabel: { color: '#faf8f580' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f5c54210' } },
      axisLabel: { color: '#faf8f580' },
    },
    series: data.priceTrends.map((trend, index) => ({
      name: trend.name,
      type: 'line',
      smooth: true,
      data: trend.data,
      lineStyle: { width: 2 },
      itemStyle: { color: ['#f5c542', '#c44536', '#4a5d23', '#3d2b1f'][index % 4] },
    })),
  };

  return (
    <Layout title="仪表盘" subtitle="胶片价格一览">
      <div className="space-y-6">
        <OverviewCards data={data} />

        <Card className="p-5">
          <ReactECharts option={chartOption} style={{ height: 350 }} />
        </Card>

        <HotFilms films={data.hotFilms} />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {data.priceTrends.map((trend, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-film-cream/50 font-body truncate max-w-[120px]">{trend.name}</span>
                <TrendMini
                  data={trend.data}
                  color={['#f5c542', '#c44536', '#4a5d23', '#3d2b1f'][index % 4]}
                />
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-display font-bold text-film-yellow">
                  ¥{trend.data[trend.data.length - 1]}
                </span>
                <span className="text-xs text-film-cream/40 font-body">最新</span>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
