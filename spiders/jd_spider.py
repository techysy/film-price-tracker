import scrapy
from models.film import SessionLocal, Film, PriceHistory
from spiders.base_spider import BaseFilmSpider
import re


class JDSpider(BaseFilmSpider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = [
        'https://search.jd.com/Search?keyword=胶卷&enc=utf-8&wq=胶卷',
        'https://search.jd.com/Search?keyword=柯达胶卷&enc=utf-8&wq=柯达胶卷',
        'https://search.jd.com/Search?keyword=富士胶卷&enc=utf-8&wq=富士胶卷',
        'https://search.jd.com/Search?keyword=伊尔福胶卷&enc=utf-8&wq=伊尔福胶卷'
    ]

    def parse(self, response):
        products = response.css('.gl-item')

        for product in products:
            name = product.css('.p-name em::text').get()
            if not name:
                continue

            price = product.css('.p-price .price::text').get()
            if not price:
                continue

            url = product.css('.p-name a::attr(href)').get()
            if url and not url.startswith('http'):
                url = 'https://jd.com' + url

            brand, model, iso, film_format = self.parse_product_name(name)

            if brand:
                price = float(re.sub('[^0-9.]', '', price))
                self.save_price(
                    brand=brand,
                    model=model,
                    platform='京东',
                    price=price,
                    url=url,
                    iso=iso,
                    film_format=film_format
                )

        next_page = response.css('.pn-next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse
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
