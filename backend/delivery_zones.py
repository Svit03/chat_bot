from database import SessionLocal, DeliveryZone, Microdistrict, FreeDolomiteMicrodistrict

def get_all_zones():
    db = SessionLocal()
    try:
        zones = db.query(DeliveryZone).all()
        result = {}
        for z in zones:
            microdistricts = db.query(Microdistrict).filter(Microdistrict.zone_id == z.id).all()
            result[z.key_name] = {
                "name": z.name,
                "base_price": z.base_price,
                "coefficient": z.coefficient,
                "note": z.note,
                "microdistricts": [m.name for m in microdistricts] + [m.slang_name for m in microdistricts if m.slang_name]
            }
        return result
    finally:
        db.close()

def detect_delivery_zone(text):
    text_lower = text.lower()
    db = SessionLocal()
    try:
        zones = db.query(DeliveryZone).all()
        for zone in zones:
            microdistricts = db.query(Microdistrict).filter(Microdistrict.zone_id == zone.id).all()
            for md in microdistricts:
                if md.name.lower() in text_lower or (md.slang_name and md.slang_name.lower() in text_lower):
                    print(f"📍 Найдена зона: {zone.name}, микрорайон: {md.name}")
                    return zone.key_name, {
                        "name": zone.name, 
                        "base_price": zone.base_price,
                        "microdistrict_name": md.name
                    }
        return "октябрьский", {
            "name": "Октябрьский район", 
            "base_price": 3500,
            "microdistrict_name": None
        }
    finally:
        db.close()

def calculate_delivery_price(zone_key, material_key=None, microdistrict_name=None):
    db = SessionLocal()
    try:
        zone = db.query(DeliveryZone).filter(DeliveryZone.key_name == zone_key).first()
        if not zone:
            return 3500
        
        if material_key in ["доломит", "мраморный_щебень"]:
            if microdistrict_name:
                print(f"🔍 Проверка бесплатной доставки для микрорайона: {microdistrict_name}")
                
                free_micro = db.query(FreeDolomiteMicrodistrict).filter(
                    (FreeDolomiteMicrodistrict.name.ilike(microdistrict_name)) |
                    (FreeDolomiteMicrodistrict.slang_name.ilike(microdistrict_name)) |
                    (FreeDolomiteMicrodistrict.name.ilike(f"%{microdistrict_name}%")) |
                    (FreeDolomiteMicrodistrict.slang_name.ilike(f"%{microdistrict_name}%"))
                ).first()
                
                if free_micro:
                    print(f"✅ БЕСПЛАТНАЯ доставка! Найден микрорайон: {free_micro.name} (народное: {free_micro.slang_name})")
                    return 0
                else:
                    print(f"❌ Микрорайон {microdistrict_name} не найден в списке бесплатных")
            
            return zone.bag_price if zone.bag_price else 700
        
        return zone.base_price
    
    finally:
        db.close()

def get_districts_list():
    db = SessionLocal()
    try:
        zones = db.query(DeliveryZone).all()
        result = []
        for z in zones:
            microdistricts = db.query(Microdistrict).filter(Microdistrict.zone_id == z.id).limit(3).all()
            examples = ", ".join([md.name for md in microdistricts[:2]])
            result.append(f"• {z.name} ({examples})")
        return "\n".join(result)
    finally:
        db.close()