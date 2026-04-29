from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import re
from difflib import get_close_matches
from materials import find_material, get_material_price, get_material_name, get_all_materials
from delivery_zones import detect_delivery_zone, calculate_delivery_price, get_districts_list
from admin import router as admin_router

app = FastAPI(title="Неруд Консультант", version="1.0.0")

app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_path = 'ml/models/intent_model.pkl'
id_map_path = 'ml/models/id_to_intent.pkl'

if os.path.exists(model_path):
    pipeline = joblib.load(model_path)
    id_to_intent = joblib.load(id_map_path)
    print("✅ ML модель загружена")
else:
    pipeline = None
    print("⚠️ ML модель не найдена, используется заглушка")

user_sessions = {}

class Message(BaseModel):
    text: str
    user_id: str = "anonymous"

class BotResponse(BaseModel):
    reply: str
    intent: str
    confidence: float

def normalize_text(text):
    text_lower = text.lower().strip()
    corrections = {
        "гравий": ["грави", "гравей", "гравии", "грвий"],
        "щебень": ["щебен", "щебнь", "щебенъ", "щеб", "шебень", "шебен"],
        "песок": ["писок", "писак", "песак", "песокк"],
        "доломит": ["даломит", "доломитт", "доломид", "доломи"],
        "отсев": ["отсевв", "отсеф", "отсевк"],
        "крошка": ["крошк", "крошкаа", "крошечка"],
        "уголь": ["угол", "угль", "угал"],
        "гранит": ["гранитт", "гранид"],
        "пыль": ["пыл", "пыльь"],
        "пгс": ["пгц", "пкс"],
        "галька": ["галка", "гальк", "галькаа"],
    }
    
    for correct, wrong_list in corrections.items():
        for wrong in wrong_list:
            if wrong in text_lower:
                text_lower = text_lower.replace(wrong, correct)
    
    common_typos = {
        "сколько": ["сколька", "скольки", "скольео", "скелько"],
        "цена": ["ценаа", "цина", "цына"],
        "стоит": ["стоет", "стоить", "стои"],
        "доставка": ["даставка", "доставк", "дастафка"],
        "телефон": ["телефан", "тэлефон", "телефонн"],
        "район": ["райан", "раен", "раён"],
    }
    
    for correct, wrong_list in common_typos.items():
        for wrong in wrong_list:
            if wrong in text_lower:
                text_lower = text_lower.replace(wrong, correct)
    
    return text_lower

def fuzzy_match_material(query, threshold=0.7):
    materials = get_all_materials()
    all_names = []
    name_to_key = {}
    
    for key, info in materials.items():
        all_names.append(info['name'].lower())
        name_to_key[info['name'].lower()] = key
        all_names.append(key.lower())
        name_to_key[key.lower()] = key
    
    matches = get_close_matches(query.lower(), all_names, n=1, cutoff=threshold)
    
    if matches:
        return name_to_key[matches[0]]
    
    return None

def get_bag_text(quantity):
    if quantity == 1:
        return "мешок"
    elif 2 <= quantity <= 4:
        return "мешка"
    else:
        return "мешков"

def get_ton_text(quantity):
    if quantity == 1:
        return "тонна"
    elif 2 <= quantity <= 4:
        return "тонны"
    else:
        return "тонн"

