from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=False, null=False)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    favourite_books = models.ManyToManyField('Book', related_name='fans', blank=True)
    read_books = models.ManyToManyField('Book', related_name='done', blank=True)
    want_to_read_books = models.ManyToManyField('Book', related_name='wish', blank=True)
    disliked_books = models.ManyToManyField('Book', related_name='haters', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followed_by', blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='is_following', blank=True)



    def __str__(self):
        return self.user.username
    

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=50, null=False, default='Unknown')
    author = models.CharField(max_length=255)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    ratings = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    file = models.FileField(upload_to='books/', null=True, blank=True)

    def __str__(self):
        return self.title


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    current_page = models.IntegerField(default=1)
    last_accessed = models.DateTimeField(auto_now=True)
    


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.author.username} : {self.content[:30]}'
    

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE,)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification to {self.recipient.username} from {self.sender.username}'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_message')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_message')
    content = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username}'
    

class Discussion(models.Model):
    book = models.ForeignKey(Book, related_name='disscussion', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField()
    picture = models.ImageField(upload_to='authors_pictures/', blank=True, null=True)

    






    



    