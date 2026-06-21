from spiders.base_spider import BaseFilmSpider
from models.film import TaobaoStore
import scrapy
import re


class TaobaoSpider(BaseFilmSpider):
    name = 'taobao'
    allowed_domains = ['taobao.com']

    def start_requests(self):
        stores = self.session.query(TaobaoStore).filter_by(enabled=True).all()
        if not stores:
            self.logger.warning("没有启用的淘宝店铺，跳过爬取")
            return
        for store in stores:
            self.logger.info(f"开始爬取店铺: {store.name} ({store.url})")
            yield scrapy.Request(
                url=store.url,
                callback=self.parse_store,
                meta={'store_name': store.name},
                dont_filter=True
            )

    def parse_store(self, response):
        store_name = response.meta['store_name']
        products = response.css('.item, .item-card, [data-item], .shop-item, .product-item, .Card--doubleCardWrapper--L2XFE73')
        if not products:
            products = response.css('a[href*="item.taobao.com"], a[href*="detail.tmall.com"]').xpath('ancestor::div[1]')

        for product in products:
            name = (
                product.css('.title a::text').get()
                or product.css('.title::text').get()
                or product.css('.item-title::text').get()
                or product.css('[class*="title"]::text').get()
                or product.css('a::attr(title)').get()
            )
            if not name or not name.strip():
                continue

            price = (
                product.css('.price strong::text').get()
                or product.css('.price::text').get()
                or product.css('[class*="price"]::text').get()
            )
            if not price:
                continue

            url = (
                product.css('.title a::attr(href)').get()
                or product.css('a::attr(href)').get()
            )
            if url and not url.startswith('http'):
                url = 'https:' + url if url.startswith('//') else 'https://www.taobao.com' + url

            brand, model, iso, film_format = self.parse_product_name(name.strip())

            if brand:
                try:
                    price = float(re.sub('[^0-9.]', '', price))
                except (ValueError, TypeError):
                    continue
                if price <= 0:
                    continue
                self.save_price(
                    brand=brand,
                    model=model,
                    platform=store_name,
                    price=price,
                    url=url,
                    iso=iso,
                    film_format=film_format
                )

        next_page = response.css('.next::attr(href), a[href*="page="]::attr(href)').get()
        if next_page:
            if not next_page.startswith('http'):
                next_page = response.urljoin(next_page)
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_store,
                meta={'store_name': store_name},
                dont_filter=True
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

        if not film_format:
            for kw, fmt in self.instant_keywords.items():
                if kw in name:
                    film_format = fmt
                    break

        return brand, model, iso, film_format
