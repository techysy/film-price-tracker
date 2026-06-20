from spiders.base_spider import BaseFilmSpider
import scrapy
import re


class TaobaoSpider(BaseFilmSpider):
    name = 'taobao'
    allowed_domains = ['taobao.com']
    start_urls = [
        'https://s.taobao.com/search?q=胶卷&bcoffset=0',
        'https://s.taobao.com/search?q=柯达胶卷&bcoffset=0',
        'https://s.taobao.com/search?q=富士胶卷&bcoffset=0',
        'https://s.taobao.com/search?q=伊尔福胶卷&bcoffset=0',
    ]

    def parse(self, response):
        products = response.css('.items .item')

        for product in products:
            name = product.css('.title a::text').get()
            if not name:
                name = product.css('.title::text').get()
            if not name:
                continue

            price = product.css('.price strong::text').get()
            if not price:
                continue

            url = product.css('.title a::attr(href)').get()
            if url and not url.startswith('http'):
                url = 'https:' + url if url.startswith('//') else 'https://www.taobao.com' + url

            brand, model, iso, film_format = self.parse_product_name(name.strip())

            if brand:
                price = float(re.sub('[^0-9.]', '', price))
                self.save_price(
                    brand=brand,
                    model=model,
                    platform='淘宝',
                    price=price,
                    url=url,
                    iso=iso,
                    film_format=film_format
                )

    def parse_product_name(self, name):
        brand = None
        model = name
        iso = None
        film_format = None

        for b in self.film_brands:
            if b in name:
                brand = b
                model = name.replace(b, '').strip()
                break

        iso_match = re.search(r'ISO(\d+)', name, re.IGNORECASE)
        if not iso_match:
            iso_match = re.search(r'(\d+)度', name)
        if iso_match:
            iso = int(iso_match.group(1))

        for fmt in self.film_formats:
            if fmt in name:
                film_format = fmt
                break
        if '135' in name:
            film_format = '35mm'

        return brand, model, iso, film_format
