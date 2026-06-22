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
    film_type = Column(String(30))
    expiry = Column(String(10))
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    price_histories = relationship('PriceHistory', back_populates='film')


class PriceHistory(Base):
    __tablename__ = 'price_histories'

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'), nullable=False)
    platform = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    url = Column(String(255))
    rolls_per_pack = Column(Integer, default=1)
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

    import sqlite3
    from config import config as app_config_module
    db_path = app_config_module['default'].SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    TABLE_COLUMNS = {
        'films': {
            'brand': 'VARCHAR(50) NOT NULL DEFAULT \'其他\'',
            'model': 'VARCHAR(100) NOT NULL DEFAULT \'\'',
            'iso': 'INTEGER',
            'format': 'VARCHAR(20)',
            'film_type': 'VARCHAR(30)',
            'expiry': 'VARCHAR(10)',
            'description': 'VARCHAR(255)',
            'created_at': 'DATETIME',
        },
        'price_histories': {
            'film_id': 'INTEGER NOT NULL',
            'platform': 'VARCHAR(50) NOT NULL DEFAULT \'\'',
            'price': 'REAL NOT NULL DEFAULT 0',
            'url': 'VARCHAR(255)',
            'rolls_per_pack': 'INTEGER DEFAULT 1',
            'timestamp': 'DATETIME',
        },
        'taobao_stores': {
            'name': 'VARCHAR(100) NOT NULL DEFAULT \'\'',
            'url': 'VARCHAR(500) NOT NULL DEFAULT \'\'',
            'created_at': 'DATETIME',
        },
    }

    for table, columns in TABLE_COLUMNS.items():
        cursor.execute(f'PRAGMA table_info({table})')
        existing = {row[1] for row in cursor.fetchall()}
        for col_name, col_def in columns.items():
            if col_name not in existing:
                try:
                    cursor.execute(f'ALTER TABLE {table} ADD COLUMN {col_name} {col_def}')
                except sqlite3.OperationalError:
                    pass

    conn.commit()
    conn.close()
