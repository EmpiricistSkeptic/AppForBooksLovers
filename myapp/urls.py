from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('search/books/', views.BookSearchListView.as_view(), name='search-books'),
    path('books/<int:book_id>/discussions/', views.DiscussionListView.as_view(), name='discussion_list'),
    path('add-favourite-book/<int:book_id>/', views.AddFavouriteBookView.as_view(), name='add-favourite-book'),
    path('books/upload/', views.BookUploadView.as_view(), name='book-upload'),
    path('books/<int:book_id>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_id>/progress/', views.ReadingProgressView.as_view(), name='reading-progress'),
    path('discussions/<int:book_id>/', views.DiscussionListView.as_view(), name='discussion-list'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('search/authors/', views.AuthorSearchListView.as_view(), name='search-authors'),
    path('profile/', views.ProfileListView.as_view(), name='profile'),
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('follow/<int:user_id>/', views.FollowUserView.as_view(), name='follow-user'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('comments/<int:discussion_id>/', views.CommentListView.as_view(), name='comment-list'),
    path('messages/', views.MessageListView.as_view(), name='message-list'),
    path('search/users/', views.UserSearchListView.as_view(), name='search-users'),
]