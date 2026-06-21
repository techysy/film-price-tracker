import io
import re
import base64
import tempfile
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

FILM_BRANDS = {
    'kodak': '柯达', '柯达': '柯达',
    'fujifilm': '富士', '富士': '富士', 'fuji': '富士',
    'ilford': '伊尔福', '伊尔福': '伊尔福',
    'agfa': '爱克发', '爱克发': '爱克发',
    'lomography': '乐魔', '乐魔': '乐魔',
    'cinestill': 'Cinestill', 'fomapan': 'Fomapan',
    'wolfen': 'Wolfen', 'orwo': 'ORWO',
    'flic': 'Flic Film', 'chrome': '反转',
}
INSTANT_FORMATS = {
    'instax mini': '拍立得Mini', 'mini': '拍立得Mini',
    'instax sq': '拍立得SQ', 'sq': '拍立得SQ',
    'instax wide': '拍立得Wide', 'wide': '拍立得Wide',
    'instax': '拍立得',
    'polaroid': '宝丽来', '宝丽来': '宝丽来',
    'igo': '宝丽来',
}
FILM_TYPES = {
    '彩负': '彩负', '彩色负片': '彩负', 'color': '彩负', 'colorplus': '彩负',
    'gold': '彩负', 'ultra': '彩负', 'max': '彩负',
    '黑白': '黑白', 'b&w': '黑白', 'bw': '黑白', 'pan': '黑白',
    'hp5': '黑白', 'delta': '黑白', 'fomapan': '黑白',
    '反转': '反转', 'slide': '反转', 'reversal': '反转',
    'chrome': '反转', 'provia': '反转', 'velvia': '反转', 'ektar': '反转',
    '彩负电影卷': '电影卷', '电影卷': '电影卷', 'vision': '电影卷', '5207': '电影卷', '5219': '电影卷',
    '黑白电影卷': '黑白电影卷',
    '一次成像': '一次成像', '拍立得': '一次成像', '宝丽来': '一次成像',
    'phoenix': '彩负',
}
UNKNOWN_BRAND = '其他'


def parse_product_name(name):
    name_lower = name.lower()
    brand = None
    model = name
    iso = None
    film_format = None
    film_type = None
    expiry = None

    for key, val in FILM_BRANDS.items():
        if key in name_lower:
            brand = val
            break

    iso_match = re.search(r'ISO[\s]*(\d+)', name, re.IGNORECASE)
    if not iso_match:
        iso_match = re.search(r'(\d+)度', name)
    if not iso_match:
        iso_match = re.search(r'(?:金|GOLD|Max|Ultra|Plus|Color|CP|Pan|HP|Delta|Provia|Velvia|Ektar|Cine|Still)[\s]*(\d{3,4})', name, re.IGNORECASE)
    if not iso_match:
        iso_match = re.search(r'(\d{3,4})\s*(?:T|F|C|D|Plus|Pro)[\b\s]', name, re.IGNORECASE)
    if not iso_match:
        iso_match = re.search(r'(\d{3,4})(?:\s*(?:张| exposures?| exp))', name, re.IGNORECASE)
    if iso_match:
        iso_val = int(iso_match.group(1))
        if 25 <= iso_val <= 6400:
            iso = iso_val

    for kw, fmt in sorted(INSTANT_FORMATS.items(), key=lambda x: -len(x[0])):
        if kw in name_lower:
            film_format = fmt
            break
    if not film_format:
        if '135' in name or '35mm' in name_lower:
            film_format = '35mm'
        elif '120' in name:
            film_format = '120'
        elif '220' in name:
            film_format = '220'
        elif '4x5' in name or '4x4' in name:
            film_format = '大画幅'
        elif '5x7' in name or '8x10' in name:
            film_format = '大画幅'

    if film_format and ('拍立得' in film_format or '宝丽来' in film_format):
        if '黑白' in name or 'b&w' in name_lower:
            film_type = '黑白一次成像'
        elif '彩色' in name or 'color' in name_lower:
            film_type = '彩色一次成像'
        else:
            film_type = '一次成像'
    else:
        for kw, ft in sorted(FILM_TYPES.items(), key=lambda x: -len(x[0])):
            if kw in name_lower:
                film_type = ft
                break

    exp_match = re.search(r'(\d{2})[年.\-/](\d{1,2})[月]?', name)
    if exp_match:
        y = int(exp_match.group(1))
        m = int(exp_match.group(2))
        if 20 <= y <= 35:
            y += 2000
        if 1 <= m <= 12:
            expiry = f'{y}-{m:02d}'

    return {
        'brand': brand or UNKNOWN_BRAND,
        'model': name[:100],
        'iso': iso,
        'format': film_format,
        'film_type': film_type,
        'expiry': expiry,
    }


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


