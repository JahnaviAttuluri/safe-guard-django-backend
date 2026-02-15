from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Check if fields are missing
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Authenticate using username (Django uses username internally)
        user = authenticate(username=user.username, password=password)

        if user is not None:
            return Response(
                {
                    "message": "Login successful",
                    "username": user.username,
                    "email": user.email
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
