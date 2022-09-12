from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as ParentTokenObtainPairSerializer,
)
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer as ParentTokenRefreshSerializer,
)

from applications.authentication.models import User
from applications.common.serializers import NonNullableCharField


class TokenObtainPairSerializer(ParentTokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)
        data.update(
            {
                "user": self.user.get_full_name(),
                "groups": list(self.user.groups.values_list('name', flat=True))
            }
        )

        return data


class TokenRefreshSerializer(ParentTokenRefreshSerializer):
    pass


class UserInfoSerializer(serializers.ModelSerializer):
    # Read Fields
    full_name = serializers.CharField(read_only=True, source="get_full_name")
    list_of_interests = serializers.StringRelatedField(many=True, source='interests', read_only=True)
    groups = serializers.StringRelatedField(many=True, read_only=True)

    # Write Fields
    short_biography = NonNullableCharField(allow_blank=True, required=False)
    country = NonNullableCharField(allow_blank=True, required=False)
    city = NonNullableCharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "groups",
            "list_of_interests",
            # Write Fields
            "first_name",
            "last_name",
            "email",
            "short_biography",
            "birth_date",
            "country",
            "city",
            "interests",
        ]
        extra_kwargs = {'interests': {'write_only': True, 'required': False}}



class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    password = serializers.CharField(
        max_length=128,
        min_length=10,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', "first_name", "last_name", 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        refresh = ParentTokenObtainPairSerializer.get_token(instance)
        self._data = dict(
            **self.to_representation(self.instance),
            refresh=str(refresh),
            access=str(refresh.access_token)
        )

        return instance
