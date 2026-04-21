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
    """Определение интента через ML модель"""
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
            return f"💰 {info['name']}\n\nЦена: {info['price']} руб/{info['unit']}\n{info['description']}\n\nСколько тонн вам нужно? Уточните адрес доставки!"
        else:
            materials_list = "\n".join([f"• {m}: {info['price']} руб/{info['unit']}" for m, info in MATERIALS.items()])
            return f"💰 У нас есть:\n{materials_list}\n\nКакой материал вас интересует?"
    
    elif intent == "delivery":
        return f"🚚 Доставка по {DELIVERY_INFO['city']}\n\nСамосвалы: {', '.join(DELIVERY_INFO['trucks'])}\nСтоимость: {DELIVERY_INFO['price']}\n\nУточните точный адрес для расчёта!"
    
    elif intent == "availability":
        material = find_material(text)
        if material:
            info = MATERIALS[material]
            return f"📦 {info['name']} - есть в наличии!\n\nМожем отгрузить сегодня!"
        return f"📦 Все материалы в наличии!\n\nСпрашивайте: щебень, доломит, песок, гравий"
    
    elif intent == "contact":
        return f"📞 Наши контакты:\n\n• Телефон: 575677\n\nЗвоните, договоримся!"
    
    elif intent == "greeting":
        return f"👋 Здравствуйте! Я бот-консультант по нерудным материалам.\n\nДоставка по Улан-Удэ самосвалами 2 и 4 тонны.\n\nЧто вас интересует?"
    
    return "Извините, я не совсем понял. Позвоните нам: 575677"

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