import io
import re
import base64
from datetime import datetime
from pathlib import Path
import json
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, Response
from PIL import Image
from models.film import SessionLocal, Film, PriceHistory, TaobaoStore

try:
    from rapidocr_onnxruntime import RapidOCR
    ocr_engine = RapidOCR()
except ImportError:
    ocr_engine = None

main = Blueprint('main', __name__)

FILM_BRANDS = [
    'kodak', '柯达', 'fujifilm', '富士', 'ilford', '伊尔福',
    'agfa', '爱克发', 'lomography', '乐魔'
]
FILM_FORMATS = ['35mm', '120', '135']
INSTANT_KEYWORDS = {'instax': '拍立得', '拍立得': '拍立得', 'polaroid': '宝丽来', '宝丽来': '宝丽来'}
UNKNOWN_BRAND = '其他'


def parse_product_name(name):
    brand = None
    model = name
    iso = None
    film_format = None

    for b in FILM_BRANDS:
        if b in name:
            brand = b
            model = name.replace(b, '').strip()
            break

    iso_match = re.search(r'ISO(\d+)', name, re.IGNORECASE)
    if not iso_match:
        iso_match = re.search(r'(\d+)度', name)
    if iso_match:
        iso = int(iso_match.group(1))

    for fmt in FILM_FORMATS:
        if fmt in name:
            film_format = fmt
            break
    if '135' in name:
        film_format = '35mm'

    if not film_format:
        for kw, fmt in INSTANT_KEYWORDS.items():
            if kw in name:
                film_format = fmt
                break

    return brand or UNKNOWN_BRAND, model, iso, film_format


def parse_ocr_lines(ocr_result):
    if not ocr_result:
        return []

    lines = []
    for item in ocr_result:
        if item and len(item) >= 2:
            text = item[1]
            lines.append(text)

    SKIP_PATTERNS = ['88VIP', '退货', '退款', '删除', '移入收藏', '商品规格', '含税', '有效期',
                     '立即购买', '已选', '库存', '配送', '服务', '保障', '评价']
    results = []
    current_store = ''
    pending_title = ''

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if any(kw in line for kw in SKIP_PATTERNS):
            continue
        if re.match(r'^[\d\s\-\+]+$', line):
            continue
        if line in ('淘宝', '天猫', '京东', '淘宝网'):
            continue
        if re.match(r'^[\d\s\-/]+$', line):
            continue

        price_match = re.search(r'[¥￥]\s*(\d+\.?\d*)', line)
        if price_match:
            price = float(price_match.group(1))
            if price <= 0:
                continue

            title_before = line[:price_match.start()].strip()
            if title_before and len(title_before) > 2:
                results.append({
                    'store': current_store or '未知店铺',
                    'title': title_before,
                    'price': price,
                })
                pending_title = ''
            elif pending_title:
                results.append({
                    'store': current_store or '未知店铺',
                    'title': pending_title,
                    'price': price,
                })
                pending_title = ''
            continue

        if len(line) > 5 and not current_store and not results:
            current_store = line
            continue

        if len(line) > 5:
            has_film_keyword = any(kw in line.lower() for kw in
                ['胶卷', '胶片', 'kodak', '柯达', 'fuji', '富士', 'ilford', '伊尔福',
                 '120', '135', '35mm', '负片', '反转', '彩负', '黑白', 'iso',
                 'portra', 'gold', 'ultra', 'ektar', 'provia', 'velvia', 'cinestill',
                 'fomapan', 'hp5', 'delta', 'pan400', 'colorplus', 'lomo', 'wolfen',
                 'orwo', 'agfa', 'cn400', 'cn800', 'nc400', '5207', '5219', '5203', '5222',
                 'phoenix', 'instax', 'polaroid', '宝丽来', '拍立得', '测试卷', '片头卷'])
            if has_film_keyword:
                pending_title = line

    return results


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


@main.route('/export/json')
def export_json():
    session = SessionLocal()
    try:
        films = session.query(Film).all()
        data = []
        for film in films:
            price_histories = (
                session.query(PriceHistory)
                .filter_by(film_id=film.id)
                .order_by(PriceHistory.timestamp)
                .all()
            )
            platforms = {}
            for ph in price_histories:
                if ph.platform not in platforms:
                    platforms[ph.platform] = []
                platforms[ph.platform].append({
                    'timestamp': ph.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'price': ph.price,
                    'url': ph.url,
                })
            data.append({
                'brand': film.brand,
                'model': film.model,
                'iso': film.iso,
                'format': film.format,
                'description': film.description,
                'platforms': platforms,
            })

        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename="film_price_tracker.json"'}
        )
    finally:
        session.close()


@main.route('/export/html')
def export_html():
    session = SessionLocal()
    try:
        films = session.query(Film).all()
        all_data = []
        for film in films:
            price_histories = (
                session.query(PriceHistory)
                .filter_by(film_id=film.id)
                .order_by(PriceHistory.timestamp)
                .all()
            )
            platforms = {}
            for ph in price_histories:
                if ph.platform not in platforms:
                    platforms[ph.platform] = []
                platforms[ph.platform].append({
                    'x': ph.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'y': ph.price,
                })
            all_data.append({
                'film': film,
                'platforms': platforms,
            })

        html = render_template('export.html', all_data=all_data, now=datetime.utcnow())
        return Response(
            html,
            mimetype='text/html',
            headers={'Content-Disposition': 'attachment; filename="film_price_tracker.html"'}
        )
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


@main.route('/upload')
def upload():
    return render_template('upload.html')


@main.route('/api/ocr', methods=['POST'])
def api_ocr():
    if not ocr_engine:
        return jsonify({'error': 'OCR 引擎未安装，请运行: pip install rapidocr-onnxruntime'}), 500

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': '请提供图片数据'}), 400

    image_data = data['image']
    if ',' in image_data:
        image_data = image_data.split(',', 1)[1]

    try:
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        img_path = Path('temp_upload.png')
        img.save(img_path)
        result, _ = ocr_engine(str(img_path))
        img_path.unlink(missing_ok=True)
    except Exception as e:
        return jsonify({'error': f'图片处理失败: {str(e)}'}), 400

    items = parse_ocr_lines(result)
    return jsonify({'items': items, 'raw_lines': [item[1] for item in (result or []) if item]})


@main.route('/api/save', methods=['POST'])
def api_save():
    data = request.get_json()
    if not data or 'items' not in data:
        return jsonify({'error': '没有要保存的数据'}), 400

    items = data['items']
    session = SessionLocal()
    saved = 0
    try:
        for item in items:
            title = item.get('title', '').strip()
            price = item.get('price', 0)
            store_name = item.get('store', '未知店铺')
            url = item.get('url', '')

            if not title or price <= 0:
                continue

            brand, model, iso, film_format = parse_product_name(title)

            film = session.query(Film).filter_by(brand=brand, model=model).first()
            if not film:
                film = Film(brand=brand, model=title[:100], iso=iso, format=film_format)
                session.add(film)
                session.commit()

            ph = PriceHistory(film_id=film.id, platform=store_name, price=price, url=url)
            session.add(ph)
            session.commit()
            saved += 1
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'保存失败: {str(e)}'}), 500
    finally:
        session.close()

    return jsonify({'saved': saved})
