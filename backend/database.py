from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://postgres:password@localhost:5434/nerud_bot"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True)
    key_name = Column(String(100), unique=True)
    name = Column(String(200))
    price_per_ton = Column(Float)
    price_per_bag = Column(Float)
    bag_weight = Column(Integer)
    unit = Column(String(50))
    description = Column(Text)
    type = Column(String(20), default="ton")

class FreeDolomiteMicrodistrict(Base):
    __tablename__ = "free_dolomite_microdistricts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slang_name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

class DeliveryZone(Base):
    __tablename__ = "delivery_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    base_price = Column(Integer, nullable=False)
    bag_price = Column(Integer, default=700)
    coefficient = Column(Float, default=1.0)
    note = Column(Text)

class Microdistrict(Base):
    __tablename__ = "microdistricts"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"))
    name = Column(String(200))
    slang_name = Column(String(200))

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")