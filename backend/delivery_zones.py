from database import SessionLocal, DeliveryZone, Microdistrict

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
                    return zone.key_name, {"name": zone.name, "base_price": zone.base_price}
        return "октябрьский", {"name": "Октябрьский район", "base_price": 3500}
    finally:
        db.close()

def calculate_delivery_price(zone_key, loading_point_key, material_key=None):
    db = SessionLocal()
    try:
        zone = db.query(DeliveryZone).filter(DeliveryZone.key_name == zone_key).first()
        if not zone:
            return 3500
        
        if material_key in ["доломит", "мраморный_щебень"]:
            if zone_key == "октябрьский":
                return 0
            return 700
        
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