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

class DeliveryZone(Base):
    __tablename__ = "delivery_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    base_price = Column(Integer, nullable=False)
    bag_price = Column(Integer, default=700)
    coefficient = Column(Float, default=1.0)
    note = Column(Text)

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=False)

class Microdistrict(Base):
    __tablename__ = "microdistricts"
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"))
    name = Column(String(200))
    slang_name = Column(String(200))

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100))
    user_message = Column(Text)
    bot_response = Column(Text)
    detected_intent = Column(String(50))
    confidence = Column(Float)
    user_feedback = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class TrainingExample(Base):
    __tablename__ = "training_examples"
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    intent = Column(String(50))
    source = Column(String(50), default="manual")
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")