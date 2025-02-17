from django.test import TestCase
from django.utils import timezone
import time
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Profile, Book, CustomUser, ReadingProgress, Post, Notification


User = get_user_model()

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = Profile.objects.get(user=self.user)
        
        self.book1 = Book.objects.create(title='Book 1', author='Author 1')
        self.book2 = Book.objects.create(title='Book 2', author='Author 2')
        self.book3 = Book.objects.create(title='Book 3', author='Author 3')

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.user.name, 'Test User')
        self.assertEqual(self.profile.bio, 'Test Bio')
        self.assertEqual(isinstance(self.profile, Profile))

        self.assertEqual(str(self.profile), self.profile.name)

    def profile_required_fields(self):
        with self.assertRaises(ValidationError):
            Profile.objects.create(user=self.user, name='')

    def test_m2m_relationships_for_books(self):

        self.profile.favourite_books.add(self.book1)
        self.profile.read_books.add(self.book2)
        self.profile.want_to_read_books.add(self.book3)
        self.profile.disliked_books.add(self.book1)

        self.assertEqual(self.profile.favourite_books.count(), 1)
        self.assertEqual(self.profile.read_books.count(), 1)
        self.assertEqual(self.profile.want_to_read_books.count(), 1)
        self.assertEqual(self.profile.disliked_books.count(), 1)

        self.assertIn(self.profile, self.book1.fans.all())
        self.assertIn(self.profile, self.book2.done.all())
        self.assertIn(self.profile, self.book3.wish.all())
        self.assertIn(self.profile, self.book1.haters.all())

    def test_follow_relationships(self):

        user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
        profile2 = Profile.objects.create(user=user2, name='Test User 2')

        self.profile.following.add(profile2)
        profile2.followers.add(self.profile)

        self.assertEqual(self.profile.following.count(), 1)
        self.assertEqual(profile2.followers.count(), 2)
        self.assertEqual(profile2.following.count(), 0)
        self.assertEqual(self.profile.followers.count(), 0)

        self.assertIn(profile2, self.profile.following.all())
        self.assertIn(self.profile, profile2.followed_by.all())

    def test_optional_fields(self):
        profile = Profile.objects.create(
            user=User.objects.create_user(username='empty user'),
            name='Empty User'
        )
        self.assertEqual(profile.photo, None)
        self.assertEqual(profile.bio, None)

    def test_max_length_constraints(self):
        max_length_name = self.profile._meta.get_field('name').max_length
        self.assertEqual(max_length_name, 100)

        max_length_bio = self.profile._meta.get_field('bio').max_length
        self.assertEqual(max_length_bio, 500)

    def test_duplicate_user_profile(self):
        """Тест на уникальность связи с пользователем"""
        with self.assertRaises(Exception):
            # Используем CustomUser вместо User
            Profile.objects.create(user=self.user, name='Duplicate Profile')

    def test_optional_fields(self):
        """Тестирование необязательных полей"""
        # Создаём пользователя через CustomUser
        user2 = CustomUser.objects.create_user(username='emptyuser')
        profile = Profile.objects.create(
            user=user2,
            name='Empty User'
        )
        self.assertEqual(profile.photo, None)
        self.assertEqual(profile.bio, None)


class BookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tetsuser', password='testpass')

    def create_book(self, **kwargs):
        defaults = {
            'title': 'Test Book',
            'description': 'A test book description',
            'author': 'Test author'
        }
        defaults.update(kwargs)
        return Book.objects.create(**defaults)
    
    def test_str_method_returns_title(self):
        title = 'Sample Book'
        book = self.create_book(title=title)
        self.assertEqual(str(book), title)

    def test_default_genre_is_unknown(self):
        book = self.create_book()
        self.assertEqual(book.genre, 'Unknown')

    def test_created_at_auto_set(self):
        book = self.create_book()
        self.assertIsNotNone(book.created_at)
        self.assertEqual((timezone.now() - book.created_at).total_seconds(), 1)

    def test_uploaded_at_auto_set(self):
        book = self.create_book(uploaded_by=self.user)
        self.assertIsNotNone(book.uploaded_at)
        self.assertLessEqual((timezone.now() - book.uploaded_at).total_seconds(), 1)

    def test_default_ratings_is_zero(self):
        book = self.create_book()
        self.assertEqual(book.ratings, 0)

    def test_cover_field_allows_blank_and_null(self):
        book = self.create_book()
        self.assertFalse(book.cover)

        temp_image = SimpleUploadedFile(
            "test_cover.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        book.cover = temp_image
        book.save()
        self.assertTrue(book.cover)

    def test_file_field_allows_blank_and_null(self):
        book = self.create_book()
        self.assertFalse(book.file)

        temp_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        book.file = temp_file
        book.save()
        self.assertTrue(book.file)


class ReadingProgressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.book = Book.objects.create(
            title='Test Book',
            description='Test Description',
            author='Test Author'
        )

    def test_default_current_page(self):
        progress = ReadingProgress.objects.create(user=self.user, book=self.book)
        self.assertEqual(progress.current_page, 1)

    def test_last_accessed_auto_now(self):
        progress = ReadingProgress.objects.create(user=self.user, book=self.book)
        self.assertIsNotNone(progress.last_accessed)
        now = timezone.now()
        self.assertLessEqual((now - progress.last_accessed).total_seconds(), 1)

    def test_last_accessed_updated_on_save(self):
        progress = ReadingProgress.objects.create(user=self.user, book=self.book)
        original_last_accessed = progress.last_accessed
        time.sleep(1)
        progress.current_page = 10
        progress.save()
        progress.refresh_from_db

        self.assertGreater(progress.last_accessed, original_last_accessed)

    def test_foreign_keys_relationships(self):
        progress = ReadingProgress.objects.create(user=self.user, book=self.book, current_page=50)
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.book, self.book)
        self.assertIn(progress, self.user.readingprogress_set.all())
        self.assertIn(progress, self.book.readingprogress_set.all())


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testname', password='testpass')

    def test_str_method_returns_correct_format(self):
        content = 'This is an example of a content which are longer than 30 symbols for testing'
        post = Post.objects.create(author=self.user, content=content)
        expected_str = f'{self.user.username} : {content[:30]}'
        self.assertEqual(str(post), expected_str)

    def test_created_at_default_value(self):
        post = Post.objects.create(author=self.user, content="Test content")
        self.assertIsNotNone(post.created_at)
        now_time = timezone.now()
        self.assertLessEqual((now_time - post.created_at).total_seconds(), 1)


class NotificationModelTets(TestCase):
    def setUp(self):
        self.recipient = User.objects.user_create(username='recipient', password='testpass')
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.post = Post.objects.create('The content of the post for the test')

    def test_str_method_returns_correct_string(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            post=self.post,
            message="Test message"
        )
        expected_str = f'Notification to {self.recipient.username} from {self.sender.username}'
        self.assertEqual(str(notification), expected_str)

    def test_default_is_read_is_false(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            post=self.post,
            messsage="Test message"
        )
        self.assertFalse(notification.is_read)

    def test_created_at_auto_set(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            post=self.post,
            message="Test message"
        )
        self.assertIsNotNone(notification.created_at)
        now_time = timezone.now()
        self.assertLessEqual((now_time - notification.created_at).total_seconds(), 1)

    def test_recipient_notifications_related_name(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            post=self.post,
            message="Test message"
        )
        self.assertIn(notification, self.recipient.notifications.all())

    def test_post_field_can_be_null(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            post=self.post,
            messsge="Test message"
        )
        self.assertIsNone(notification.post)