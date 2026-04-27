from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import re
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

def extract_quantity(text, material_key=None):
    text_lower = text.lower().strip()
    
    number_words = {
        "одна": 1, "один": 1, "одну": 1,
        "две": 2, "два": 2, "двух": 2,
        "три": 3, "трёх": 3,
        "четыре": 4, "четырёх": 4,
        "пять": 5, "пяти": 5,
        "шесть": 6, "шести": 6,
        "семь": 7, "семи": 7,
        "восемь": 8, "восьми": 8,
        "девять": 9, "девяти": 9,
        "десять": 10, "десяти": 10
    }
    
    is_bag_material = material_key in ["доломит", "мраморный_щебень"] if material_key else False
    
    if text_lower.isdigit():
        quantity = int(text_lower)
        if is_bag_material:
            if 1 <= quantity <= 100:
                return {"value": quantity, "unit": "bag"}
        else:
            if 1 <= quantity <= 4:
                return {"value": quantity, "unit": "ton"}
    
    for word, num in number_words.items():
        if word == text_lower:
            if is_bag_material:
                if 1 <= num <= 100:
                    return {"value": num, "unit": "bag"}
            else:
                if 1 <= num <= 4:
                    return {"value": num, "unit": "ton"}
    
    if not is_bag_material:
        if text_lower == "тонна" or text_lower == "тонну" or text_lower == "тонны":
            return {"value": 1, "unit": "ton"}
    
    if is_bag_material:
        bag_match = re.search(r'(\d+)\s*мешк', text_lower)
        if bag_match:
            quantity = int(bag_match.group(1))
            if 1 <= quantity <= 100:
                return {"value": quantity, "unit": "bag"}
        
        if text_lower == "мешок" or text_lower == "мешка":
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
    if quantity == 1:
        ton_text = "тонна"
    elif 2 <= quantity <= 4:
        ton_text = "тонны"
    else:
        ton_text = "тонн"
    
    return f"""🚛 РАСЧЁТ СТОИМОСТИ

📦 Материал: {material_name}
⚖️ Количество: {quantity:.1f} {ton_text}

💰 Стоимость материала: {material_price:,.0f} руб/тонна × {quantity:.1f} = {material_price * quantity:,.0f} руб
🚚 Доставка: {delivery_price:,.0f} руб

━━━━━━━━━━━━━━━━━━━━
💰 ИТОГО: {total:,.0f} руб

📞 Для заказа звоните: 575677"""

def format_price_calculation_bag(material_name, quantity, material_price, delivery_price, total):
    if quantity == 1:
        bag_text = "мешок"
    elif 2 <= quantity <= 4:
        bag_text = "мешка"
    else:
        bag_text = "мешков"
    
    delivery_text = "БЕСПЛАТНО" if delivery_price == 0 else f"{delivery_price:,.0f} руб"
    return f"""🚛 РАСЧЁТ СТОИМОСТИ

📦 Материал: {material_name}
📦 Количество: {quantity} {bag_text} (по 40-45кг)

💰 Стоимость материала: {material_price} руб/мешок × {quantity} = {material_price * quantity:,.0f} руб
🚚 Доставка: {delivery_text}

━━━━━━━━━━━━━━━━━━━━
💰 ИТОГО: {total:,.0f} руб

📞 Для заказа звоните: 575677"""

def get_intent_ml(text):
    if pipeline is None:
        return "unknown", 0.5
    
    text_lower = text.lower()
    pred_id = pipeline.predict([text_lower])[0]
    proba = pipeline.predict_proba([text_lower])[0]
    confidence = max(proba)
    intent = id_to_intent[pred_id]
    return intent, confidence

def extract_material_from_price_query(text):
    text_lower = text.lower()
    
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

