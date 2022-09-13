from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class MemberPostSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    slug = serializers.CharField()
    created_at = serializers.DateTimeField()
    author = serializers.StringRelatedField(source="user")
    post_url = serializers.HyperlinkedIdentityField(
        view_name="post-detail",
    )


class MembersListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True, source="get_full_name")
    total_posts = serializers.IntegerField(read_only=True)
    list_of_interests = serializers.StringRelatedField(many=True, source='interests', read_only=True)
    last_posts = MemberPostSerializer(source="last_five_posts", many=True)
    user_details = serializers.HyperlinkedIdentityField(
        view_name="member-detail",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "list_of_interests",
            "total_posts",
            "short_biography",
            "birth_date",
            "country",
            "city",
            "last_posts",
            "user_details"
        ]


class MembersDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True, source="get_full_name")
    list_of_interests = serializers.StringRelatedField(many=True, source='interests', read_only=True)
    total_posts = serializers.IntegerField(read_only=True)
    total_subscriptions = serializers.IntegerField(read_only=True)
    total_subscribers = serializers.IntegerField(read_only=True)
    last_posts = MemberPostSerializer(source="last_five_posts", many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "list_of_interests",
            "total_posts",
            "short_biography",
            "birth_date",
            "country",
            "city",
            "last_posts",
            "total_subscriptions",
            "total_subscribers",
        ]
