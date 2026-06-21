from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
from config import config

Base = declarative_base()

app_config = config['default']
engine = create_engine(app_config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)


class Film(Base):
    __tablename__ = 'films'

    id = Column(Integer, primary_key=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    iso = Column(Integer)
    format = Column(String(20))
    description = Column(String(255))

    price_histories = relationship('PriceHistory', back_populates='film')


class PriceHistory(Base):
    __tablename__ = 'price_histories'

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'), nullable=False)
    platform = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    url = Column(String(255))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    film = relationship('Film', back_populates='price_histories')


class TaobaoStore(Base):
    __tablename__ = 'taobao_stores'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)
