DELIVERY_ZONES = {
    "октябрьский": {
        "name": "Октябрьский район",
        "base_price": 3500,
        "microdistricts": ["комушка", "новая комушка", "забайкальский", "горького", "звездный", 
                          "зерногородок", "импульс", "медведчиково", "мелькомбинат", "мясокомбинат",
                          "николаевский", "октябрьский", "радуга", "светлый", "силикатный", 
                          "сокольники", "сосновый бор", "степной", "таежный", "тальцы", 
                          "тепловик", "тулунжа", "энергетик", "южный", "сотые кварталы"],
        "coefficient": 1.0
    },
    "советский": {
        "name": "Советский район",
        "base_price": 4000,
        "microdistricts": ["центр", "вагжанова", "исток", "солдатский", "сокол", "аэропорт", "тапхар"],
        "coefficient": 1.15
    },
    "железнодорожный": {
        "name": "Железнодорожный район",
        "base_price": 5000,
        "microdistricts": ["аршан", "верхняя берёзовка", "восточный", "гавань", "загорск", 
                          "зеленхоз", "зеленый", "кирз", "лысая гора", "матросова", "мостовой", 
                          "орешково", "площадка", "солнечный", "шишковка"],
        "coefficient": 1.43
    },
    "левый_берег": {
        "name": "Левый берег (Солдатский, Сосновый Бор, Степной)",
        "base_price": 5000,
        "microdistricts": ["солдатский", "левый берег", "сосновый бор", "степной"],
        "coefficient": 1.43,
        "note": "Доставка через мост"
    },
    "эрхирик": {
        "name": "Эрхирик (карьер)",
        "base_price": 5500,
        "microdistricts": ["эрхирик"],
        "coefficient": 1.57,
        "note": "Карьер гравия/отсева"
    },
    "тапхар_иволгинск": {
        "name": "Тапхар / Иволгинск",
        "base_price": 6500,
        "microdistricts": ["тапхар", "иволгинск", "иволга"],
        "coefficient": 1.86
    }
}

LOADING_POINTS = {
    "сотые_кварталы": {
        "name": "Сотые кварталы",
        "district": "октябрьский",
        "materials": ["щебень", "крошка"],
        "base_price": 3500
    },
    "эрхирик": {
        "name": "Эрхирик",
        "district": "эрхирик",
        "materials": ["гравий", "отсев"],
        "base_price": 5500
    },
    "солдатский": {
        "name": "Солдатский / Левый берег",
        "district": "левый_берег",
        "materials": ["песок", "пгс"],
        "base_price": 5000
    }
}

def detect_delivery_zone(text):
    """Определение зоны доставки по тексту"""
    text_lower = text.lower()
    
    for zone_key, zone_info in DELIVERY_ZONES.items():
        for microdistrict in zone_info["microdistricts"]:
            if microdistrict in text_lower:
                return zone_key, zone_info
    
    if any(word in text_lower for word in ["центр", "площадь"]):
        return "советский", DELIVERY_ZONES["советский"]
    elif any(word in text_lower for word in ["вокзал", "ж/д"]):
        return "железнодорожный", DELIVERY_ZONES["железнодорожный"]
    elif any(word in text_lower for word in ["комушка", "октябрьский"]):
        return "октябрьский", DELIVERY_ZONES["октябрьский"]
    
    return "октябрьский", DELIVERY_ZONES["октябрьский"]

def detect_loading_point(text, material):
    """Определение места загрузки по материалу"""
    material_lower = material.lower() if material else ""
    
    for point_key, point_info in LOADING_POINTS.items():
        for mat in point_info["materials"]:
            if mat in material_lower:
                return point_key, point_info
    
    return "сотые_кварталы", LOADING_POINTS["сотые_кварталы"]

def calculate_delivery_price(zone_key, loading_point_key):
    """Расчёт стоимости доставки с учётом зоны и места загрузки"""
    zone = DELIVERY_ZONES.get(zone_key, DELIVERY_ZONES["октябрьский"])
    loading = LOADING_POINTS.get(loading_point_key, LOADING_POINTS["сотые_кварталы"])
    
    base_price = max(zone["base_price"], loading["base_price"])
    
    extra = 0
    if zone_key == "эрхирик" or loading_point_key == "эрхирик":
        extra = 500
    elif zone_key == "тапхар_иволгинск":
        extra = 500
    
    return base_price + extra

def format_price_calculation(material_name, quantity, zone_key, loading_point_key, material_price, delivery_price):
    """Форматирование расчёта стоимости"""
    material_cost = material_price * quantity
    
    discount = 0
    if quantity >= 20:
        discount = material_cost * 0.10
        discount_note = "10% скидка за объём (от 20 тонн)"
    elif quantity >= 10:
        discount = material_cost * 0.05
        discount_note = "5% скидка за объём (от 10 тонн)"
    else:
        discount_note = "Нет скидки"
    
    total = material_cost + delivery_price - discount
    
    zone_info = DELIVERY_ZONES.get(zone_key, {})
    loading_info = LOADING_POINTS.get(loading_point_key, {})
    
    return f"""🚛 <strong>РАСЧЁТ СТОИМОСТИ</strong>

📦 <strong>Материал:</strong> {material_name}
⚖️ <strong>Количество:</strong> {quantity} тонн

💰 <strong>Стоимость материала:</strong>
   {quantity} × {material_price} руб = {material_cost:,.0f} руб

🚚 <strong>Доставка:</strong>
   Откуда: {loading_info.get('name', 'Сотые кварталы')}
   Куда: {zone_info.get('name', 'Октябрьский район')}
   Стоимость: {delivery_price:,.0f} руб

🎁 <strong>{discount_note}:</strong> -{discount:,.0f} руб

━━━━━━━━━━━━━━━━━━━━
💰 <strong>ИТОГО: {total:,.0f} руб</strong>

📞 Для оформления заказа звоните: 575677"""