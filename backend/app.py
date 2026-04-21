from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import re
from materials import MATERIALS, find_material, get_material_price
from delivery_zones import detect_delivery_zone, detect_loading_point, calculate_delivery_price, DELIVERY_ZONES

app = FastAPI(title="Неруд Консультант", version="1.0.0")

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

def extract_quantity(text):
    """Извлечение количества тонн из текста с ограничением до 4 тонн"""
    patterns = [
        r'(\d+(?:[.,]\d+)?)\s*тонн?',
        r'(\d+(?:[.,]\d+)?)\s*т',
        r'(\d+(?:[.,]\d+)?)\s*тонны?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            quantity = float(match.group(1).replace(',', '.'))
            if 1 <= quantity <= 4:
                return quantity
            elif quantity > 4:
                return "max_exceeded"
    return None

def extract_district(text):
    """Извлечение района доставки из текста"""
    text_lower = text.lower()
    
    for zone_key, zone_info in DELIVERY_ZONES.items():
        for microdistrict in zone_info["microdistricts"]:
            if microdistrict in text_lower:
                return zone_key, zone_info["name"]
    
    district_keywords = {
        "октябрьский": "октябрьский",
        "советский": "советский", 
        "железнодорожный": "железнодорожный",
        "левый берег": "левый_берег",
        "солдатский": "левый_берег",
        "комушка": "октябрьский",
        "забайкальский": "октябрьский",
        "центр": "советский",
        "вокзал": "железнодорожный",
        "берёзовка": "железнодорожный"
    }
    
    for keyword, zone in district_keywords.items():
        if keyword in text_lower:
            return zone, DELIVERY_ZONES[zone]["name"]
    
    return None, None

def format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total):
    """Форматирование расчёта стоимости (без откуда и скидки)"""
    return f"""🚛 РАСЧЁТ СТОИМОСТИ

📦 Материал: {material_name}
⚖️ Количество: {quantity} тонн
🚛 Машина: {quantity} тонн

💰 Стоимость материала: {material_price:,.0f} руб/тонна × {quantity} = {material_price * quantity:,.0f} руб
🚚 Доставка: {delivery_price:,.0f} руб

━━━━━━━━━━━━━━━━━━━━
💰 ИТОГО: {total:,.0f} руб

📞 Для заказа звоните: 575677"""

def get_districts_list():
    """Получить список районов для подсказки"""
    return """• Октябрьский район (Комушка, Забайкальский)
• Советский район (центр, Вагжанова)
• Железнодорожный район (Верхняя Берёзовка, Аршан)
• Левый берег (Солдатский, Сосновый Бор)"""

def get_intent_ml(text):
    if pipeline is None:
        return "unknown", 0.5
    
    text_lower = text.lower()
    pred_id = pipeline.predict([text_lower])[0]
    proba = pipeline.predict_proba([text_lower])[0]
    confidence = max(proba)
    intent = id_to_intent[pred_id]
    return intent, confidence

