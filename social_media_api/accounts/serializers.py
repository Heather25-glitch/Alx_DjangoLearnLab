from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token

User = get_user_model()  # ✅ Ensure this is used

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # ✅ Ensure this is here
        token = Token.objects.create(user=user)  # ✅ Explicitly creating a token
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")
            data['user'] = user
            token, created = Token.objects.get_or_create(user=user)  # ✅ Ensure token retrieval
            data['token'] = token.key
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data
