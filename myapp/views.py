from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from .models import Book, Profile, Post, Notification, Message, Discussion, Comment, Author, CustomUser
from .serializers import ProfileSerializer, PostSerializer, NotificationSerializer, MessageSerializer, DiscussionSerializer, CommentSerialier, BookSerializer, CustomUserSerializer, AuthorSerializer
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse



User = get_user_model()

def home(request):
    return HttpResponse("Welcome to the Home Page!")


class BookListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        


class ProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile)

        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddFavouriteBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        book = Book.objects.get(id=book_id)
        request.user.profile.favourite_books.add(book)
        return Response({'message': 'Book added to favourites.'})


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(author__in=request.user.following.all())
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_follow = User.objects.get(username=username)
            profile = Profile.objects.get(user=request.user)
            profile.following.add(user_to_follow.profile)
            return Response({'status': 'following'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = Message.objects.filter(recipient=request.user)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DiscussionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id):
        discussions = Discussion.objects.filter(book_id=book_id)
        serializer = DiscussionSerializer(discussions, many=True)
        return Response(serializer.data)
    
    def post(self, request, book_id):
        data = request.data.copy()
        data['book'] = book_id
        data['created_at'] = request.user.id
        serializer = DiscussionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 

class CommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, discussion_id):
        comments = Comment.objects.filter(discussion_id=discussion_id)
        serializer = CommentSerialier(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, discussion_id):
        data = request.data.copy()
        data['discussion'] = discussion_id
        data['created_at'] = request.user.id
        serializer = CommentSerialier(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, reqeust):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class BookSearchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        search = request.query_params.get('search', None)
        ordering = request.query_params.get('ordering', None)
        if search:
            books = books.filter(title__icontains=search) | books.filter(author__name__icontains=search)

        if ordering:
            books = books.order_by(ordering)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    


class AuthorSearchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        authors = Author.objects.all()
        search = request.query_params.get('search', 'None')
        if search:
            authors = authors.filter(name__icontains=search)
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    


class UserSearchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()

        search = request.query_params.get('search', None)
        if search:
            users = users.filter(username__icontains=search) | users(username__icontains=search)
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

    







