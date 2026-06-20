from datetime import datetime
from flask import Blueprint, render_template, jsonify
from models.film import SessionLocal, Film, PriceHistory

main = Blueprint('main', __name__)


@main.route('/')
def index():
    session = SessionLocal()
    try:
        films = session.query(Film).all()
        return render_template('index.html', films=films)
    finally:
        session.close()


@main.route('/film/<int:film_id>')
def film_detail(film_id):
    session = SessionLocal()
    try:
        film = session.query(Film).filter_by(id=film_id).first()
        if not film:
            return "胶卷不存在", 404

        price_histories = (
            session.query(PriceHistory)
            .filter_by(film_id=film_id)
            .order_by(PriceHistory.timestamp)
            .all()
        )

        platforms = {}
        for ph in price_histories:
            if ph.platform not in platforms:
                platforms[ph.platform] = []
            platforms[ph.platform].append({
                'x': ph.timestamp.strftime('%Y-%m-%d %H:%M'),
                'y': ph.price
            })

        return render_template('film_detail.html', film=film, platforms=platforms)
    finally:
        session.close()


@main.route('/api/price_history/<int:film_id>')
def api_price_history(film_id):
    session = SessionLocal()
    try:
        price_histories = (
            session.query(PriceHistory)
            .filter_by(film_id=film_id)
            .order_by(PriceHistory.timestamp)
            .all()
        )

        data = [
            {
                'timestamp': ph.timestamp.isoformat(),
                'price': ph.price,
                'platform': ph.platform,
                'url': ph.url
            }
            for ph in price_histories
        ]

        return jsonify(data)
    finally:
        session.close()