def get_response(intent, text, user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    
    if session.get("awaiting_district"):
        zone_key, zone_name = extract_district(text)
        if zone_key:
            material = session.get("pending_material")
            quantity = session.get("pending_quantity")
            
            if material and quantity:
                material_price = get_material_price(material)
                delivery_price = calculate_delivery_price(zone_key, "сотые_кварталы")
                material_name = MATERIALS[material]["name"]
                total = (material_price * quantity) + delivery_price
                
                session.clear()
                return format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total)
            else:
                session.clear()
                return "❌ Что-то пошло не так. Напишите '4 тонны щебня в Комушку'"
        else:
            return f"""📍 Укажите район доставки:

{get_districts_list()}

Пример: "в Комушку" или "в Октябрьский район" """
    
    if session.get("awaiting_quantity"):
        quantity = extract_quantity(text)
        
        if quantity == "max_exceeded":
            return f"""⚠️ Извините, наши самосвалы вмещают максимум 4 тонны за рейс.

Пожалуйста, укажите количество от 1 до 4 тонн.

Пример: "2 тонны" или "4 тонны" """
        
        if quantity:
            session["pending_quantity"] = quantity
            session["awaiting_quantity"] = False
            session["awaiting_district"] = True
            
            material_name = MATERIALS[session["pending_material"]]["name"]
            return f"""📦 {material_name}, {quantity} тонн

🚛 Доступные машины: 2 или 4 тонны

📍 Укажите район доставки:

{get_districts_list()}

Например: "в Комушку" """
        else:
            return f"""❓ Укажите количество тонн (от 1 до 4 тонн)

Примеры:
• "2 тонны"
• "4 тонны"
• "3 тонны" """
    
    if intent == "price":
        material = find_material(text)
        quantity = extract_quantity(text)
        zone_key, zone_name = extract_district(text)
        
        if quantity == "max_exceeded":
            return f"""⚠️ Извините, наши самосвалы вмещают максимум 4 тонны за рейс.

Пожалуйста, укажите количество от 1 до 4 тонн.

Пример: "4 тонны щебня в Комушку" """
        
        if material and quantity and zone_key:
            material_price = get_material_price(material)
            delivery_price = calculate_delivery_price(zone_key, "сотые_кварталы")
            material_name = MATERIALS[material]["name"]
            total = (material_price * quantity) + delivery_price
            return format_price_calculation_simple(material_name, quantity, material_price, delivery_price, total)
        
        elif material and quantity:
            session["pending_material"] = material
            session["pending_quantity"] = quantity
            session["awaiting_district"] = True
            material_name = MATERIALS[material]["name"]
            return f"""📦 {material_name}, {quantity} тонн

🚛 Доступные машины: 2 или 4 тонны

📍 Укажите район доставки:

{get_districts_list()}

Например: "в Комушку" """
        
        elif material:
            session["pending_material"] = material
            session["awaiting_quantity"] = True
            info = MATERIALS[material]
            return f"""💰 {info['name']}

💰 Цена: {info['price_per_ton']} руб/тонна
📝 {info['description']}

❓ Укажите количество тонн (от 1 до 4 тонн)

Примеры: "2 тонны" или "4 тонны" """
        
        else:
            materials_list = "\n".join([f"• {info['name']}: {info.get('price_per_ton', info.get('price_per_bag', 0))} руб/{info.get('unit', 'тонна')}" for m, info in MATERIALS.items()])
            return f"""💰 Наши материалы:

{materials_list}

❓ Какой материал вас интересует?

Пример: "щебень" """
    
    elif intent == "delivery":
        return f"""🚚 Доставка по Улан-Удэ

🚛 Грузоподъёмность: 2 и 4 тонны (максимум 4 тонны за рейс)

📍 Стоимость доставки:
• Октябрьский район: 3500 руб
• Советский район: 4000-4500 руб
• Левый берег: 5000 руб
• Железнодорожный район: 5000-5500 руб

💡 Напишите: "4 тонны щебня в Комушку" для расчёта полной стоимости"""
    
    elif intent == "availability":
        material = find_material(text)
        if material:
            info = MATERIALS[material]
            return f"""📦 {info['name']}

✅ Есть в наличии!
💰 Цена: {info['price_per_ton']} руб/тонна
🚛 Максимум: 4 тонны за рейс

❓ Укажите количество (1-4 тонны) и район доставки"""
        return f"""📦 Все материалы в наличии!

✅ Щебень
✅ Доломит
✅ Песок
✅ Гравий
✅ Крошка
✅ Отсев

🚛 Максимум: 4 тонны за рейс

❓ Какой материал вас интересует?"""
    
    elif intent == "contact":
        return f"""📞 Наши контакты

📱 Телефон: 575677
💬 WhatsApp: 575677

📍 Улан-Удэ
🚛 Доставка от 1 до 4 тонн

✨ Звоните, договоримся!"""
    
    elif intent == "greeting":
        return f"""👋 Здравствуйте! Я Неруд Консультант

🚚 Доставка нерудных материалов по Улан-Удэ
🚛 Грузоподъёмность: 2 и 4 тонны (максимум 4 тонны за рейс)

📦 Что у нас есть:
• 🪨 Щебень - 1700 руб/тонна
• 💎 Доломит - 330 руб/мешок
• 🏖️ Песок - 800 руб/тонна
• ⚫ Гравий - 1600 руб/тонна

💬 Просто напишите, например: "4 тонны щебня"

Я сам спрошу район и рассчитаю стоимость!"""
    
    return f"""❌ Извините, я не совсем понял.

📞 Позвоните: 575677
💬 Или напишите: "4 тонны щебня в Комушку" """

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