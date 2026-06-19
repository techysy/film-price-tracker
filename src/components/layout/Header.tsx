import React from 'react';
import { Bell, RefreshCw } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="h-16 bg-film-dark/50 backdrop-blur-sm border-b border-film-yellow/10 sticky top-0 z-40">
      <div className="h-full px-6 flex items-center justify-between">
        <div>
          <h2 className="font-display text-xl font-semibold text-film-cream">{title}</h2>
          {subtitle && <p className="text-sm text-film-cream/50 font-body">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 rounded-lg hover:bg-film-yellow/10 transition-colors group">
            <RefreshCw className="w-5 h-5 text-film-cream/50 group-hover:text-film-yellow transition-colors" />
          </button>
          <button className="p-2 rounded-lg hover:bg-film-yellow/10 transition-colors relative">
            <Bell className="w-5 h-5 text-film-cream/50 group-hover:text-film-yellow transition-colors" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-film-red rounded-full" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
