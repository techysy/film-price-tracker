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

OCR_CONFIG_PATH = Path(__file__).parent / 'ocr_config.json'

_default_ocr_config = {
    "text_score": 0.5,
    "use_det": True,
    "use_cls": True,
    "use_rec": True,
    "min_height": 30,
    "max_side_len": 2000,
    "ignore_top": 0,
    "ignore_bottom": 0,
}


def _load_ocr_config():
    if OCR_CONFIG_PATH.exists():
        try:
            with open(OCR_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return _default_ocr_config.copy()


def _build_ocr_engine(config=None):
    if config is None:
        config = _load_ocr_config()
    try:
        from rapidocr_onnxruntime import RapidOCR
        kwargs = {}
        if 'text_score' in config:
            kwargs['text_score'] = config['text_score']
        if 'use_det' in config:
            kwargs['use_det'] = config['use_det']
        if 'use_cls' in config:
            kwargs['use_cls'] = config['use_cls']
        if 'use_rec' in config:
            kwargs['use_rec'] = config['use_rec']
        return RapidOCR(**kwargs)
    except ImportError:
        return None


ocr_engine = _build_ocr_engine()

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

    order_info = detect_order(lines)
    if order_info:
        return parse_order_lines(lines, order_info)

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
                 'phoenix', 'instax', 'polaroid', '宝丽来', '拍立得', '测试卷', '片头卷',
                 'c200', 'c400', 'gold200', 'ultramax', 'ek100', 'ek100ii',
                 'pro400h', 'superia', 'velvia50', 'velvia100', 'provia100f',
                 '100度', '200度', '400度', '800度', '1600度',
                 '负片胶', '彩色负', '彩色胶'])
            if has_film_keyword:
                pending_title = line

    return results


def detect_order(lines):
    order_date = ''
    order_no = ''
    order_store = ''
    for line in lines:
        line = line.strip()
        date_match = re.match(r'^(\d{4}[-/]\d{1,2}[-/]\d{1,2})', line)
        if date_match:
            order_date = date_match.group(1)
        no_match = re.search(r'订单号[：:\s]*(\d+)', line)
        if no_match:
            order_no = no_match.group(1)
        if not order_store and re.search(r'(淘宝|天猫|京东)\s+(.+)', line):
            store_match = re.search(r'(淘宝|天猫|京东)\s+(.+)', line)
            order_store = store_match.group(2).strip()
        if not order_store and re.search(r'(irohas|camera|store|shop)', line.lower()):
            if len(line) < 30:
                order_store = line

    if not order_date and not order_no:
        return None
    return {
        'date': order_date,
        'order_no': order_no,
        'store': order_store or '未知店铺',
    }


def parse_order_lines(lines, order_info):
    results = []
    pending_title = ''
    pending_price = 0
    pending_qty = 1

    SKIP_PATTERNS = ['88VIP', '退货', '退款', '删除', '移入收藏', '商品规格', '含税',
                     '立即购买', '已选', '库存', '配送', '服务', '保障', '评价',
                     '申请售后', '再买一单', '加入购物车', '手机订单', '订单详情',
                     '交易成功', '7天无理由退货', '实付款', '含运费', '手机订单',
                     '7天无理由']

    FILM_KEYWORDS = ['胶卷', '胶片', 'kodak', '柯达', 'fuji', '富士', 'ilford', '伊尔福',
             '120', '135', '35mm', '负片', '反转', '彩负', '黑白', 'iso',
             'portra', 'gold', 'ultra', 'ektar', 'provia', 'velvia', 'cinestill',
             'fomapan', 'hp5', 'delta', 'pan400', 'colorplus', 'lomo', 'wolfen',
             'orwo', 'agfa', 'cn400', 'cn800', 'nc400', '5207', '5219', '5203', '5222',
             'phoenix', 'instax', 'polaroid', '宝丽来', '拍立得', '测试卷', '片头卷',
             'c200', 'c400', 'gold200', 'ultramax', 'ek100', 'ek100ii',
             'pro400h', 'superia', 'velvia50', 'velvia100', 'provia100f',
             '100度', '200度', '400度', '800度', '1600度',
             '负片胶', '彩色负', '彩色胶', 'color']

    def flush():
        nonlocal pending_title, pending_price, pending_qty
        if pending_title and pending_price > 0:
            results.append({
                'store': order_info['store'],
                'title': pending_title,
                'price': pending_price * pending_qty,
                'quantity': pending_qty,
                'unit_price': pending_price,
                'order_date': order_info['date'],
                'order_no': order_info['order_no'],
            })
        pending_title = ''
        pending_price = 0
        pending_qty = 1

    def extract_inline_qty(text):
        m = re.search(r'[x×]\s*(\d+)\b', text)
        if m:
            return int(m.group(1))
        return 1

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if any(kw in line for kw in SKIP_PATTERNS):
            continue
        if re.match(r'^[\d\s\-/]+$', line):
            continue
        if line in ('淘宝', '天猫', '京东', '淘宝网', '订单详情'):
            continue

        qty_match = re.match(r'^[x×]\s*(\d+)$', line)
        if qty_match:
            pending_qty = int(qty_match.group(1))
            flush()
            continue

        price_match = re.search(r'[¥￥]\s*(\d+\.?\d*)', line)
        if price_match:
            price = float(price_match.group(1))
            if price <= 0:
                continue

            rest_before = line[:price_match.start()].strip()
            rest_after = line[price_match.end():].strip()

            inline_qty = extract_inline_qty(rest_after)

            if rest_before and len(rest_before) > 2:
                flush()
                pending_title = rest_before
                pending_price = price
                pending_qty = inline_qty
                flush()
            elif pending_title:
                pending_price = price
                pending_qty = inline_qty
                flush()
            else:
                has_film_kw = any(kw in line.lower() for kw in FILM_KEYWORDS)
                if has_film_kw:
                    pending_title = line
                    pending_price = price
                    pending_qty = inline_qty
                    flush()
            continue

        has_film_keyword = any(kw in line.lower() for kw in FILM_KEYWORDS)
        if has_film_keyword:
            if pending_title and pending_price > 0:
                flush()
            pending_title = line

    flush()
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
            rolls = ph.rolls_per_pack or 1
            per_roll_price = ph.price / rolls if rolls > 1 else ph.price
            platforms[ph.platform].append({
                'x': ph.timestamp.strftime('%Y-%m-%d %H:%M'),
                'y': round(per_roll_price, 2)
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
                'id': ph.id,
                'timestamp': ph.timestamp.isoformat(),
                'price': ph.price,
                'platform': ph.platform,
                'url': ph.url,
                'rolls_per_pack': ph.rolls_per_pack or 1,
            }
            for ph in price_histories
        ]

        return jsonify(data)
    finally:
        session.close()


