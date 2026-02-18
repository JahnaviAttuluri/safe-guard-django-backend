import os
import pickle
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Get current directory (api folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load trained model and vectorizer
model_path = os.path.join(BASE_DIR, "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))


# ---------------------------
# Dummy Register Endpoint
# ---------------------------
@csrf_exempt
def register(request):
    return JsonResponse({"message": "Register endpoint working"})


# ---------------------------
# Dummy Login Endpoint
# ---------------------------
@csrf_exempt
def login(request):
    return JsonResponse({"message": "Login endpoint working"})


# ---------------------------
# ML Analyze Endpoint
# ---------------------------
@csrf_exempt
def analyze(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")

            if not text:
                return JsonResponse({"error": "No text provided"}, status=400)

            # Transform text
            text_vectorized = vectorizer.transform([text])

            # Predict
            prediction = model.predict(text_vectorized)[0]
            probability = model.predict_proba(text_vectorized)[0][1]

            return JsonResponse({
                "prediction": int(prediction),
                "confidence": round(float(probability), 4)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Use POST request"})
