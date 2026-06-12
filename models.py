from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    asin = Column(String(20), unique=True, index=True)
    title = Column(String(500))
    price = Column(String(20))
    original_price = Column(String(20))
    discount_percent = Column(String(20))
    rating = Column(Float)
    rating_count = Column(Integer)
    delivery_date = Column(String(100))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    url = Column(String(500))