def extract_quantity(text, material_key=None):
    text_lower = normalize_text(text).strip()
    
    number_words = {
        "одна": 1, "один": 1, "одну": 1, "одного": 1,
        "две": 2, "два": 2, "двух": 2, "двум": 2,
        "три": 3, "трёх": 3, "трём": 3,
        "четыре": 4, "четырёх": 4, "четырем": 4,
        "пять": 5, "пяти": 5,
        "шесть": 6, "шести": 6,
        "семь": 7, "семи": 7,
        "восемь": 8, "восьми": 8,
        "девять": 9, "девяти": 9,
        "десять": 10, "десяти": 10,
        "одиннадцать": 11, "двенадцать": 12, "тринадцать": 13, "четырнадцать": 14, "пятнадцать": 15,
        "шестнадцать": 16, "семнадцать": 17, "восемнадцать": 18, "neunzehn": 19, "двадцать": 20,
        "тридцать": 30, "сорок": 40, "пятьдесят": 50, "шестьдесят": 60, "семьдесят": 70,
        "восемьдесят": 80, "девяносто": 90, "сто": 100
    }
    
    is_bag_material = False
    if material_key:
        materials = get_all_materials()
        if material_key in materials and materials[material_key]['type'] == 'bag':
            is_bag_material = True
    
    if text_lower.isdigit():
        quantity = int(text_lower)
        if is_bag_material:
            if 1 <= quantity <= 100:
                return {"value": quantity, "unit": "bag"}
        else:
            if 1 <= quantity <= 4:
                return {"value": quantity, "unit": "ton"}
        if not is_bag_material and quantity > 4:
            return "max_exceeded"
    
    for word, num in number_words.items():
        if word == text_lower or text_lower.startswith(word):
            if is_bag_material:
                if 1 <= num <= 100:
                    return {"value": num, "unit": "bag"}
            else:
                if 1 <= num <= 4:
                    return {"value": num, "unit": "ton"}
    
    if not is_bag_material:
        if text_lower in ["тонна", "тонну", "тонны", "тонн"]:
            return {"value": 1, "unit": "ton"}
    
    if is_bag_material:
        bag_match = re.search(r'(\d+)\s*мешк', text_lower)
        if bag_match:
            quantity = int(bag_match.group(1))
            if 1 <= quantity <= 100:
                return {"value": quantity, "unit": "bag"}
        
        if text_lower in ["мешок", "мешка", "мешков"]:
            return {"value": 1, "unit": "bag"}
        
        for word, num in number_words.items():
            if f"{word} мешк" in text_lower:
                if 1 <= num <= 100:
                    return {"value": num, "unit": "bag"}
    
    patterns = [
        r'(\d+)\s*тонн?',
        r'(\d+)\s*т',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            quantity = int(match.group(1))
            if is_bag_material:
                return "invalid_unit"
            else:
                if 1 <= quantity <= 4:
                    return {"value": quantity, "unit": "ton"}
                elif quantity > 4:
                    return "max_exceeded"
    
    return None

def format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total):
    ton_text = get_ton_text(quantity)
    
    return f"""<div class="material-name">📦 {material_name}</div>
<div class="price-amount">{material_price:,.0f} ₽ / тонна</div>
<div class="section-title"><span class="section-icon">⚖️</span> Количество</div>
<div>• {quantity:.1f} {ton_text}</div>
<div class="section-title"><span class="section-icon">💰</span> Стоимость материала</div>
<div>• {material_price:,.0f} ₽ × {quantity:.1f} = <strong>{material_price * quantity:,.0f} ₽</strong></div>
<div class="section-title"><span class="section-icon">🚚</span> Доставка</div>
<div>• {delivery_price:,.0f} ₽</div>
<div class="separator-line"></div>
<div class="total-cost">💰 ИТОГО: {total:,.0f} ₽</div>
<div class="delivery-cost">📞 Для заказа звоните: 575677</div>"""

def format_price_calculation_bag(material_name, quantity, material_price, delivery_price, total):
    bag_text = get_bag_text(quantity)
    delivery_text = "БЕСПЛАТНО" if delivery_price == 0 else f"{delivery_price:,.0f} ₽"
    
    return f"""<div class="material-name">📦 {material_name}</div>
<div class="price-amount">{material_price} ₽ / мешок</div>
<div class="section-title"><span class="section-icon">📦</span> Количество</div>
<div>• {quantity} {bag_text} (по 40-45 кг)</div>
<div class="section-title"><span class="section-icon">💰</span> Стоимость материала</div>
<div>• {material_price} ₽ × {quantity} = <strong>{material_price * quantity:,.0f} ₽</strong></div>
<div class="section-title"><span class="section-icon">🚚</span> Доставка</div>
<div>• {delivery_text}</div>
<div class="separator-line"></div>
<div class="total-cost">💰 ИТОГО: {total:,.0f} ₽</div>
<div class="delivery-cost">📞 Для заказа звоните: 575677</div>"""

def get_intent_ml(text):
    if pipeline is None:
        return "unknown", 0.5
    
    text_lower = normalize_text(text)
    pred_id = pipeline.predict([text_lower])[0]
    proba = pipeline.predict_proba([text_lower])[0]
    confidence = max(proba)
    intent = id_to_intent[pred_id]
    return intent, confidence