@main.route('/films')
def films():
    session = SessionLocal()
    try:
        film_list = session.query(Film).order_by(Film.brand, Film.model).all()
        return render_template('films.html', films=film_list)
    finally:
        session.close()


@main.route('/films/add', methods=['POST'])
def film_add():
    brand = request.form.get('brand', '').strip()
    model = request.form.get('model', '').strip()
    film_format = request.form.get('format', '').strip() or None
    film_type = request.form.get('film_type', '').strip() or None
    iso = request.form.get('iso', '').strip()
    iso = int(iso) if iso and iso.isdigit() else None
    expiry = request.form.get('expiry', '').strip() or None
    if not brand or not model:
        flash('品牌和型号不能为空', 'danger')
        return redirect(url_for('main.films'))
    session = SessionLocal()
    try:
        film = Film(brand=brand, model=model, format=film_format,
                    film_type=film_type, iso=iso, expiry=expiry)
        session.add(film)
        session.commit()
        flash(f'胶片 "{brand} {model}" 添加成功', 'success')
    except Exception as e:
        session.rollback()
        flash(f'添加失败: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('main.films'))


@main.route('/films/edit/<int:film_id>', methods=['POST'])
def film_edit(film_id):
    session = SessionLocal()
    try:
        film = session.query(Film).get(film_id)
        if not film:
            flash('胶片不存在', 'danger')
            return redirect(url_for('main.films'))
        brand = request.form.get('brand', '').strip()
        model = request.form.get('model', '').strip()
        film_format = request.form.get('format', '').strip() or None
        film_type = request.form.get('film_type', '').strip() or None
        iso = request.form.get('iso', '').strip()
        iso = int(iso) if iso and iso.isdigit() else None
        expiry = request.form.get('expiry', '').strip() or None
        if brand:
            film.brand = brand
        if model:
            film.model = model
        film.format = film_format
        film.film_type = film_type
        film.iso = iso
        film.expiry = expiry
        session.commit()
        flash(f'胶片 "{film.brand} {film.model}" 已更新', 'success')
    except Exception as e:
        session.rollback()
        flash(f'更新失败: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('main.films'))


@main.route('/films/delete/<int:film_id>', methods=['POST'])
def film_delete(film_id):
    session = SessionLocal()
    try:
        film = session.query(Film).get(film_id)
        if not film:
            flash('胶片不存在', 'danger')
            return redirect(url_for('main.films'))
        name = f'{film.brand} {film.model}'
        session.query(PriceHistory).filter_by(film_id=film.id).delete()
        session.delete(film)
        session.commit()
        flash(f'胶片 "{name}" 已删除', 'success')
    except Exception as e:
        session.rollback()
        flash(f'删除失败: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('main.films'))


@main.route('/api/films/list')
def api_films_list():
    session = SessionLocal()
    try:
        films = session.query(Film).all()
        return jsonify([{
            'id': f.id, 'brand': f.brand, 'model': f.model,
            'format': f.format, 'film_type': f.film_type,
            'iso': f.iso, 'expiry': f.expiry
        } for f in films])
    finally:
        session.close()


@main.route('/api/films/match', methods=['POST'])
def api_film_match():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'film_id': None})

    title = data['title'].lower()
    session = SessionLocal()
    try:
        films = session.query(Film).all()
        best = None
        best_score = 0
        for film in films:
            score = 0
            name = f'{film.brand} {film.model}'.lower()
            brand_l = (film.brand or '').lower()
            if brand_l and brand_l in title:
                score += 10
            if film.iso:
                iso_str = str(film.iso)
                if iso_str in title:
                    score += 5
            if film.format:
                fmt = film.format.lower()
                if '35mm' in fmt and ('135' in title or '35mm' in title):
                    score += 5
                elif '120' in fmt and '120' in title:
                    score += 5
                elif fmt in title:
                    score += 5
            if film.film_type:
                ft = film.film_type.lower()
                if '彩负' in ft and ('彩负' in title or 'color' in title or '彩色负片' in title):
                    score += 3
                elif '黑白' in ft and ('黑白' in title or 'b&w' in title):
                    score += 3
                elif '反转' in ft and ('反转' in title or 'slide' in title):
                    score += 3
                elif '电影卷' in ft and ('电影卷' in title or 'vision' in title):
                    score += 3
                elif '一次成像' in ft and ('一次成像' in title or 'instax' in title or 'polaroid' in title):
                    score += 3
            if score > best_score:
                best_score = score
                best = film
        if best and best_score >= 5:
            return jsonify({'film_id': best.id, 'brand': best.brand, 'model': best.model, 'score': best_score})
        return jsonify({'film_id': None})
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


@main.route('/api/stores/import', methods=['POST'])
def api_stores_import():
    data = request.get_json()
    if not data or 'stores' not in data:
        return jsonify({'error': '没有要导入的数据'}), 400

    stores = data['stores']
    session = SessionLocal()
    imported = 0
    try:
        for item in stores:
            name = item.get('name', '').strip()
            url = item.get('url', '').strip()
            if not name or not url:
                continue
            existing = session.query(TaobaoStore).filter_by(url=url).first()
            if existing:
                continue
            session.add(TaobaoStore(name=name, url=url))
            imported += 1
        session.commit()
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'导入失败: {str(e)}'}), 500
    finally:
        session.close()

    return jsonify({'imported': imported})


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
        if name:
            store.name = name
        if url:
            store.url = url
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
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        result, _ = ocr_engine(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        return jsonify({'error': f'图片处理失败: {str(e)}'}), 400

    items = parse_ocr_lines(result)
    for item in items:
        info = parse_product_name(item.get('title', ''))
        item['brand'] = info['brand']
        item['format'] = info['format']
        item['film_type'] = info['film_type']
        item['iso'] = info['iso']
        item['expiry'] = info['expiry']
    return jsonify({'items': items, 'raw_lines': [item[1] for item in (result or []) if item]})


@main.route('/api/save', methods=['POST'])
def api_save():
    data = request.get_json()
    if not data or 'items' not in data:
        return jsonify({'error': '没有要保存的数据'}), 400

    items = data['items']
    session = SessionLocal()
    saved = 0
    skipped = 0
    try:
        all_films = session.query(Film).all()
        for item in items:
            title = item.get('title', '').strip()
            price = item.get('price', 0)
            store_name = item.get('store', '未知店铺')
            url = item.get('url', '')
            force_film_id = item.get('film_id')

            if not title or price <= 0:
                continue

            film = None
            if force_film_id:
                film = session.query(Film).get(force_film_id)
            else:
                film = _match_film(title, all_films)

            if not film:
                skipped += 1
                continue

            ph = PriceHistory(film_id=film.id, platform=store_name, price=price, url=url)
            session.add(ph)
            session.commit()
            saved += 1
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'保存失败: {str(e)}'}), 500
    finally:
        session.close()

    return jsonify({'saved': saved, 'skipped': skipped})


