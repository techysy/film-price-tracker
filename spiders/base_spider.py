import scrapy
from models.film import SessionLocal, Film, PriceHistory


class BaseFilmSpider(scrapy.Spider):
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
        self.instant_keywords = {
            'instax': '拍立得', '拍立得': '拍立得',
            'polaroid': '宝丽来', '宝丽来': '宝丽来',
        }
        self.session = SessionLocal()

    def closed(self, reason):
        self.session.close()

    def save_price(self, brand, model, platform, price, url, iso=None, film_format=None):
        film = self.session.query(Film).filter_by(brand=brand, model=model).first()
        if not film:
            film = Film(
                brand=brand,
                model=model,
                iso=iso,
                format=film_format
            )
            self.session.add(film)
            self.session.commit()

        price_history = PriceHistory(
            film_id=film.id,
            platform=platform,
            price=price,
            url=url
        )
        self.session.add(price_history)
        self.session.commit()

        self.logger.info(f"Saved price for {brand} {model} on {platform}: ¥{price}")
