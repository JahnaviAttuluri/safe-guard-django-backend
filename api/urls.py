from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('analyze/', views.analyze),

    # 🔥 ML Prediction API
    path('predict/', views.predict_view),
]