import os
import pickle
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ---------------------------------------------------
# Load ML Model & Vectorizer (Production Safe)
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

model = None
vectorizer = None

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)

    print("✅ Model and Vectorizer loaded successfully")

except Exception as e:
    print("❌ Model loading failed:", e)


# ---------------------------------------------------
# Register Endpoint (Dummy)
# ---------------------------------------------------

@csrf_exempt
def register(request):
    if request.method == "POST":
        return JsonResponse({"message": "Register endpoint working"})
    return JsonResponse({"error": "Use POST request"}, status=400)


# ---------------------------------------------------
# Login Endpoint (Dummy)
# ---------------------------------------------------

@csrf_exempt
def login(request):
    if request.method == "POST":
        return JsonResponse({"message": "Login endpoint working"})
    return JsonResponse({"error": "Use POST request"}, status=400)


# ---------------------------------------------------
# ML Analyze Endpoint
# ---------------------------------------------------

@csrf_exempt
def analyze(request):
    if request.method == "POST":
        try:
            if model is None or vectorizer is None:
                return JsonResponse(
                    {"error": "Model not loaded properly"},
                    status=500
                )

            data = json.loads(request.body)
            text = data.get("text", "").strip()

            if not text:
                return JsonResponse(
                    {"error": "No text provided"},
                    status=400
                )

            # Transform input
            text_vectorized = vectorizer.transform([text])

            # Predict
            prediction = model.predict(text_vectorized)[0]

            # Confidence (safe way)
            confidence = None
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(text_vectorized)[0]
                confidence = float(max(probabilities))

            return JsonResponse({
                "prediction": int(prediction),
                "confidence": round(confidence, 4) if confidence else None
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Use POST request"}, status=400)