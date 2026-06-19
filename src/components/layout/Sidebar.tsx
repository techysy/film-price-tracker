import React from 'react';
import { NavLink } from 'react-router-dom';
import { Camera, TrendingUp, GitCompare, LayoutDashboard } from 'lucide-react';

const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: '仪表盘' },
    { to: '/trends', icon: TrendingUp, label: '价格趋势' },
    { to: '/compare', icon: GitCompare, label: '品牌对比' },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-film-dark border-r border-film-yellow/20 z-50">
      <div className="p-6 border-b border-film-yellow/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-film-yellow flex items-center justify-center">
            <Camera className="w-6 h-6 text-film-dark" />
          </div>
          <div>
            <h1 className="font-display text-lg font-semibold text-film-cream">胶片价格</h1>
            <p className="text-xs text-film-yellow/60">Film Price Tracker</p>
          </div>
        </div>
      </div>

      <nav className="p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-film-yellow/10 text-film-yellow border-l-2 border-film-yellow'
                      : 'text-film-cream/70 hover:bg-film-yellow/5 hover:text-film-cream'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span className="font-body">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-film-yellow/10">
        <div className="text-xs text-film-cream/40 font-body">
          <p>数据每日更新</p>
          <p className="mt-1">模拟数据仅供演示</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
