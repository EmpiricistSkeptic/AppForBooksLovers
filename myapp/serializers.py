from djoser.serializers import UserSerializer
from rest_framework import serializers
from .models import Profile, Book, Post, Notification, Message, Discussion, Comment, Author, AbstractUser, ReadingProgress, ReadingRoom, UserReadingProgress, ChatMessage

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'




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


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['recipient', 'sender', 'post', 'message', 'created_at', 'is_read']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'content', 'created_at', 'is_read']


class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class ReadingProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingProgress
        fields = '__all__'



class ReadingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingRoom
        fields = ['id', 'name', 'book', 'users']


class UserReadingProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReadingProgress
        fields = ['user', 'current_page', 'last_updated']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['user', 'message', 'timestamp']