import scrapy
from ..models.film import session, Film, PriceHistory

class BaseFilmSpider(scrapy.Spider):
    """基础爬虫类，提供通用功能"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.film_brands = [
            'kodak', '柯达',
            'fujifilm', '富士',
            'ilford', '伊尔福',
            'agfa', '爱克发',
            'lomography', '乐魔'
        ]
        self.film_formats = ['35mm', '120', '135']
    
    def save_price(self, brand, model, platform, price, url, iso=None, film_format=None):
        """保存价格数据到数据库"""
        # 查找或创建胶卷记录
        film = session.query(Film).filter_by(brand=brand, model=model).first()
        if not film:
            film = Film(
                brand=brand,
                model=model,
                iso=iso,
                format=film_format
            )
            session.add(film)
            session.commit()
        
        # 创建价格历史记录
        price_history = PriceHistory(
            film_id=film.id,
            platform=platform,
            price=price,
            url=url
        )
        session.add(price_history)
        session.commit()
        
        self.logger.info(f"Saved price for {brand} {model} on {platform}: ¥{price}")
