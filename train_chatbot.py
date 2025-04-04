# train_chatbot.py
import json
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def train_chatbot(json_path='app/static/chat_rules.json'):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    X = []
    y = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            X.append(pattern)
            y.append(intent['tag'])

    vectorizer = CountVectorizer()
    X_vectorized = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vectorized, y)

    with open('chatbot_model.pkl', 'wb') as f:
        pickle.dump((model, vectorizer, data), f)

    print("✅ Đã huấn luyện xong và lưu model!")

if __name__ == "__main__":
    train_chatbot()