def extract_material_from_price_query(text):
    text_lower = normalize_text(text)
    
    price_words = ["цена", "почём", "сколько", "стоит", "стоимость", "руб"]
    if not any(word in text_lower for word in price_words):
        return None
    
    materials = get_all_materials()
    
    for material_key, material_info in materials.items():
        material_name = material_info["name"].lower()
        if material_name in text_lower:
            return material_key

    for material_key in materials.keys():
        if material_key in text_lower:
            return material_key

    for material_key, material_info in materials.items():
        for part in material_info["name"].lower().split():
            if len(part) > 3 and part in text_lower:
                return material_key

    return None

def get_districts_list_html():
    return """<div class="district-item"><span class="section-icon">🏘️</span> <span class="district-name">Советский район</span> — Вагжанова, Исток</div>
<div class="district-item"><span class="section-icon">🚂</span> <span class="district-name">Железнодорожный район</span> — Аршан, Верхняя Берёзовка</div>
<div class="district-item"><span class="section-icon">🏭</span> <span class="district-name">Октябрьский район</span> — Комушка, Забайкальский</div>
<div class="district-item"><span class="section-icon">🌲</span> <span class="district-name">Отдалённые микрорайоны</span> — Сосновый бор, Тальцы</div>
<div class="example-query">💡 Например: "в Комушку" или "в Октябрьский район"</div>"""

def get_free_delivery_note():
    return """<div class="delivery-cost">🎁 В некоторые микрорайоны доставка мешковых материалов БЕСПЛАТНО!</div>"""

def get_greeting_message():
    return f"""<div class="material-name">👋 Здравствуйте! Я Неруд Консультант</div>
<div class="price-amount">🚚 Доставка по Улан-Удэ</div>
<div class="section-title"><span class="section-icon">📦</span> Что у нас есть</div>
<div class="district-item">• 🪨 Щебень (5-20, 20-40, 40-70)</div>
<div class="district-item">• 💎 Доломит в мешках</div>
<div class="district-item">• 🏖️ Песок, ПГС</div>
<div class="district-item">• ⚫ Гравий, крошка, отсев, уголь</div>
<div class="delivery-cost">📞 Контакты: 575677</div>
<div class="example-query">💬 Что вас интересует?</div>"""

