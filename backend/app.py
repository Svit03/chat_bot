from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from materials import MATERIALS, DELIVERY_INFO, find_material

app = FastAPI(title="Неруд Консультант", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    user_id: str = "anonymous"

class BotResponse(BaseModel):
    reply: str
    intent: str
    confidence: float

def get_intent(text):
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["цена", "стоит", "почём", "сколько"]):
        return "price", 0.85
    elif any(word in text_lower for word in ["доставк", "привези", "довези"]):
        return "delivery", 0.80
    elif any(word in text_lower for word in ["есть", "наличие", "в наличии"]):
        return "availability", 0.75
    elif any(word in text_lower for word in ["телефон", "позвони", "контакт", "связаться"]):
        return "contact", 0.90
    elif any(word in text_lower for word in ["привет", "здравствуй", "добрый"]):
        return "greeting", 0.95
    else:
        return "unknown", 0.50

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
        return f"👋 Здравствуйте! Я бот-консультант по нерудным материалам.\n\nДоставка по Улан-Удэ самосвалами 2 и 4 тонны.\n\nЧто вас интересует? (цены, доставка, наличие, контакты)"
    
    return "Извините, я не совсем понял. Позвоните нам: 575677"

@app.get("/")
async def root():
    return {"message": "🚛 Неруд Консультант API", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=BotResponse)
async def chat(message: Message):
    intent, confidence = get_intent(message.text)
    reply = get_response(intent, message.text)
    
    return BotResponse(reply=reply, intent=intent, confidence=confidence)

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