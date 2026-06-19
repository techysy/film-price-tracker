from .base_spider import BaseFilmSpider
import scrapy
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
        # 提取商品列表
        products = response.css('.gl-item')
        
        for product in products:
            # 提取商品名称
            name = product.css('.p-name em::text').get()
            if not name:
                continue
            
            # 提取价格
            price = product.css('.p-price .price::text').get()
            if not price:
                continue
            
            # 提取商品链接
            url = product.css('.p-name a::attr(href)').get()
            if url and not url.startswith('http'):
                url = 'https://jd.com' + url
            
            # 解析品牌和型号
            brand, model, iso, film_format = self.parse_product_name(name)
            
            if brand:
                # 清理价格
                price = float(re.sub('[^0-9.]', '', price))
                
                # 保存价格
                self.save_price(
                    brand=brand,
                    model=model,
                    platform='京东',
                    price=price,
                    url=url,
                    iso=iso,
                    film_format=film_format
                )
        
        # 翻页
        next_page = response.css('.pn-next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse
            )
    
    def parse_product_name(self, name):
        """解析商品名称，提取品牌、型号、ISO和格式"""
        brand = None
        model = name
        iso = None
        film_format = None
        
        # 识别品牌
        for b in self.film_brands:
            if b in name:
                brand = b
                model = name.replace(b, '').strip()
                break
        
        # 识别ISO
        iso_match = re.search(r'ISO(\d+)', name, re.IGNORECASE)
        if not iso_match:
            iso_match = re.search(r'(\d+)度', name)
        if iso_match:
            iso = int(iso_match.group(1))
        
        # 识别格式
        for fmt in self.film_formats:
            if fmt in name:
                film_format = fmt
                break
        if '135' in name:
            film_format = '35mm'
        
        return brand, model, iso, film_format
