export interface PricePoint {
  date: string;
  price: number;
  platform: string;
}

export interface Film {
  id: string;
  name: string;
  brand: string;
  type: string;
  format: string;
  currentPrice: number;
  lowestPrice: number;
  highestPrice: number;
  priceHistory: PricePoint[];
  updateTime: string;
}

export interface Brand {
  id: string;
  name: string;
  country: string;
  filmCount: number;
}

const brands: Brand[] = [
  { id: 'kodak', name: 'Kodak', country: '美国', filmCount: 12 },
  { id: 'fujifilm', name: 'Fujifilm', country: '日本', filmCount: 8 },
  { id: 'ilford', name: 'Ilford', country: '英国', filmCount: 6 },
  { id: 'foma', name: 'Fomapan', country: '捷克', filmCount: 4 },
  { id: 'cinestill', name: 'CineStill', country: '美国', filmCount: 3 },
  { id: 'lomography', name: 'Lomography', country: '奥地利', filmCount: 5 },
];

function generatePriceHistory(basePrice: number, days: number = 30): PricePoint[] {
  const history: PricePoint[] = [];
  const now = new Date();
  let price = basePrice * (0.85 + Math.random() * 0.1);

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const change = (Math.random() - 0.45) * 5;
    price = Math.max(price * 0.9, Math.min(price * 1.1, price + change));

    const platforms = ['京东', '天猫', '拼多多', '亚马逊'];
    history.push({
      date: date.toISOString().split('T')[0],
      price: Math.round(price * 100) / 100,
      platform: platforms[Math.floor(Math.random() * platforms.length)],
    });
  }

  history[history.length - 1].price = basePrice;
  return history;
}

const films: Film[] = [
  {
    id: 'kodak-portra-400-135',
    name: 'Kodak Portra 400',
    brand: 'Kodak',
    type: '彩色负片',
    format: '135',
    currentPrice: 68,
    lowestPrice: 58,
    highestPrice: 85,
    priceHistory: generatePriceHistory(68),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'kodak-gold-200-135',
    name: 'Kodak Gold 200',
    brand: 'Kodak',
    type: '彩色负片',
    format: '135',
    currentPrice: 42,
    lowestPrice: 35,
    highestPrice: 52,
    priceHistory: generatePriceHistory(42),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'kodak-trix-400-135',
    name: 'Kodak Tri-X 400',
    brand: 'Kodak',
    type: '黑白负片',
    format: '135',
    currentPrice: 55,
    lowestPrice: 48,
    highestPrice: 68,
    priceHistory: generatePriceHistory(55),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'kodak-ektar-100-135',
    name: 'Kodak Ektar 100',
    brand: 'Kodak',
    type: '彩色负片',
    format: '135',
    currentPrice: 62,
    lowestPrice: 52,
    highestPrice: 75,
    priceHistory: generatePriceHistory(62),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'fuji-superia-400-135',
    name: 'Fujifilm Superia X-TRA 400',
    brand: 'Fujifilm',
    type: '彩色负片',
    format: '135',
    currentPrice: 38,
    lowestPrice: 32,
    highestPrice: 48,
    priceHistory: generatePriceHistory(38),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'fuji-pro-400h-135',
    name: 'Fujifilm Pro 400H',
    brand: 'Fujifilm',
    type: '彩色负片',
    format: '135',
    currentPrice: 85,
    lowestPrice: 72,
    highestPrice: 98,
    priceHistory: generatePriceHistory(85),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'fuji-velvia-50-135',
    name: 'Fujifilm Velvia 50',
    brand: 'Fujifilm',
    type: '彩色反转片',
    format: '135',
    currentPrice: 75,
    lowestPrice: 65,
    highestPrice: 92,
    priceHistory: generatePriceHistory(75),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'fuji-acros-100-135',
    name: 'Fujifilm Neopan ACROS 100',
    brand: 'Fujifilm',
    type: '黑白负片',
    format: '135',
    currentPrice: 52,
    lowestPrice: 45,
    highestPrice: 65,
    priceHistory: generatePriceHistory(52),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'ilford-hp5-400-135',
    name: 'Ilford HP5 PLUS 400',
    brand: 'Ilford',
    type: '黑白负片',
    format: '135',
    currentPrice: 35,
    lowestPrice: 28,
    highestPrice: 45,
    priceHistory: generatePriceHistory(35),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'ilford-delta-3200-135',
    name: 'Ilford Delta 3200',
    brand: 'Ilford',
    type: '黑白负片',
    format: '135',
    currentPrice: 58,
    lowestPrice: 48,
    highestPrice: 72,
    priceHistory: generatePriceHistory(58),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'cinestill-800t-135',
    name: 'CineStill 800T',
    brand: 'CineStill',
    type: '彩色负片',
    format: '135',
    currentPrice: 78,
    lowestPrice: 65,
    highestPrice: 95,
    priceHistory: generatePriceHistory(78),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'fomapan-100-135',
    name: 'Fomapan 100',
    brand: 'Fomapan',
    type: '黑白负片',
    format: '135',
    currentPrice: 22,
    lowestPrice: 18,
    highestPrice: 28,
    priceHistory: generatePriceHistory(22),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'kodak-portra-400-120',
    name: 'Kodak Portra 400',
    brand: 'Kodak',
    type: '彩色负片',
    format: '120',
    currentPrice: 128,
    lowestPrice: 108,
    highestPrice: 155,
    priceHistory: generatePriceHistory(128),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'fuji-gfx-100s-4x5',
    name: 'Fujifilm GFX 100S',
    brand: 'Fujifilm',
    type: '彩色负片',
    format: '4x5',
    currentPrice: 850,
    lowestPrice: 750,
    highestPrice: 980,
    priceHistory: generatePriceHistory(850),
    updateTime: new Date().toISOString(),
  },
  {
    id: 'lomo-lady-grey-400-135',
    name: 'Lomography Lady Grey 400',
    brand: 'Lomography',
    type: '黑白负片',
    format: '135',
    currentPrice: 32,
    lowestPrice: 26,
    highestPrice: 42,
    priceHistory: generatePriceHistory(32),
    updateTime: new Date().toISOString(),
  },
];

export const getFilms = (): Film[] => films;

export const getFilmById = (id: string): Film | undefined => {
  return films.find(f => f.id === id);
};

export const getBrands = (): Brand[] => brands;

export const getFilmsByBrand = (brand: string): Film[] => {
  return films.filter(f => f.brand.toLowerCase() === brand.toLowerCase());
};

export const getDashboardData = () => {
  const avgPrice = Math.round(films.reduce((sum, f) => sum + f.currentPrice, 0) / films.length);
  const hotFilms = [...films].sort(() => Math.random() - 0.5).slice(0, 8);

  const priceTrends = hotFilms.slice(0, 4).map(f => ({
    name: f.name,
    data: f.priceHistory.slice(-7).map(p => p.price),
  }));

  return {
    totalFilms: films.length,
    totalBrands: brands.length,
    avgPrice,
    hotFilms,
    priceTrends,
  };
};
