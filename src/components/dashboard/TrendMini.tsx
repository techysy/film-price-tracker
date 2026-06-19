import React from 'react';
import ReactECharts from 'echarts-for-react';

interface TrendMiniProps {
  data: number[];
  color?: string;
}

const TrendMini: React.FC<TrendMiniProps> = ({ data, color = '#f5c542' }) => {
  const option = {
    grid: {
      left: 0,
      right: 0,
      top: 5,
      bottom: 5,
    },
    xAxis: {
      type: 'category',
      show: false,
      data: data.map((_, i) => i),
    },
    yAxis: {
      type: 'value',
      show: false,
    },
    series: [
      {
        data: data,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: color,
          width: 2,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: color + '40' },
              { offset: 1, color: color + '00' },
            ],
          },
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: 40, width: '100%' }} />;
};

export default TrendMini;
