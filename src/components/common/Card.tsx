import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({ children, className = '', hover = false, onClick }) => {
  return (
    <div
      className={`bg-film-dark/80 border border-film-yellow/10 rounded-xl backdrop-blur-sm ${
        hover ? 'hover:border-film-yellow/30 hover:shadow-lg hover:shadow-film-yellow/5 transition-all duration-300 cursor-pointer' : ''
      } ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;
