MATERIALS = {
    "щебень": {
        "name": "Щебень",
        "price_per_ton": 1700,
        "fractions": ["5-20", "20-40", "40-70"],
        "description": "Для бетона, фундамента, дорожек"
    },
    "щебень 5-20": {
        "name": "Щебень фракции 5-20мм",
        "price_per_ton": 1700,
        "description": "Мелкий щебень для бетона и дорожек"
    },
    "щебень 20-40": {
        "name": "Щебень фракции 20-40мм",
        "price_per_ton": 1650,
        "description": "Средний щебень для фундамента"
    },
    "доломит": {
        "name": "Доломит (белый камень)",
        "price_per_ton": 7500,
        "price_per_bag": 330,
        "bag_weight": 45,
        "description": "Для сада, дорожек, декора"
    },
    "песок": {
        "name": "Песок строительный",
        "price_per_ton": 800,
        "description": "Для бетона и строительных работ"
    },
    "гравий": {
        "name": "Гравий",
        "price_per_ton": 1600,
        "description": "Для дренажа и строительства"
    },
    "крошка": {
        "name": "Крошка гранитная",
        "price_per_ton": 1800,
        "description": "Для огорода, бетона, стяжки"
    },
    "отсев": {
        "name": "Отсев речной",
        "price_per_ton": 900,
        "description": "Для бетона, стяжки, штукатурки"
    }
}

def find_material(query):
    """Поиск материала в тексте"""
    query_lower = query.lower()
    
    for key in MATERIALS.keys():
        if key in query_lower:
            return key
    
    if "щебень" in query_lower:
        return "щебень 5-20"
    if "доломит" in query_lower:
        return "доломит"
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
    """Получить цену материала за тонну"""
    material = MATERIALS.get(material_key)
    if material and "price_per_ton" in material:
        return material["price_per_ton"]
    return 0