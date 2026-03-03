from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pickle
import os

# -----------------------------------
# Load Model + Vectorizer Safely
# -----------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

model = None
vectorizer = None

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)

    print("✅ Model loaded successfully")

except Exception as e:
    print("❌ Model loading failed:", e)


# -----------------------------------
# EXISTING AUTH APIs (keep yours)
# -----------------------------------

def register(request):
    return JsonResponse({"message": "Register endpoint working"})

def login(request):
    return JsonResponse({"message": "Login endpoint working"})

def analyze(request):
    return JsonResponse({"message": "Analyze endpoint working"})


# -----------------------------------
# 🔥 PREDICT API
# -----------------------------------

@csrf_exempt
def predict_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    if model is None or vectorizer is None:
        return JsonResponse({"error": "Model not loaded"}, status=500)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if not text:
            return JsonResponse({"error": "Text is required"}, status=400)

        transformed = vectorizer.transform([text])
        prediction = model.predict(transformed)[0]

        # Optional: confidence
        confidence = None
        if hasattr(model, "predict_proba"):
            confidence = float(max(model.predict_proba(transformed)[0]))

        result = "Fraudulent" if prediction == 1 else "Real"

        return JsonResponse({
            "prediction": result,
            "confidence": confidence
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)