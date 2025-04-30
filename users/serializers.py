from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now

User = get_user_model()


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
        else:
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid username or password")

        user.last_login = now()
        user.save(update_fields=["last_login"])
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get("user")

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "refresh": str(refresh),
            "access": str(access),
        }
