from flask import Flask, render_template, jsonify
from models.film import session, Film, PriceHistory
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    """首页，展示胶卷列表"""
    films = session.query(Film).all()
    return render_template('index.html', films=films)

@app.route('/film/<int:film_id>')
def film_detail(film_id):
    """胶卷详情页，展示价格历史趋势"""
    film = session.query(Film).filter_by(id=film_id).first()
    if not film:
        return "胶卷不存在", 404
    
    # 获取价格历史数据
    price_histories = session.query(PriceHistory).filter_by(film_id=film_id).order_by(PriceHistory.timestamp).all()
    
    # 准备图表数据
    labels = []
    prices = []
    platforms = {}
    
    for ph in price_histories:
        labels.append(ph.timestamp.strftime('%Y-%m-%d %H:%M'))
        prices.append(ph.price)
        
        # 按平台分组
        if ph.platform not in platforms:
            platforms[ph.platform] = []
        platforms[ph.platform].append({
            'x': ph.timestamp.strftime('%Y-%m-%d %H:%M'),
            'y': ph.price
        })
    
    return render_template('film_detail.html', film=film, platforms=platforms)

@app.route('/api/price_history/<int:film_id>')
def api_price_history(film_id):
    """API接口，返回价格历史数据"""
    price_histories = session.query(PriceHistory).filter_by(film_id=film_id).order_by(PriceHistory.timestamp).all()
    
    data = []
    for ph in price_histories:
        data.append({
            'timestamp': ph.timestamp.isoformat(),
            'price': ph.price,
            'platform': ph.platform,
            'url': ph.url
        })
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
