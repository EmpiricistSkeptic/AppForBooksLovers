from django.contrib import admin
from .models import Profile, Book, Post, Notification, Message, Discussion, Comment, Author, ChatMessage, UserReadingProgress, ReadingRoom


admin.site.register(Profile)
admin.site.register(Book)
admin.site.register(Post)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Discussion)
admin.site.register(Comment)
admin.site.register(Author)
admin.site.register(ChatMessage)
admin.site.register(ReadingRoom)
admin.site.register(UserReadingProgress)


