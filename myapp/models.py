from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=False, null=False)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, bull=True)
    favourite_books = models.ManyToManyField('Book', related_name='fans', blank=True)
    read_books = models.ManyToManyField('Book', related_name='done', blank=True)
    want_to_read_books = models.ManyToManyField('Book', related_name='wish', blank=True)
    disliked_books = models.ManyToManyField('Book', related_name='haters', black=True)

    def __str__(self):
        return self.user.username
    

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.CharField(max_length=255)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    ratings = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    