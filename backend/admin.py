from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal, Material, DeliveryZone
import secrets

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

security = HTTPBasic()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class MaterialUpdate(BaseModel):
    price_per_ton: Optional[float] = None
    price_per_bag: Optional[float] = None

class MaterialCreate(BaseModel):
    key_name: str
    name: str
    price_per_ton: Optional[float] = None
    price_per_bag: Optional[float] = None
    bag_weight: Optional[int] = None
    unit: str
    description: str
    type: str

class ZoneUpdate(BaseModel):
    base_price: int

class ZoneCreate(BaseModel):
    key_name: str
    name: str
    base_price: int
    coefficient: float = 1.0
    note: Optional[str] = None

@router.get("/materials")
async def get_materials(admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        materials = db.query(Material).all()
        return [
            {
                "id": m.id,
                "key_name": m.key_name,
                "name": m.name,
                "price_per_ton": m.price_per_ton,
                "price_per_bag": m.price_per_bag,
                "bag_weight": m.bag_weight,
                "unit": m.unit,
                "description": m.description,
                "type": m.type
            }
            for m in materials
        ]
    finally:
        db.close()

@router.put("/materials/{material_id}")
async def update_material(material_id: int, data: MaterialUpdate, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Материал не найден")
        
        if data.price_per_ton is not None:
            material.price_per_ton = data.price_per_ton
        if data.price_per_bag is not None:
            material.price_per_bag = data.price_per_bag
        
        db.commit()
        return {"message": "Цена обновлена", "material": material.key_name}
    finally:
        db.close()

@router.post("/materials")
async def create_material(data: MaterialCreate, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        existing = db.query(Material).filter(Material.key_name == data.key_name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Материал уже существует")
        
        material = Material(**data.dict())
        db.add(material)
        db.commit()
        return {"message": "Материал создан", "id": material.id}
    finally:
        db.close()

@router.delete("/materials/{material_id}")
async def delete_material(material_id: int, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise HTTPException(status_code=404, detail="Материал не найден")
        
        db.delete(material)
        db.commit()
        return {"message": "Материал удалён"}
    finally:
        db.close()

@router.get("/zones")
async def get_zones(admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        zones = db.query(DeliveryZone).all()
        return [
            {
                "id": z.id,
                "key_name": z.key_name,
                "name": z.name,
                "base_price": z.base_price,
                "coefficient": z.coefficient,
                "note": z.note
            }
            for z in zones
        ]
    finally:
        db.close()

@router.put("/zones/{zone_id}")
async def update_zone(zone_id: int, data: ZoneUpdate, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail="Зона не найдена")
        
        zone.base_price = data.base_price
        db.commit()
        return {"message": "Цена доставки обновлена", "zone": zone.name}
    finally:
        db.close()

@router.post("/zones")
async def create_zone(data: ZoneCreate, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        existing = db.query(DeliveryZone).filter(DeliveryZone.key_name == data.key_name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Зона уже существует")
        
        zone = DeliveryZone(**data.dict())
        db.add(zone)
        db.commit()
        return {"message": "Зона создана", "id": zone.id}
    finally:
        db.close()

@router.delete("/zones/{zone_id}")
async def delete_zone(zone_id: int, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail="Зона не найдена")
        
        db.delete(zone)
        db.commit()
        return {"message": "Зона удалена"}
    finally:
        db.close()

from database import Microdistrict

@router.get("/microdistricts/{zone_id}")
async def get_microdistricts(zone_id: int, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        microdistricts = db.query(Microdistrict).filter(Microdistrict.zone_id == zone_id).all()
        return [
            {
                "id": md.id,
                "name": md.name,
                "slang_name": md.slang_name,
                "zone_id": md.zone_id
            }
            for md in microdistricts
        ]
    finally:
        db.close()

class MicrodistrictCreate(BaseModel):
    zone_id: int
    name: str
    slang_name: Optional[str] = None

@router.post("/microdistricts")
async def create_microdistrict(data: MicrodistrictCreate, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        microdistrict = Microdistrict(
            zone_id=data.zone_id,
            name=data.name,
            slang_name=data.slang_name
        )
        db.add(microdistrict)
        db.commit()
        return {"message": "Микрорайон добавлен", "id": microdistrict.id}
    finally:
        db.close()

@router.delete("/microdistricts/{microdistrict_id}")
async def delete_microdistrict(microdistrict_id: int, admin: str = Depends(verify_admin)):
    db = SessionLocal()
    try:
        microdistrict = db.query(Microdistrict).filter(Microdistrict.id == microdistrict_id).first()
        if not microdistrict:
            raise HTTPException(status_code=404, detail="Микрорайон не найден")
        
        db.delete(microdistrict)
        db.commit()
        return {"message": "Микрорайон удалён"}
    finally:
        db.close()