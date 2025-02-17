from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from .models import Book, Profile, Post, Notification, Message, Discussion, Comment, Author, CustomUser, ReadingProgress, ReadingRoom, UserReadingProgress, ChatMessage
from .serializers import ProfileSerializer, PostSerializer, NotificationSerializer, MessageSerializer, DiscussionSerializer, CommentSerialier, BookSerializer, CustomUserSerializer, AuthorSerializer, ReadingProgressSerializer, ReadingRoomSerializer, UserReadingProgressSerializer, ChatMessageSerializer
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import ebooklib
from ebooklib import epub
import xmltodict




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
    
        


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return get_object_or_404(Profile, user=self.request.user)

    def get(self, request):
        profile = self.get_object
        serializer = ProfileSerializer(profile)

        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        profile = self.get_object
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddFavouriteBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):

        book = get_object_or_404(Book, id=book_id)
        profile = request.user.profile
        
        if profile.favourite_books.filter(pk=book.pk).exists():
            return Response({'message': 'Book is already in favourites.'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.favourite_books.add(book)
        
        return Response({'message': 'Book added to favourites.'}, status=status.HTTP_200_OK)



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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        user_to_follow = get_object_or_404(User, username=username)

        if user_to_follow == request.user:
            return Response(
                {'error': "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        profile = request.user.profile

        if profile.following.filter(pk=user_to_follow.profile.pk).exists():
            return Response(
                {'message': "Already following this user."},
                status=status.HTTP_400_BAD_REQUETS
            )
        
        profile.following.add(user_to_follow.profile)
        return Response(
            {'status': 'following'},
            status=status.HTTP_200_OK
        )


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
    
    

class BookUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valed():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id):
        cache_key = f'book_content_{book_id}'
        content = cache.get(cache_key)
        if not content:
            try:
                book = Book.objects.get(id=book_id)
                file_path = book.file.path
                content = self.extract_content(file_path)
                cache.set(cache_key, book, timeout=60*15)
            except Book.DoesNotExist:
                return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = BookSerializer(book)
        response_data = serializer.data['content'] = content
        return Response(response_data)
    
    def extract_content(self, file_path):
        extension = file_path.split('.')[-1].lower()
        if extension == 'pdf':
            return self.extract_pdf_content(file_path)
        elif extension == 'epub':
            return self.extract_epub_content(file_path)
        elif extension == 'fb2':
            return self.extract_fb2_content(file_path)
        else:
            return "Unsupported file format"


class BookUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, book_id):
        try:
            book = Book.objects.get(id=book)
            serializer = BookSerializer(Book, data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache_key = f'book_{book_id}'
                cache.delete(cache_key)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    

class ReadingProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id):
        cache_key = f'reading_progress_{request.user.id}_{book_id}'
        progress = cache.get(cache_key)
        if not progress:
            progress = ReadingProgress.objects.filter(user=request.user, book_id=book_id).first()
        if progress:
            cache.set(cache_key, progress, timeout=60*15)
        if progress:
            serializer = ReadingProgressSerializer(progress)
            return Response(serializer.data)
        return Response({'detail': 'No progress found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, book_id):
        data = request.data
        data['user'] = request.user.id
        data['book'] = book_id  
        serializer = ReadingProgressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, book_id):
        progress = ReadingProgress.objects.filter(user=request.user, book_id=book_id).first()
        if not progress:
            return Response({'detail': 'No progress found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReadingProgressSerializer(progress, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        room = ReadingRoom.objects.create(name=data['name'], book_id=data['book_id'])
        room.users.add(request.user)
        return Response({'room_id': room.id}, status=status.HTTP_201_CREATED)


class JoinRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = ReadingRoom.objects.get(id=room_id)
        room.users.add(request.user)
        return Response({'message': 'Joined the room'}, status=status.HTTP200_OK)
    

class UpdateProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        data = request.data
        progress, created = UserReadingProgress.objects.get_or_create(user=request.user, room_id=room_id)
        progress.current_page = data['current_page']
        progress.save()
        return Response({'message': 'Progress updated'}, status=status.HTTP_200_OK)


class GetRoomProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        progress = UserReadingProgress.objects.filter(room_id=room_id)
        serializer = UserReadingProgressSerializer(progress, mant=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        data = request.data
        message = ChatMessage.objects.create(room_id=room_id, user=request.user, message=data['message'])
        return Response({'message': 'Message sent'}, status=status.HTTP_201_CREATED)
    
    def get(self, request, room_id):
        message = ChatMessage.objects.filter(room_id=room_id).order_by('timestamp')
        serializer = ChatMessageSerializer(message, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






