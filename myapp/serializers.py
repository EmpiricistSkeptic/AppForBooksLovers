from djoser.serializers import UserSerializer
from rest_framework import serializers
from .models import Profile, Book

class ProfileSerializer(serializers.ModelSerializer):
    favourite_books = serializers.StringRelatedField(many=True)
    disliked_books = serializers.StringRelatedField(many=True)
    read_books = serializers.StringRelatedField(many=True)
    want_to_read_books = serializers.StringRelatedField(many=True)


    class Meta:
        model = Profile
        fields = ('name', 'photo', 'bio', 'favourite_books', 'disliked_books', 'read_books', 'want_to_read_books')



class CustomUserSerializer(UserSerializer):
    profile = ProfileSerializer()

    class Meta(UserSerializer.Meta):
        fields = ('id', 'username', 'email', 'profile')