@main.route('/api/price_history/delete/<int:ph_id>', methods=['POST'])
def api_price_history_delete(ph_id):
    session = SessionLocal()
    try:
        ph = session.query(PriceHistory).get(ph_id)
        if not ph:
            return jsonify({'error': '记录不存在'}), 404
        film_id = ph.film_id
        session.delete(ph)
        session.commit()
        return jsonify({'ok': True, 'film_id': film_id})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@main.route('/ocr-admin')
def ocr_admin():
    config = _load_ocr_config()
    engine_status = 'running' if ocr_engine else 'not_installed'
    return render_template('ocr_admin.html', config=config, engine_status=engine_status)


@main.route('/api/ocr-config', methods=['GET'])
def api_ocr_config_get():
    return jsonify(_load_ocr_config())


@main.route('/api/ocr-config', methods=['POST'])
def api_ocr_config_apply():
    global ocr_engine
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供配置数据'}), 400

    config = _load_ocr_config()
    config.update(data)

    new_engine = _build_ocr_engine(config)
    if new_engine is None:
        return jsonify({'error': 'OCR 引擎未安装，请运行: pip install rapidocr-onnxruntime'}), 500

    ocr_engine = new_engine
    return jsonify({'ok': True, 'config': config})


@main.route('/api/ocr-config/save', methods=['POST'])
def api_ocr_config_save():
    global ocr_engine
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供配置数据'}), 400

    config = _load_ocr_config()
    config.update(data)

    try:
        with open(OCR_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({'error': f'保存失败: {str(e)}'}), 500

    new_engine = _build_ocr_engine(config)
    if new_engine is not None:
        ocr_engine = new_engine

    return jsonify({'ok': True, 'config': config})


@main.route('/api/ocr/model-info', methods=['GET'])
def api_ocr_model_info():
    if not ocr_engine:
        return jsonify({'error': 'OCR 引擎未安装'}), 500
    try:
        info = {
            'engine': 'RapidOCR (ONNX Runtime)',
            'config': _load_ocr_config(),
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/ocr/test', methods=['POST'])
def api_ocr_test():
    if not ocr_engine:
        return jsonify({'error': 'OCR 引擎未安装，请运行: pip install rapidocr-onnxruntime'}), 500

    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': '请提供图片数据'}), 400

    image_data = data['image']
    if ',' in image_data:
        image_data = image_data.split(',', 1)[1]

    config = _load_ocr_config()
    ignore_top = config.get('ignore_top', 0)
    ignore_bottom = config.get('ignore_bottom', 0)

    try:
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        img_height = img.height
        top_cutoff = int(img_height * ignore_top / 100) if ignore_top > 0 else 0
        bottom_cutoff = img_height - int(img_height * ignore_bottom / 100) if ignore_bottom > 0 else img_height

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        result, _ = ocr_engine(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        return jsonify({'error': f'图片处理失败: {str(e)}'}), 400

    filtered_result = []
    for item in (result or []):
        if item and len(item) >= 2:
            bbox = item[0]
            if bbox and len(bbox) >= 4:
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                if y_center < top_cutoff or y_center > bottom_cutoff:
                    continue
            filtered_result.append(item)

    raw_lines = [item[1] for item in filtered_result if item]
    return jsonify({'raw_lines': raw_lines, 'config': config})


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
                    'rolls_per_pack': ph.rolls_per_pack or 1,
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

    MODEL_KEYWORDS = {
        'colorplus': ['colorplus', '易拍', 'color plus'],
        'gold': ['gold', '金200', '金 200'],
        'ultramax': ['ultramax', '全能', 'ultra max'],
        'portra': ['portra', '波特拉'],
        'ektar': ['ektar', '依克塔'],
        'provia': ['provia', '普罗维亚'],
        'velvia': ['velvia', '维尔维亚'],
        'cinestill': ['cinestill', '电影卷'],
        'superia': ['superia', '世霸'],
        'c200': ['c200', 'c 200'],
        'c400': ['c400', 'c 400'],
        'hp5': ['hp5', 'hp 5'],
        'delta': ['delta'],
        'fomapan': ['fomapan'],
        'pan400': ['pan400', 'pan 400'],
        'ek100': ['ek100', 'ek 100'],
    }

    try:
        films = session.query(Film).all()
        best = None
        best_score = 0
        for film in films:
            score = 0
            brand_l = (film.brand or '').lower()
            model_l = (film.model or '').lower()
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
            if model_l:
                for key, aliases in MODEL_KEYWORDS.items():
                    if key in model_l:
                        for alias in aliases:
                            if alias in title:
                                score += 20
                                break
                        break
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

    config = _load_ocr_config()
    ignore_top = config.get('ignore_top', 0)
    ignore_bottom = config.get('ignore_bottom', 0)

    try:
        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes))
        img_height = img.height
        top_cutoff = int(img_height * ignore_top / 100) if ignore_top > 0 else 0
        bottom_cutoff = img_height - int(img_height * ignore_bottom / 100) if ignore_bottom > 0 else img_height

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        result, _ = ocr_engine(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        return jsonify({'error': f'图片处理失败: {str(e)}'}), 400

    filtered_result = []
    for item in (result or []):
        if item and len(item) >= 2:
            bbox = item[0]
            if bbox and len(bbox) >= 4:
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                if y_center < top_cutoff or y_center > bottom_cutoff:
                    continue
            filtered_result.append(item)

    items = parse_ocr_lines(filtered_result)
    for item in items:
        info = parse_product_name(item.get('title', ''))
        item['brand'] = info['brand']
        item['format'] = info['format']
        item['film_type'] = info['film_type']
        item['iso'] = info['iso']
        item['expiry'] = info['expiry']
    return jsonify({'items': items, 'raw_lines': [item[1] for item in filtered_result if item]})


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

            timestamp = None
            order_date = item.get('order_date', '')
            if order_date:
                try:
                    timestamp = datetime.strptime(order_date, '%Y-%m-%d')
                except ValueError:
                    pass

            rolls_per_pack = item.get('rolls_per_pack', 1) or 1

            ph = PriceHistory(film_id=film.id, platform=store_name, price=price, url=url, rolls_per_pack=rolls_per_pack)
            if timestamp:
                ph.timestamp = timestamp
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

    MODEL_KEYWORDS = {
        'colorplus': ['colorplus', '易拍', 'color plus'],
        'gold': ['gold', '金200', '金 200'],
        'ultramax': ['ultramax', '全能', 'ultra max'],
        'portra': ['portra', '波特拉'],
        'ektar': ['ektar', '依克塔'],
        'provia': ['provia', '普罗维亚'],
        'velvia': ['velvia', '维尔维亚'],
        'cinestill': ['cinestill', '电影卷'],
        'superia': ['superia', '世霸'],
        'c200': ['c200', 'c 200'],
        'c400': ['c400', 'c 400'],
        'hp5': ['hp5', 'hp 5'],
        'delta': ['delta'],
        'fomapan': ['fomapan'],
        'pan400': ['pan400', 'pan 400'],
        'ek100': ['ek100', 'ek 100'],
    }

    for film in all_films:
        score = 0
        brand_l = (film.brand or '').lower()
        model_l = (film.model or '').lower()
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
        if model_l:
            for key, aliases in MODEL_KEYWORDS.items():
                if key in model_l:
                    for alias in aliases:
                        if alias in title_lower:
                            score += 20
                            break
                    break
        if score > best_score:
            best_score = score
            best = film
    if best and best_score >= 5:
        return best
    return None

    return jsonify({'saved': saved})
