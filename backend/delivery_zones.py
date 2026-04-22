from materials import MATERIALS

DELIVERY_ZONES = {
    "октябрьский": {
        "name": "Октябрьский район",
        "base_price": 3500,
        "microdistricts": [
            "комушка", "новая комушка", "забайкальский", "зверосовхоз", "горького", "звездный",
            "зерногородок", "импульс", "медведчиково", "мелькомбинат", "мясокомбинат",
            "николаевский", "октябрьский", "радуга", "светлый", "силикатный",
            "сокольники", "сосновый бор", "сосновка", "степной", "таежный", "тальцы",
            "тепловик", "тулунжа", "энергетик", "южный", "сотые кварталы",
            "октябрь", "зауда", "18-19 кварталы", "5-й цинхай", "20-й квартал",
            "форт", "nst", "новостройка", "43-й квартал", "поле чудес", "заря",
            "47-й квартал", "манхэттен", "чанкайши", "102-й квартал", "загробная",
            "нахаловка"
        ],
        "coefficient": 1.0
    },
    "советский": {
        "name": "Советский район",
        "base_price": 4000,
        "microdistricts": [
            "центр", "вагжанова", "исток", "солдатский", "сокол", "аэропорт",
            "заречный", "заречка", "тапхар", "левый берег", "кумыска", "стеклозавод",
            "арбат", "площадь советов", "башка", "голова", "площадь революции",
            "палец", "бигфак", "площадь банзарова", "банзарка", "борсоева", "китайка",
            "приречная", "радарка", "бабушкина", "новянка", "геологическая", "шестидом",
            "профсоюзная", "1-й цинхай", "дворянское гнездо", "модогоева", "лесная моль",
            "проспект 50-летия октября", "broadway", "0-й цинхай", "проспект победы",
            "злодейка", "аквариум", "филармония", "шары", "яйца", "кооперативный техникум",
            "копчик", "тск", "суконка", "элеватор", "ресбольница", "бруски",
            "пентагон", "4-й цинхай", "городской сад", "горсад", "огород", "батарейка",
            "почтовка", "гортоп", "дружба", "казахстан", "вертолетка", "старая барахолка"
        ],
        "coefficient": 1.15
    },
    "железнодорожный": {
        "name": "Железнодорожный район",
        "base_price": 5000,
        "microdistricts": [
            "аршан", "верхняя берёзовка","верхняя березовка", "берёзовка","березовка", "восточный", "загорск",
            "авиазавод", "машзавод", "зеленхоз", "зеленый", "кирз", "кирзавод",
            "лысая гора", "матросова", "мостовой", "орешково", "пвз", "площадка",
            "солнечный", "шишковка", "3-й цинхай"
        ],
        "coefficient": 1.43
    },
    "левый_берег": {
        "name": "Левый берег (Солдатский, Сосновый Бор, Степной)",
        "base_price": 5000,
        "microdistricts": ["солдатский", "левый берег", "сосновый бор", "сосновка", "степной"],
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
    
    if any(word in text_lower for word in ["центр", "арбат", "голова", "банзарка"]):
        return "советский", DELIVERY_ZONES["советский"]
    elif any(word in text_lower for word in ["вокзал", "ж/д", "железнодорожный"]):
        return "железнодорожный", DELIVERY_ZONES["железнодорожный"]
    elif any(word in text_lower for word in ["комушка", "октябрьский", "октябрь", "зауда"]):
        return "октябрьский", DELIVERY_ZONES["октябрьский"]
    elif any(word in text_lower for word in ["левый берег", "сосновка"]):
        return "левый_берег", DELIVERY_ZONES["левый_берег"]
    
    return "октябрьский", DELIVERY_ZONES["октябрьский"]

def detect_loading_point(text, material):
    """Определение места загрузки по материалу"""
    material_lower = material.lower() if material else ""
    
    for point_key, point_info in LOADING_POINTS.items():
        for mat in point_info["materials"]:
            if mat in material_lower:
                return point_key, point_info
    
    return "сотые_кварталы", LOADING_POINTS["сотые_кварталы"]

def calculate_delivery_price(zone_key, loading_point_key, material_key=None):
    """Расчёт стоимости доставки (с учётом бесплатной доставки для доломита/мраморного щебня)"""
    
    if material_key in ["доломит", "мраморный щебень"]:
        zone_lower = zone_key.lower()
        free_zones = ["октябрьский", "комушка", "горький", "радужный", "октябрь", "зауда"]
        
        for free_zone in free_zones:
            if free_zone in zone_lower:
                return 0 
        
        return 700
    
    zone = DELIVERY_ZONES.get(zone_key, DELIVERY_ZONES["октябрьский"])
    loading = LOADING_POINTS.get(loading_point_key, LOADING_POINTS["сотые_кварталы"])
    
    base_price = max(zone["base_price"], loading["base_price"])
    
    extra = 0
    if zone_key == "эрхирик" or loading_point_key == "эрхирик":
        extra = 500
    elif zone_key == "тапхар_иволгинск":
        extra = 500
    
    return base_price + extra