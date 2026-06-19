import React from 'react';
import Card from '../common/Card';

interface FilterBarProps {
  brands: string[];
  formats: string[];
  selectedBrand: string;
  selectedFormat: string;
  onBrandChange: (brand: string) => void;
  onFormatChange: (format: string) => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  brands,
  formats,
  selectedBrand,
  selectedFormat,
  onBrandChange,
  onFormatChange,
}) => {
  return (
    <Card className="p-4">
      <div className="flex flex-wrap items-center gap-6">
        <div>
          <label className="block text-xs text-film-cream/50 font-body mb-2">品牌</label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onBrandChange('')}
              className={`px-4 py-1.5 rounded-full text-sm font-body transition-all ${
                selectedBrand === ''
                  ? 'bg-film-yellow text-film-dark'
                  : 'bg-film-dark/60 text-film-cream/70 hover:bg-film-yellow/10'
              }`}
            >
              全部
            </button>
            {brands.map((brand) => (
              <button
                key={brand}
                onClick={() => onBrandChange(brand)}
                className={`px-4 py-1.5 rounded-full text-sm font-body transition-all ${
                  selectedBrand === brand
                    ? 'bg-film-yellow text-film-dark'
                    : 'bg-film-dark/60 text-film-cream/70 hover:bg-film-yellow/10'
                }`}
              >
                {brand}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs text-film-cream/50 font-body mb-2">规格</label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onFormatChange('')}
              className={`px-4 py-1.5 rounded-full text-sm font-body transition-all ${
                selectedFormat === ''
                  ? 'bg-film-yellow text-film-dark'
                  : 'bg-film-dark/60 text-film-cream/70 hover:bg-film-yellow/10'
              }`}
            >
              全部
            </button>
            {formats.map((format) => (
              <button
                key={format}
                onClick={() => onFormatChange(format)}
                className={`px-4 py-1.5 rounded-full text-sm font-body transition-all ${
                  selectedFormat === format
                    ? 'bg-film-yellow text-film-dark'
                    : 'bg-film-dark/60 text-film-cream/70 hover:bg-film-yellow/10'
                }`}
              >
                {format}
              </button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default FilterBar;
