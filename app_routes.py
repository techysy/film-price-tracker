from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from models.film import SessionLocal, Film, PriceHistory, TaobaoStore

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


@main.route('/stores')
def stores():
    session = SessionLocal()
    try:
        store_list = session.query(TaobaoStore).order_by(TaobaoStore.created_at.desc()).all()
        return render_template('stores.html', stores=store_list)
    finally:
        session.close()


@main.route('/stores/add', methods=['POST'])
def store_add():
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    if not name or not url:
        flash('店铺名称和URL不能为空', 'danger')
        return redirect(url_for('main.stores'))
    session = SessionLocal()
    try:
        store = TaobaoStore(name=name, url=url)
        session.add(store)
        session.commit()
        flash(f'店铺 "{name}" 添加成功', 'success')
    except Exception as e:
        session.rollback()
        flash(f'添加失败: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('main.stores'))


@main.route('/stores/edit/<int:store_id>', methods=['POST'])
def store_edit(store_id):
    session = SessionLocal()
    try:
        store = session.query(TaobaoStore).get(store_id)
        if not store:
            flash('店铺不存在', 'danger')
            return redirect(url_for('main.stores'))
        name = request.form.get('name', '').strip()
        url = request.form.get('url', '').strip()
        enabled = request.form.get('enabled') == 'on'
        if name:
            store.name = name
        if url:
            store.url = url
        store.enabled = enabled
        session.commit()
        flash(f'店铺 "{store.name}" 已更新', 'success')
    except Exception as e:
        session.rollback()
        flash(f'更新失败: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('main.stores'))


@main.route('/stores/delete/<int:store_id>', methods=['POST'])
def store_delete(store_id):
    session = SessionLocal()
    try:
        store = session.query(TaobaoStore).get(store_id)
        if not store:
            flash('店铺不存在', 'danger')
            return redirect(url_for('main.stores'))
        name = store.name
        session.delete(store)
        session.commit()
        flash(f'店铺 "{name}" 已删除', 'success')
    except Exception as e:
        session.rollback()
        flash(f'删除失败: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('main.stores'))