def get_response(intent, text, user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    text_lower = text.lower().strip()
    
    material = find_material(text)
    if not material:
        material = extract_material_from_price_query(text)
    
    if material:
        session["pending_material"] = material
    
    quantity_data = extract_quantity(text, session.get("pending_material"))
    if quantity_data and quantity_data not in ["max_exceeded", "invalid_unit"]:
        session["pending_quantity"] = quantity_data
    
    zone_key, zone_name = detect_delivery_zone(text)
    if zone_key:
        session["pending_zone"] = zone_key
    
    if session.get("awaiting_quantity") and quantity_data:
        session["awaiting_quantity"] = False
        session["awaiting_district"] = True
        material_name = get_material_name(session["pending_material"])
        value = quantity_data["value"]
        unit = "мешков" if quantity_data["unit"] == "bag" else ("тонна" if value == 1 else "тонны")
        return f"📦 {material_name}, {value} {unit}\n\n📍 Укажите район доставки:\n\n{get_districts_list()}"
    
    if session.get("awaiting_district") and zone_key:
        material = session.get("pending_material")
        quantity_data = session.get("pending_quantity")
        if material and quantity_data:
            material_price, price_unit = get_material_price(material)
            quantity = quantity_data["value"]
            material_name = get_material_name(material)
            delivery_price = calculate_delivery_price(zone_key, "сотые_кварталы", material)
            total = (material_price * quantity) + delivery_price
            session.clear()
            if price_unit == "bag":
                return format_price_calculation_bag(material_name, quantity, material_price, delivery_price, total)
            else:
                return format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total)
    
    if material and not quantity_data and not session.get("awaiting_quantity"):
        session["awaiting_quantity"] = True
        material_price, price_unit = get_material_price(material)
        material_name = get_material_name(material)
        if price_unit == "bag":
            return f"💰 {material_name}\n\n💰 Цена: {material_price} руб/мешок (40-45кг)\n🎁 Бесплатная доставка по Октябрьскому району\n\n❓ Укажите количество мешков"
        else:
            return f"💰 {material_name}\n\n💰 Цена: {material_price} руб/тонна\n\n❓ Укажите количество тонн (от 1 до 4)\n\nПримеры: 2, 3, 4"
    
    if quantity_data and not material:
        return "❓ Укажите материал\n\n• щебень\n• песок\n• гравий\n• крошка\n• отсев\n• доломит"
    
    if intent == "greeting":
        materials = get_all_materials()
        ton_materials = [info['name'] for m, info in materials.items() if info['type'] == 'ton']
        bag_materials = [info['name'] for m, info in materials.items() if info['type'] == 'bag']
        return f"""👋 Здравствуйте! Я Неруд Консультант

🚚 Доставка нерудных материалов по Улан-Удэ

📦 Что у нас есть:
• 🪨 Сыпучие: {', '.join(ton_materials[:5])}
• 💎 В мешках: {', '.join(bag_materials)}

🎁 Доломит: БЕСПЛАТНАЯ доставка по Октябрьскому району!

💬 Просто напишите, например: "4 тонны щебня" или "10 мешков доломита" """
    
    if not material and not quantity_data:
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
            result += '━━━━━━━━━━━━━━━━━━━━<br>'
            result += ''.join(ton_items) + '<br>'
        
        if bag_items:
            result += '💎 <strong>В мешках</strong><br>'
            result += '━━━━━━━━━━━━━━━━━━━━<br>'
            result += ''.join(bag_items) + '<br>'
        
        result += '<strong>💡 Напишите:</strong><br>'
        result += '"цена щебня" или "2 тонны песка"<br>'
        result += '🚛 <strong>Рассчитаю с доставкой</strong>'
        result += '</div>'
        
        return result
        
    elif intent == "delivery":
        zones = get_districts_list()
        return f"""🚚 Доставка по Улан-Удэ

🚛 Грузоподъёмность: 2 и 4 тонны (максимум 4 тонны за рейс)

{zones}

💡 Напишите: "4 тонны щебня в Комушку" или "10 мешков доломита" """
    
    elif intent == "availability":
        material = find_material(text)
        if material:
            material_price, price_unit = get_material_price(material)
            material_name = get_material_name(material)
            if price_unit == "bag":
                return f"""📦 {material_name}

✅ Есть в наличии!
💰 Цена: {material_price} руб/мешок (40-45кг)
🎁 Бесплатная доставка по Октябрьскому району

❓ Укажите количество мешков и район доставки"""
            else:
                return f"""📦 {material_name}

✅ Есть в наличии!
💰 Цена: {material_price} руб/тонна
🚛 Максимум: 4 тонны за рейс

❓ Укажите количество (1-4 тонны) и район доставки"""
        materials = get_all_materials()
        bag_materials = [info['name'] for m, info in materials.items() if info['type'] == 'bag']
        ton_materials = [info['name'] for m, info in materials.items() if info['type'] == 'ton']
        return f"""📦 Все материалы в наличии!

✅ Сыпучие (тонны): {', '.join(ton_materials[:5])}
✅ Мешковые: {', '.join(bag_materials)}

❓ Какой материал вас интересует?"""
    
    elif intent == "contact":
        return f"""📞 Наши контакты

📱 Телефон: 575677

📍 Улан-Удэ
🚛 Доставка от 1 до 4 тонн (сыпучие) или мешками

✨ Звоните, договоримся!"""
    
    elif intent == "greeting":
        materials = get_all_materials()
        ton_materials = [info['name'] for m, info in materials.items() if info['type'] == 'ton']
        bag_materials = [info['name'] for m, info in materials.items() if info['type'] == 'bag']
        return f"""👋 Здравствуйте! Я Неруд Консультант

🚚 Доставка нерудных материалов по Улан-Удэ

📦 Что у нас есть:
• 🪨 Сыпучие: {', '.join(ton_materials[:5])}
• 💎 В мешках: {', '.join(bag_materials)}

🎁 Доломит и мраморный щебень: БЕСПЛАТНАЯ доставка по Октябрьскому району!

💬 Просто напишите, например: "4 тонны щебня" или "10 мешков доломита"

Я сам спрошу район и рассчитаю стоимость!"""
    
    return f"""❌ Извините, я не совсем понял.

📞 Позвоните: 575677
💬 Или напишите: "4 тонны щебня в Комушку" или "10 мешков доломита" """

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