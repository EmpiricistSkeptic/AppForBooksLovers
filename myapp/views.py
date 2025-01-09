from rest_framework.views import APIView
from rest_framework.responce import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Book, Profile
from .serializers import ProfileSerializer
from django.shortcuts import get_object_or_404



class ProfileView(APIView):
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
    



