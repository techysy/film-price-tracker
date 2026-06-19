import { Router } from 'express';
import {
  getFilms,
  getFilmById,
  getBrands,
  getFilmsByBrand,
  getDashboardData,
} from '../../src/data/mockData.js';

const router = Router();

router.get('/films', (req, res) => {
  const { brand } = req.query;
  if (brand) {
    res.json({
      success: true,
      data: getFilmsByBrand(brand as string),
    });
  } else {
    res.json({
      success: true,
      data: getFilms(),
    });
  }
});

router.get('/films/:id', (req, res) => {
  const film = getFilmById(req.params.id);
  if (film) {
    res.json({
      success: true,
      data: film,
    });
  } else {
    res.status(404).json({
      success: false,
      error: 'Film not found',
    });
  }
});

router.get('/films/:id/trend', (req, res) => {
  const film = getFilmById(req.params.id);
  if (film) {
    const days = parseInt(req.query.days as string) || 30;
    res.json({
      success: true,
      data: film.priceHistory.slice(-days),
    });
  } else {
    res.status(404).json({
      success: false,
      error: 'Film not found',
    });
  }
});

router.get('/brands', (req, res) => {
  res.json({
    success: true,
    data: getBrands(),
  });
});

router.get('/dashboard', (req, res) => {
  res.json({
    success: true,
    data: getDashboardData(),
  });
});

export default router;
