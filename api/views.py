from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import predict_text


def register(request):
    return JsonResponse({"message": "Register endpoint working"})


def login(request):
    return JsonResponse({"message": "Login endpoint working"})


def analyze(request):
    return JsonResponse({"message": "Analyze endpoint working"})


@csrf_exempt
def predict_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if not text:
            return JsonResponse({"error": "Text is required"}, status=400)

        result = predict_text(text)

        if "error" in result:
            return JsonResponse(result, status=500)

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)