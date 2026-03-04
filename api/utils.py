import os
import pickle
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from .models import ScamDataset, ModelStatus

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------
MODEL_PATH = os.path.join(settings.BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, "vectorizer.pkl")

model = None
vectorizer = None


# --------------------------------------------------
# TRAIN MODEL FUNCTION
# --------------------------------------------------
def retrain_model():
    global model, vectorizer

    dataset = ScamDataset.objects.all()

    if dataset.count() < 2:
        print("❌ Not enough data to train")
        return 0

    texts = [data.text for data in dataset]
    labels = [data.label for data in dataset]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    y = labels

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    ModelStatus.objects.all().delete()
    ModelStatus.objects.create(accuracy=accuracy)

    print(f"✅ Model retrained successfully. Accuracy: {accuracy}%")

    return accuracy


# --------------------------------------------------
# SAFE MODEL LOAD
# --------------------------------------------------
def load_model():
    global model, vectorizer

    if model is not None and vectorizer is not None:
        return True

    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("⚠️ Model files not found.")
        return False

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)

        print("✅ Model loaded successfully")
        return True

    except Exception as e:
        print("❌ Model loading failed:", e)
        return False


# --------------------------------------------------
# PREDICT FUNCTION
# --------------------------------------------------
def predict_text(text):
    global model, vectorizer

    if not load_model():
        return {"error": "Model not trained yet"}

    vectorized_text = vectorizer.transform([text])
    prediction = model.predict(vectorized_text)[0]
    probability = model.predict_proba(vectorized_text)[0]

    confidence = round(max(probability) * 100, 2)

    return {
        "prediction": int(prediction),
        "confidence": confidence
    }