from rest_framework import generics, permissions, status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate

# Create your views here.
class RegisterView(APIView):
    permission_class = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class FollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        user_t0_follow = get_object_or_404(CustonUser, id=user_id)
        request.user.following.add(user_to_follow)
        return Response({"message": "You are now following this user."}, status=status.HTTP_200_OK)

class UnfollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
        request.user.following.remove(user_to_unfollow)
        return Response({'message': 'You have unfollow this user.'}, status=status.HTTP_200_OK)

class ListUsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]