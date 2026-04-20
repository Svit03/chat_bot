MATERIALS = {
    "щебень 5-20": {
        "name": "Щебень фракции 5-20мм",
        "price": 1700,
        "unit": "тонна",
        "description": "Мелкий щебень для бетона и дорожек",
        "source": "Новопавловка"
    },
    "щебень 20-40": {
        "name": "Щебень фракции 20-40мм",
        "price": 1650,
        "unit": "тонна",
        "description": "Средний щебень для фундамента",
        "source": "Баин-Зурхэ"
    },
    "доломит": {
        "name": "Доломит (белый камень)",
        "price": 330,
        "unit": "мешок 40-45кг",
        "description": "Для сада, дорожек, декора",
        "source": "Октябрьский район"
    },
    "песок": {
        "name": "Песок строительный",
        "price": 800,
        "unit": "тонна",
        "description": "Для бетона и строительных работ",
        "source": "Гусинка"
    },
    "гравий": {
        "name": "Гравий",
        "price": 1600,
        "unit": "тонна",
        "description": "Для дренажа и строительства",
        "source": "Баин-Зурхэ"
    }
}

DELIVERY_INFO = {
    "city": "Улан-Удэ",
    "trucks": ["2 тонны", "4 тонны"],
    "price": "от 2000 руб (зависит от расстояния)"
}

def find_material(query):
    """Поиск материала в тексте"""
    query_lower = query.lower()
    for key in MATERIALS.keys():
        if key in query_lower:
            return key
    return None