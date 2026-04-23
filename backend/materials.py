from database import SessionLocal, Material

def get_all_materials():
    db = SessionLocal()
    try:
        materials = db.query(Material).all()
        return {m.key_name: {
            "name": m.name,
            "price_per_ton": m.price_per_ton,
            "price_per_bag": m.price_per_bag,
            "bag_weight": m.bag_weight,
            "unit": m.unit,
            "description": m.description,
            "type": m.type
        } for m in materials}
    finally:
        db.close()

def find_material(query):
    query_lower = query.lower()
    db = SessionLocal()
    try:
        materials = db.query(Material).all()
        
        for m in materials:
            if m.key_name.lower() in query_lower:
                return m.key_name
            if m.name.lower() in query_lower:
                return m.key_name
        
        words = query_lower.split()
        for word in words:
            for m in materials:
                if word in m.name.lower():
                    return m.key_name
        
        return None
    finally:
        db.close()

def get_material_price(material_key):
    db = SessionLocal()
    try:
        material = db.query(Material).filter(Material.key_name == material_key).first()
        if not material:
            return 0, "ton"
        if material.type == "bag":
            return material.price_per_bag or 0, "bag"
        return material.price_per_ton or 0, "ton"
    finally:
        db.close()

def get_material_name(material_key):
    db = SessionLocal()
    try:
        material = db.query(Material).filter(Material.key_name == material_key).first()
        return material.name if material else material_key
    finally:
        db.close()

def get_material_unit(material_key):
    db = SessionLocal()
    try:
        material = db.query(Material).filter(Material.key_name == material_key).first()
        if not material:
            return "тонна"
        return material.unit
    finally:
        db.close()