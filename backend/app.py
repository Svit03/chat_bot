from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
from materials import MATERIALS, DELIVERY_INFO, find_material

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

class Message(BaseModel):
    text: str
    user_id: str = "anonymous"

class BotResponse(BaseModel):
    reply: str
    intent: str
    confidence: float

def get_intent_ml(text):
    if pipeline is None:
        return "unknown", 0.5
    
    text_lower = text.lower()
    pred_id = pipeline.predict([text_lower])[0]
    proba = pipeline.predict_proba([text_lower])[0]
    confidence = max(proba)
    intent = id_to_intent[pred_id]
    return intent, confidence

def get_response(intent, text):
    if intent == "price":
        material = find_material(text)
        if material:
            info = MATERIALS[material]
            return f"💰 <strong>{info['name']}</strong>\n\nЦена: {info['price']} руб/{info['unit']}\n{info['description']}\n\n❓ Сколько тонн вам нужно? Уточните адрес доставки!"
        else:
            return f"💰 <strong>Наши цены:</strong>\n\n• 🪨 Щебень 5-20: 1700 руб/тонна\n• 🪨 Щебень 20-40: 1650 руб/тонна\n• 💎 Доломит: 330 руб/мешок 40-45кг\n• 🏖️ Песок: 800 руб/тонна\n• ⚫ Гравий: 1600 руб/тонна\n\n❓ Какой материал вас интересует?"
    
    elif intent == "delivery":
        return f"🚚 <strong>Доставка по Улан-Удэ</strong>\n\n✅ Самосвалы: 2 и 4 тонны\n✅ Стоимость: от 2000 руб (зависит от расстояния)\n\n📍 Уточните точный адрес для расчёта!"
    
    elif intent == "availability":
        material = find_material(text)
        if material:
            info = MATERIALS[material]
            return f"📦 <strong>{info['name']}</strong>\n\n✅ Есть в наличии!\n🚚 Можем отгрузить сегодня!\n\n❓ Сколько вам нужно?"
        return f"📦 <strong>Наличие на складе</strong>\n\n✅ Все материалы в наличии:\n• 🪨 Щебень (все фракции)\n• 💎 Доломит\n• 🏖️ Песок\n• ⚫ Гравий\n\n❓ Какой материал вас интересует?"
    
    elif intent == "contact":
        return f"📞 <strong>Наши контакты</strong>\n\n📱 Телефон: 575677\n💬 WhatsApp: 575677\n📧 Telegram: @nerud_03\n\n📍 Улан-Удэ\n\n⏰ Режим: Пн-Сб 8:00-19:00\n\n✨ Звоните, договоримся!"
    
    elif intent == "greeting":
        return f"👋 <strong>Здравствуйте! Я Неруд Консультант</strong>\n\n🚚 Доставка нерудных материалов по <strong>Улан-Удэ</strong>\n\n<strong>Что у нас есть:</strong>\n• 🪨 Щебень (5-20, 20-40, 40-70)\n• 💎 Доломит, мраморный щебень в мешках\n• 🏖️ Песок, ПГС\n• ⚫ Гравий, галька, крошка, отсев, уголь\n\n📞 <strong>Контакты:</strong> 575677\n\n💬 <strong>Что вас интересует?</strong>"
    
    return f"❌ Извините, я не совсем понял.\n\n📞 Позвоните нам: 575677\n\n💬 Или переформулируйте вопрос."

@app.get("/")
async def root():
    return {"message": "🚛 Неруд Консультант API", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=BotResponse)
async def chat(message: Message):
    intent, confidence = get_intent_ml(message.text)
    reply = get_response(intent, message.text)
    
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