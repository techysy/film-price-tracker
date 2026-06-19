from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class Film(Base):
    __tablename__ = 'films'
    
    id = Column(Integer, primary_key=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    iso = Column(Integer)
    format = Column(String(20))  # 35mm, 120, etc.
    description = Column(String(255))
    
    # 关系
    price_histories = relationship('PriceHistory', back_populates='film')

class PriceHistory(Base):
    __tablename__ = 'price_histories'
    
    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'), nullable=False)
    platform = Column(String(50), nullable=False)  # 京东、淘宝、亚马逊等
    price = Column(Float, nullable=False)
    url = Column(String(255))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关系
    film = relationship('Film', back_populates='price_histories')

# 数据库连接
engine = create_engine('sqlite:///film_prices.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
