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

    # Vectorize
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    y = labels

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Accuracy
    y_pred = model.predict(X_test)
    accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)

    # Save model files
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    # Save accuracy in DB
    ModelStatus.objects.all().delete()
    ModelStatus.objects.create(accuracy=accuracy)

    print(f"✅ Model retrained successfully. Accuracy: {accuracy}%")

    return accuracy


# --------------------------------------------------
# LOAD MODEL (AUTO RECOVERY)
# --------------------------------------------------
def load_model():
    global model, vectorizer

    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)

            with open(VECTORIZER_PATH, "rb") as f:
                vectorizer = pickle.load(f)

            print("✅ Model loaded successfully")

        except Exception as e:
            print("❌ Model loading failed:", e)
            retrain_model()

    else:
        print("⚠️ Model files not found. Training new model...")
        retrain_model()


# --------------------------------------------------
# PREDICT FUNCTION
# --------------------------------------------------
def predict_text(text):
    global model, vectorizer

    if model is None or vectorizer is None:
        load_model()

    if model is None:
        return {"error": "Model not available"}

    vectorized_text = vectorizer.transform([text])
    prediction = model.predict(vectorized_text)[0]
    probability = model.predict_proba(vectorized_text)[0]

    confidence = round(max(probability) * 100, 2)

    return {
        "prediction": int(prediction),
        "confidence": confidence
    }


# --------------------------------------------------
# AUTO LOAD MODEL ON SERVER START
# --------------------------------------------------
load_model()