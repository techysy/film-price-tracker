import React from 'react';
import ReactECharts from 'echarts-for-react';
import type { Film } from '../../data/mockData';

interface PriceChartProps {
  film: Film;
}

const PriceChart: React.FC<PriceChartProps> = ({ film }) => {
  const dates = film.priceHistory.map((p) => p.date.slice(5));
  const prices = film.priceHistory.map((p) => p.price);

  const option = {
    backgroundColor: 'transparent',
    title: {
      text: film.name,
      subtext: `${film.brand} · ${film.type} · ${film.format}`,
      left: 'center',
      textStyle: {
        color: '#faf8f5',
        fontSize: 18,
        fontFamily: 'Playfair Display',
      },
      subtextStyle: {
        color: '#faf8f580',
        fontSize: 13,
        fontFamily: 'Source Sans 3',
      },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1a1a1a',
      borderColor: '#f5c542',
      textStyle: { color: '#faf8f5' },
      formatter: (params: any) => {
        const p = params[0];
        return `<strong>${p.axisValue}</strong><br/>价格: ¥${p.value}`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#f5c54230' } },
      axisLabel: { color: '#faf8f580', fontFamily: 'Source Sans 3' },
    },
    yAxis: {
      type: 'value',
      min: Math.floor(film.lowestPrice * 0.95),
      max: Math.ceil(film.highestPrice * 1.05),
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f5c54210' } },
      axisLabel: {
        color: '#faf8f580',
        formatter: '¥{value}',
        fontFamily: 'Source Sans 3',
      },
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
        data: prices,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 3, color: '#f5c542' },
        itemStyle: { color: '#f5c542' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
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

  return <ReactECharts option={option} style={{ height: 400 }} />;
};

export default PriceChart;
