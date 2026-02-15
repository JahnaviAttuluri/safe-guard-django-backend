from django.urls import path
from .views import login_view   # lowercase

urlpatterns = [
    path('login/', login_view, name='login'),
]
