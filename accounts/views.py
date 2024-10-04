from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, ProfileSerializer
from django.contrib.auth import get_user_model

# Create your views here.
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Using RegisterSerializer to register users
    we override the create method to handle tokens upon registeration
    first we retrieve all incoming data from request.data and validating the data and we raise an exception if error
    occurred using raise_exception=True
    then we create the user and saved in the database using serializer.save method
    we generate a token for that user using RefreshToken.for_user
    we return the response with an access and refresh token with a 201 status code message

    """
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        return Response({'user': serializer.data,
                         "refresh_token": str(token),
                         "access_token": str(token.access_token)}, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    return self.request.user to return the profile of the logged in user
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


