import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'yellow' | 'red' | 'green';
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const variantClasses = {
    default: 'bg-film-cream/10 text-film-cream/80',
    yellow: 'bg-film-yellow/20 text-film-yellow',
    red: 'bg-film-red/20 text-film-red',
    green: 'bg-film-green/20 text-film-green',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-body font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