def get_response(intent, text, user_id):
    text_normalized = normalize_text(text)
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    
    if session.get("awaiting_quantity"):
        quantity_data = extract_quantity(text_normalized, session.get("pending_material"))
        if quantity_data and quantity_data not in ["max_exceeded", "invalid_unit"]:
            session["pending_quantity"] = quantity_data
            session["awaiting_quantity"] = False
            session["awaiting_district"] = True
            material_name = get_material_name(session["pending_material"])
            value = quantity_data["value"]
            if quantity_data["unit"] == "bag":
                bag_text = get_bag_text(value)
                unit = bag_text
            else:
                unit = get_ton_text(value)
            return f"""<div class="material-name">📦 {material_name}</div>
<div class="price-amount">{value} {unit}</div>
<div class="section-title"><span class="section-icon">📍</span> Укажите район доставки</div>
{get_districts_list_html()}"""
        elif quantity_data == "max_exceeded":
            session.clear()
            return """<div class="material-name">⚠️ Максимум за рейс - 4 тонны!</div>
<div class="price-amount">🚛 Наш самосвал вмещает до 4 тонн</div>
<div class="example-query">💬 Укажите количество от 1 до 4 тонн</div>"""
    
    if session.get("awaiting_district"):
        zone_key, zone_info = detect_delivery_zone(text_normalized)
        if zone_key:
            material = session.get("pending_material")
            quantity_data = session.get("pending_quantity")
            if material and quantity_data:
                material_price, price_unit = get_material_price(material)
                quantity = quantity_data["value"]
                material_name = get_material_name(material)
                
                microdistrict_name = zone_info.get("microdistrict_name") if zone_info else None
                
                delivery_price = calculate_delivery_price(zone_key, material, microdistrict_name)
                total = (material_price * quantity) + delivery_price
                session.clear()
                if price_unit == "bag":
                    return format_price_calculation_bag(material_name, quantity, material_price, delivery_price, total)
                else:
                    return format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total)
    
    material = find_material(text_normalized)
    if not material:
        material = extract_material_from_price_query(text_normalized)
    if not material:
        material = fuzzy_match_material(text_normalized)
    
    quantity_data = extract_quantity(text_normalized, material)
    
    zone_key, zone_info = detect_delivery_zone(text_normalized)
    
    if material and quantity_data and quantity_data not in ["max_exceeded", "invalid_unit"] and zone_key:
        material_price, price_unit = get_material_price(material)
        quantity = quantity_data["value"]
        material_name = get_material_name(material)
        
        microdistrict_name = zone_info.get("microdistrict_name") if zone_info else None
        
        delivery_price = calculate_delivery_price(zone_key, material, microdistrict_name)
        total = (material_price * quantity) + delivery_price
        session.clear()
        if price_unit == "bag":
            return format_price_calculation_bag(material_name, quantity, material_price, delivery_price, total)
        else:
            return format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total)
    
    if material and quantity_data and quantity_data not in ["max_exceeded", "invalid_unit"]:
        session["pending_material"] = material
        session["pending_quantity"] = quantity_data
        session["awaiting_district"] = True
        material_name = get_material_name(material)
        value = quantity_data["value"]
        if quantity_data["unit"] == "bag":
            bag_text = get_bag_text(value)
            unit = bag_text
        else:
            unit = get_ton_text(value)
        return f"""<div class="material-name">📦 {material_name}</div>
<div class="price-amount">{value} {unit}</div>
<div class="section-title"><span class="section-icon">📍</span> Укажите район доставки</div>
{get_districts_list_html()}"""
    
    if material and not quantity_data:
        session["pending_material"] = material
        session["awaiting_quantity"] = True
        material_price, price_unit = get_material_price(material)
        material_name = get_material_name(material)
        if price_unit == "bag":
            return f"""<div class="material-name">💰 {material_name}</div>
<div class="price-amount">{material_price} ₽ / мешок (40-45 кг)</div>
{get_free_delivery_note()}
<div class="section-title"><span class="section-icon">❓</span> Укажите количество мешков (1-100)</div>
<div class="example-query">Примеры: 10, 5, 20</div>"""
        else:
            return f"""<div class="material-name">💰 {material_name}</div>
<div class="price-amount">{material_price:,.0f} ₽ / тонна</div>
<div class="section-title"><span class="section-icon">❓</span> Укажите количество тонн (от 1 до 4)</div>
<div class="example-query">Примеры: 2, 3, 4</div>"""
    
    if quantity_data == "max_exceeded":
        return """<div class="material-name">⚠️ Максимум за рейс - 4 тонны!</div>
<div class="price-amount">🚛 Наш самосвал вмещает до 4 тонн</div>
<div class="example-query">💬 Укажите количество от 1 до 4 тонн</div>"""
    
    if quantity_data and not material:
        return """<div class="material-name">❓ Укажите материал</div>
<div class="price-amount">Доступные материалы:</div>
<div class="district-item">• 🪨 щебень</div>
<div class="district-item">• 🏖️ песок</div>
<div class="district-item">• ⚫ гравий</div>
<div class="district-item">• 🪨 крошка</div>
<div class="district-item">• 🔘 отсев</div>
<div class="district-item">• 💎 доломит</div>
<div class="example-query">💡 Например: "2 тонны гравия"</div>"""
    
    if intent == "greeting":
        return get_greeting_message()
    
    if intent == "contact":
        return f"""<div class="material-name">📞 Наши контакты</div>
<div class="price-amount">📱 Телефон: 575677</div>
<div class="district-item">📍 Улан-Удэ</div>
<div class="district-item">🚛 Доставка от 1 до 4 тонн (сыпучие) или мешками</div>
<div class="delivery-cost">✨ Звоните, договоримся!</div>"""
    
    if not material and not quantity_data and intent != "greeting" and intent != "contact":
        materials = get_all_materials()
        ton_items = []
        bag_items = []
        
        for m, info in materials.items():
            if info['type'] == 'ton' and info.get('price_per_ton'):
                price = int(info['price_per_ton'])
                price_str = f"{price:,}".replace(",", " ")
                ton_items.append(f'<div class="price-row"><span class="price-name">• {info["name"]}</span><span class="price-value">{price_str} ₽</span></div>')
            elif info['type'] == 'bag' and info.get('price_per_bag'):
                price = int(info['price_per_bag'])
                price_str = f"{price:,}".replace(",", " ")
                bag_items.append(f'<div class="price-row"><span class="price-name">• {info["name"]}</span><span class="price-value">{price_str} ₽ / мешок</span></div>')
        
        result = '<div class="price-list">'
        result += '<strong>💰 ПРАЙС-ЛИСТ</strong><br><br>'
        
        if ton_items:
            result += '🪨 <strong>Сыпучие материалы (за тонну)</strong><br>'
            result += '<div class="separator-line"></div>'
            result += ''.join(ton_items) + '<br>'
        
        if bag_items:
            result += '💎 <strong>В мешках (по 40-45 кг)</strong><br>'
            result += '<div class="separator-line"></div>'
            result += ''.join(bag_items) + '<br>'
        
        result += '<div class="example-query">💡 Напишите: "цена щебня" или "2 тонны песка"</div>'
        result += '<div class="delivery-cost">🚛 Рассчитаю с доставкой</div>'
        result += '</div>'
        
        return result
    
    elif intent == "delivery":
        return f"""<div class="material-name">🚚 Доставка по Улан-Удэ</div>
<div class="price-amount">🚛 Грузоподъёмность: 2 и 4 тонны (максимум 4 тонны за рейс)</div>
{get_districts_list_html()}
{get_free_delivery_note()}
<div class="example-query">💡 Напишите: "4 тонны щебня в Комушку" или "10 мешков доломита"</div>"""
    
    elif intent == "availability":
        if material:
            material_price, price_unit = get_material_price(material)
            material_name = get_material_name(material)
            if price_unit == "bag":
                return f"""<div class="material-name">📦 {material_name}</div>
<div class="price-amount">✅ Есть в наличии!</div>
<div class="price-value">{material_price} ₽ / мешок (40-45 кг)</div>
{get_free_delivery_note()}
<div class="section-title"><span class="section-icon">❓</span> Укажите количество мешков и район доставки</div>
<div class="example-query">Пример: "10 мешков доломита в Комушку"</div>"""
            else:
                return f"""<div class="material-name">📦 {material_name}</div>
<div class="price-amount">✅ Есть в наличии!</div>
<div class="price-value">{material_price:,.0f} ₽ / тонна</div>
<div class="delivery-cost">🚛 Максимум: 4 тонны за рейс</div>
<div class="section-title"><span class="section-icon">❓</span> Укажите количество (1-4 тонны) и район доставки</div>
<div class="example-query">Пример: "4 тонны гравия в Сокол"</div>"""
        materials = get_all_materials()
        bag_materials = [info['name'] for m, info in materials.items() if info['type'] == 'bag']
        ton_materials = [info['name'] for m, info in materials.items() if info['type'] == 'ton']
        return f"""<div class="material-name">📦 Все материалы в наличии!</div>
<div class="price-amount">✅ Сыпучие (тонны): {', '.join(ton_materials[:5])}</div>
<div class="price-amount">✅ Мешковые (по 40-45 кг): {', '.join(bag_materials)}</div>
<div class="section-title"><span class="section-icon">❓</span> Какой материал вас интересует?</div>
<div class="example-query">💡 Например: "гравий есть?"</div>"""
    
    return f"""<div class="material-name">❌ Извините, я не совсем понял</div>
<div class="price-amount">📞 Позвоните: 575677</div>
<div class="example-query">💬 Или напишите: "4 тонны щебня в Комушку" или "10 мешков доломита"</div>"""

@app.get("/")
async def root():
    return {"message": "🚛 Неруд Консультант API", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=BotResponse)
async def chat(message: Message):
    intent, confidence = get_intent_ml(message.text)
    reply = get_response(intent, message.text, message.user_id)
    
    return BotResponse(reply=reply, intent=intent, confidence=round(confidence, 3))

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚛 НЕРУД КОНСУЛЬТАНТ - ЗАПУСК БЭКЕНДА")
    print("=" * 50)
    print("📍 Доставка: Улан-Удэ")
    print("🚀 Сервер: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)