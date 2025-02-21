from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from myapp.models import Book, Profile, Post, Notification, Message, Discussion, Comment
from myapp.serializers import BookSerializer, ProfileSerializer, PostSerializer, NotificationSerializer, MessageSerializer, DiscussionSerializer, CommentSerializer

User = get_user_model()

class BookListViewTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.url = reverse('book-list')

    def test_get_book_list(self):
        book1 = Book.objects.create(
            title='Book One',
            description='Description One',
            genre='Genre One',
            author='Author One'
        )
        book2 = Book.objects.create(
            title='Book Two',
            description='Description Tw0',
            genre='Genre Two',
            author='Author Two'
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        serializer = BookSerializer(Book.objects.all(), many=True)
        self.assertEqual(response.data, serializer.data)

    def test_post_valid_book(self):
        valid_data = {
            "title": "New Book",
            "description": "New description",
            "author": "New author",
            "genre": "New genre"
        }
        response = self.client.post(self.url, data=valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

        created_book = Book.objects.first()
        self.assertEqual(created_book.title, valid_data["title"])
        self.assertEqual(created_book.description, valid_data["description"])
        self.assertEqual(created_book.author, valid_data["author"])
        self.assertEqual(created_book.genre, valid_data["genre"])

    def test_post_invalid_book(self):
        invalid_data = {
            "description": "Missing title and author",
            "genre": "Sci-Fi"
        }
        response = self.client.post(self.url, data=invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

class ProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user, bio='initial bio')

        self.url = reverse('profile')

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProfileSerializer(self.profile)
        self.assertEqual(response.data, serializer.data)

    def test_get_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHENTICATED)

    def test_patch_profile_valid(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {'bio': 'Updated bio'}
        response = self.client.patch(self.url, data=updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, updated_data['bio'])

    def test_patch_profile_invalid(self):
        self.client.force_authenicate(user=self.user)
        invalid_data = {'bio': 'x' * 101}
        response = self.client.patch(self.url, data=invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AddFavouriteBookViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(
            title='Test book',
            description='Test description',
            genre='Test genre',
            author='Test author'
        )

        if not hasattr(self.user, 'profile'):
            self.profile = Profile.objects.create(user=self.user, bio='Test bio')
        else:
            self.profile = self.user.profile

            self.url = reverse('add-favourite-book', kwargs={'book_id: self.book.id'})

    def test_add_favourite_book_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Book added to favourites.')
        self.assertTrue(self.profile.favourite_books.filter(pk=self.book.pk).exists())

    def test_add_favourite_book_already_added(self):
        self.client.force_authenticate(user=self.user)
        self.profile.favourite_books.add(self.book)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Book is already in favourites.')

    def test_add_favourite_book_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostListCreateViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.following_user = User.objects.create_user(username='following', password='testpass')
        self.not_following_user = User.objects.create_user(username='notfollowed', password='testpass')
        self.user.following.add(self.following_user)

        self.followed_post = Post.objects.create(
            author=self.following_user,
            content="Post from followed user"
        )
        self.not_following_post = Post.objects.create(
            author=self.not_following_user,
            content="Post from not followed user"
        )
        self.url = reverse('post-list-create')

    def test_get_posts(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PostSerializer([self.followed_post], many=True)
        self.assertEqual(response.data, serializer.data)

    def test_post_valid(self):
        self.client.force_authenticate(user=self.user)
        valid_data = {
            "content": "This is a new post"
        }

        response = self.client.post(self.url, data=valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_post = Post.objects.get(id=response.data['id'])
        self.assertEqual(created_post.author, self.user)
        self.assertEqual(created_post.content, valid_data["content"])

    def test_post_invalid(self):
        self.client.force_authenticate(user=self.user)
        invalid_data = {}
        response = self.client.post(self.url, data=invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FollowUserViewTests(APITestCase):
    def setUp(self):
        self.follower = User.objects.create_user(username='follower', password='testpass')
        self.target = User.objects.create_user(username='target', password='testpass')

        if not hasattr(self.follower, 'profile'):
            self.follower.profile = Profile.objects.create(user=self.follower)

        if not hasattr(self.target, 'profile'):
            self.target.profile = Profile.objects.create(user=self.target)

        self.follow_url = reverse('follow-user', kwargs={'username': self.target.username})

        self.self_follow_url = reverse('follow-user', kwargs={'username': self.follower.username})

        self.nonexistent_url = reverse('follow-user', kwargs={'username', 'nonexistent'})

    def test_follow_user_seccess(self):
        self.client.force_authenticate(user=self.follower)
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'following')
        self.assertTrue(self.follower.profile.following.filter(pk=self.target.profile.pk).exists())

    def test_follow_user_self(self):
        self.client.force_authenticate(user=self.follower)
        response = self.client.post(self.self_follow_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), "You cannot follow yourself.")

    def test_follow_user_already_following(self):
        self.client.force_authenticate(user=self.follower)
        self.follower.profile.following.add(self.target.profile)
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message'), "Already following this user.")

    def test_follow_user_nonexistent(self):
        self.clicent.force_authenticate(user=self.follower)
        response = self.client.post(self.nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_user_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        
class NoificationListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass')

        self.notification1 = Notification.objects.create(
            recipient=self.user,
            sender=self.other_user,
            message="Test Notification"
        )

        self.notification2 = Notification.objects.create(
            recipient=self.user,
            sender=self.other_user,
            message="Test Notification"
        )

        self.notification3 = Notification.objects.create(
            recipient=self.other_user,
            sender=self.user,
            message="Other Notification"
        )

        self.url = reverse('notification-list')

    def test_get_notifications_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notifications = Notification.objects.filter(recipient=self.user)
        serializer = NotificationSerializer(notifications, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_notifications_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MessageListViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass')

        self.message1 = Message.objects.create(
            recipient=self.user,
            sender=self.other_user,
            message="Hello from other user"
        )

        self.message2 = Message.objects.create(
            recipient=self.user,
            sender=self.other_user,
            message="Another message"
        )

        self.message3 = Message.objects.create(
            recipient=self.other_user,
            sender=self.user,
            message="Message not for test user"
        )

        self.url = reverse('message-list')

    def test_get_messages_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        messages = Message.objects.filter(recipient=self.user)
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)


    def test_get_messages_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_message_valid(self):
        self.client.force_authenticate(user=self.user)
        valid_data = {
            "recipient": self.other_user.id,
            "message": "Hi, How are you?"
        }
        response = self.client.get(self.url, data=valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_message = Message.objects.get(id=response.data['id'])
        self.assertEqual(created_message.sender, self.user)
        self.assertEqual(created_message.recipient, self.other_user)
        self.assertEqual(created_message.message, valid_data["message"])

    def test_post_message_invalid(self):
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            "recipient": self.other_user.id,
        }
        response = self.client.post(self.url, data=invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_message_unauthenticated(self):
        self.client.force_authenticate(user=None)
        valid_data = {
            "recipient": self.other_user,
            "message": "Hi!"
        }
        response = self.client.post(self.url, data=valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DiscussionListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test title",
            decription="Test desciption",
            author="Test author",
            genre="Test genre"
        )

        self.discussion1 = Discussion.objects.create(
            book=self.book,
            title="Discussion One",
            created_by=self.user
        )
        self.discussion2 = Discussion.obejcts.create(
            book=self.book,
            title="Discussion Two",
            created_by=self.user
        )

        self.other_book = Book.objects.create(
            title="Other book",
            description="Another book",
            author="Other author",
            genre="Non-fiction"
        )
        self.discussion_other = Discussion.objects.create(
            book=self.other_book,
            title="Other discussion",
            created_by=self.user
        )

        self.url = reverse('discussion-list', kwargs={'book_id': self.book.id})

    def test_get_discussions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        discussions = Discussion.objects.filter(book=self.book)
        serializer = DiscussionSerializer(discussions, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_post_discussion_valid(self):
        valid_data = {
            "title": "New Discussion title"
        }
        response = self.client.post(self.url, data=valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_discussion = Discussion.objects.get(title="New Discussion title")
        self.assertEqual(new_discussion.book, self.book)
        self.assertEqual(new_discussion.created_by, self.user)

    def test_post_discussion_invalid(self):
        invalid_data = {}
        response = self.client.post(self.url, data=invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        




        


    