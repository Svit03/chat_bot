MATERIALS = {
    "щебень": {
        "name": "Щебень",
        "price_per_ton": 1700,
        "unit": "тонна",
        "fractions": ["5-20", "20-40", "40-70"],
        "description": "Для бетона, фундамента, дорожек",
        "type": "ton"
    },
    "щебень 5-20": {
        "name": "Щебень фракции 5-20мм",
        "price_per_ton": 1700,
        "unit": "тонна",
        "description": "Мелкий щебень для бетона и дорожек",
        "type": "ton"
    },
    "щебень 20-40": {
        "name": "Щебень фракции 20-40мм",
        "price_per_ton": 1650,
        "unit": "тонна",
        "description": "Средний щебень для фундамента",
        "type": "ton"
    },
    "доломит": {
        "name": "Доломит (белый камень)",
        "price_per_bag": 350,
        "bag_weight": 45,
        "unit": "мешок",
        "description": "Для сада, дорожек, декора",
        "type": "bag",
        "free_delivery_zones": ["октябрьский", "комушка", "горький", "радужный"],
        "delivery_price_other": 700
    },
    "мраморный щебень": {
        "name": "Мраморный щебень в мешках",
        "price_per_bag": 350,
        "bag_weight": 45,
        "unit": "мешок",
        "description": "Для сада, огорода, дорожек и декора",
        "type": "bag",
        "free_delivery_zones": ["октябрьский", "комушка", "горький", "радужный"],
        "delivery_price_other": 700
    },
    "песок": {
        "name": "Песок строительный",
        "price_per_ton": 800,
        "unit": "тонна",
        "description": "Для бетона и строительных работ",
        "type": "ton"
    },
    "гравий": {
        "name": "Гравий",
        "price_per_ton": 1600,
        "unit": "тонна",
        "description": "Для дренажа и строительства",
        "type": "ton"
    },
    "крошка": {
        "name": "Крошка гранитная",
        "price_per_ton": 1800,
        "unit": "тонна",
        "description": "Для огорода, бетона, стяжки",
        "type": "ton"
    },
    "отсев": {
        "name": "Отсев речной",
        "price_per_ton": 900,
        "unit": "тонна",
        "description": "Для бетона, стяжки, штукатурки",
        "type": "ton"
    }
}

def find_material(query):
    query_lower = query.lower()
    
    for key in MATERIALS.keys():
        if key in query_lower:
            return key
    
    if "щебень" in query_lower:
        return "щебень 5-20"
    if "доломит" in query_lower:
        return "доломит"
    if "мраморный" in query_lower:
        return "мраморный щебень"
    if "песок" in query_lower:
        return "песок"
    if "гравий" in query_lower:
        return "гравий"
    if "крошка" in query_lower:
        return "крошка"
    if "отсев" in query_lower:
        return "отсев"
    
    return None

def get_material_price(material_key):
    """Получить цену материала (за мешок или за тонну)"""
    material = MATERIALS.get(material_key)
    if not material:
        return 0, "ton"
    
    if material.get("type") == "bag":
        return material.get("price_per_bag", 0), "bag"
    return material.get("price_per_ton", 0), "ton"

def get_material_unit(material_key):
    """Получить единицу измерения материала"""
    material = MATERIALS.get(material_key)
    if not material:
        return "тонна"
    return material.get("unit", "тонна")