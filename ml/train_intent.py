import json
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

def train_intent_classifier():
    print("=" * 50)
    print("🚛 ОБУЧЕНИЕ ML МОДЕЛИ ДЛЯ ЧАТ-БОТА")
    print("=" * 50)

    print("\n📚 Загрузка данных...")
    with open('data/intents.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = []
    labels = []
    intent_to_id = {}
    id_to_intent = {}

    for idx, intent in enumerate(data['intents']):
        intent_to_id[intent['name']] = idx
        id_to_intent[idx] = intent['name']
        for example in intent['examples']:
            texts.append(example.lower())
            labels.append(idx)

    print(f"📊 Загружено {len(texts)} примеров")
    print(f"📋 Классы: {', '.join(intent_to_id.keys())}")

    print("\n🏋️ Обучение модели...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 5),
            max_features=5000
        )),
        ('clf', LogisticRegression(C=1.0, max_iter=1000, random_state=42))
    ])

    pipeline.fit(texts, labels)

    cv_scores = cross_val_score(pipeline, texts, labels, cv=3)
    print(f"✅ Точность модели: {cv_scores.mean():.2%} (+/- {cv_scores.std()*2:.2%})")

    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(pipeline, 'ml/models/intent_model.pkl')
    joblib.dump(id_to_intent, 'ml/models/id_to_intent.pkl')
    print("💾 Модель сохранена в ml/models/intent_model.pkl")

    print("\n🧪 Тестирование модели:")
    print("-" * 40)
    test_phrases = [
        "сколько стоит щебень",
        "доставка по улан удэ",
        "есть ли доломит",
        "ваш телефон",
        "привет",
        "цена песка",
        "привезите 2 тонны",
        "как с вами связаться"
    ]

    for phrase in test_phrases:
        pred_id = pipeline.predict([phrase.lower()])[0]
        proba = pipeline.predict_proba([phrase.lower()])[0]
        confidence = max(proba)
        intent = id_to_intent[pred_id]
        print(f"  '{phrase}' → {intent} (уверенность: {confidence:.1%})")

    print("\n✅ Обучение завершено!")
    return pipeline

if __name__ == "__main__":
    train_intent_classifier()