def _match_film(title, all_films):
    title_lower = title.lower()
    best = None
    best_score = 0
    for film in all_films:
        score = 0
        brand_l = (film.brand or '').lower()
        if brand_l and brand_l in title_lower:
            score += 10
        if film.iso and str(film.iso) in title_lower:
            score += 5
        if film.format:
            fmt = film.format.lower()
            if '35mm' in fmt and ('135' in title_lower or '35mm' in title_lower):
                score += 5
            elif '120' in fmt and '120' in title_lower:
                score += 5
            elif fmt in title_lower:
                score += 5
        if film.film_type:
            ft = film.film_type.lower()
            if '彩负' in ft and ('彩负' in title_lower or 'color' in title_lower or '彩色负片' in title_lower):
                score += 3
            elif '黑白' in ft and ('黑白' in title_lower or 'b&w' in title_lower):
                score += 3
            elif '反转' in ft and ('反转' in title_lower or 'slide' in title_lower):
                score += 3
            elif '电影卷' in ft and ('电影卷' in title_lower or 'vision' in title_lower):
                score += 3
            elif '一次成像' in ft and ('一次成像' in title_lower or 'instax' in title_lower or 'polaroid' in title_lower):
                score += 3
        if score > best_score:
            best_score = score
            best = film
    if best and best_score >= 5:
        return best
    return None

    return jsonify({'saved': saved})
