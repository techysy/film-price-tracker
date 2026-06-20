from spiders.base_spider import BaseFilmSpider
import scrapy
import re
import json


class TaobaoSpider(BaseFilmSpider):
    name = 'taobao'
    start_urls = [
        'https://h5api.m.taobao.com/h5/mtop.taobao.searchapi.search/1.0/?jsv=2.7.0&appKey=12574478&t=1718856000&sign=xxx&api=mtop.taobao.searchapi.search&v=1.0&dataType=json&timeout=20000&AntiCreep=true&type=jsonp&callback=mtopjsonp1&data=%7B%22query%22%3A%22%E8%83%B6%E5%8D%B7%22%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D',
        'https://h5api.m.taobao.com/h5/mtop.taobao.searchapi.search/1.0/?jsv=2.7.0&appKey=12574478&t=1718856000&sign=xxx&api=mtop.taobao.searchapi.search&v=1.0&dataType=json&timeout=20000&AntiCreep=true&type=jsonp&callback=mtopjsonp1&data=%7B%22query%22%3A%22%E6%9F%AF%E8%BE%BE%E8%83%B6%E5%8D%B7%22%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D',
        'https://h5api.m.taobao.com/h5/mtop.taobao.searchapi.search/1.0/?jsv=2.7.0&appKey=12574478&t=1718856000&sign=xxx&api=mtop.taobao.searchapi.search&v=1.0&dataType=json&timeout=20000&AntiCreep=true&type=jsonp&callback=mtopjsonp1&data=%7B%22query%22%3A%22%E5%AF%8C%E5%A3%AB%E8%83%B6%E5%8D%B7%22%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D',
        'https://h5api.m.taobao.com/h5/mtop.taobao.searchapi.search/1.0/?jsv=2.7.0&appKey=12574478&t=1718856000&sign=xxx&api=mtop.taobao.searchapi.search&v=1.0&dataType=json&timeout=20000&AntiCreep=true&type=jsonp&callback=mtopjsonp1&data=%7B%22query%22%3A%22%E4%BC%8A%E5%B0%94%E7%A6%8F%E8%83%B6%E5%8D%B7%22%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D'
    ]

    def parse(self, response):
        try:
            json_str = re.search(r'mtopjsonp1\((.*?)\)', response.text)
            if not json_str:
                return
            data = json.loads(json_str.group(1))
            if data.get('ret') and 'SUCCESS' not in data['ret'][0]:
                return
            result = data.get('data', {})
            items = result.get('resultList', [])
            for item in items:
                if isinstance(item, dict):
                    name = item.get('title', '') or item.get('rawTitle', '')
                    if not name:
                        continue
                    price = item.get('price', '')
                    if not price:
                        continue
                    url = item.get('itemUrl', '') or f'https://item.taobao.com/item.htm?id={item.get("itemId", "")}'
                    if url and not url.startswith('http'):
                        url = 'https:' + url
                    brand, model, iso, film_format = self.parse_product_name(name)
                    if brand:
                        price = float(re.sub('[^0-9.]', '', str(price)))
                        self.save_price(brand=brand, model=model, platform='淘宝', price=price, url=url, iso=iso, film_format=film_format)
        except Exception as e:
            self.logger.error(f'Error parsing taobao API: {e}')
