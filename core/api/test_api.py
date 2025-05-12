from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Post, Course, Chat, Message, Bookmark, Like

User = get_user_model()

class APITestCase(TestCase):
    def setUp(self):
        # Создание тестовых пользователей
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

    # Клиент для аутентификации
    self.client = APIClient()
    self.client.force_authenticate(user=self.user1)

def test_create_post(self):
    """Тест создания поста"""
    data = {
        'title': 'Test Post',
        'content': 'This is a test post content',
        'code': 'print("Hello World")'
    }
    response = self.client.post('/api/posts/', data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['title'], data['title'])
    self.assertEqual(response.data['user']['username'], self.user1.username)

def test_create_course(self):
    """Тест создания курса"""
    data = {
        'title': 'Python for Beginners',
        'content': 'Learn Python programming',
        'image_url': 'http://example.com/image.jpg'
    }
    response = self.client.post('/api/courses/', data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['title'], data['title'])

def test_create_chat(self):
    """Тест создания чата между пользователями"""
    response = self.client.post('/api/chats/', {'user2': self.user2.id})
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertTrue('id' in response.data)

def test_add_bookmark(self):
    """Тест добавления закладки"""
    # Сначала создаем пост
    post = Post.objects.create(user=self.user1, title='Bookmark Test', content='Test')
    
    response = self.client.post(f'/api/bookmarks/add/{post.id}/')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_like_post(self):
    """Тест лайка поста"""
    # Создаем пост
    post = Post.objects.create(user=self.user1, title='Like Test', content='Test')
    
    response = self.client.post(f'/api/like/post/{post.id}/')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_mark_post_resolved(self):
    """Тест пометки поста как решенного"""
    post = Post.objects.create(user=self.user1, title='Resolved Test', content='Test')
    
    response = self.client.post(f'/api/posts/{post.id}/mark-resolved/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertTrue(response.data['is_resolved'])

def test_profile_view(self):
    """Тест просмотра профиля"""
    response = self.client.get(f'/api/profile/{self.user1.id}/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['user']['username'], self.user1.username)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='testpass123'
        )
    
def test_user_registration(self):
    """Тест регистрации пользователя"""
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpassword123'
    }
    response = self.client.post('/api/register/', data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_user_login(self):
    """Тест входа пользователя"""
    data = {
        'email': 'auth@example.com',
        'password': 'testpass123'
    }
    response = self.client.post('/api/login/', data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertTrue('id' in response.data)


""" Тесты для админа """

class AdminFunctionalityTests(TestCase):
    def setUp(self):
        # Создание администратора
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
    self.client = APIClient()
    self.client.force_authenticate(user=self.admin_user)

def test_create_user_warning(self):
    """Тест создания предупреждения пользователю"""
    user_to_warn = User.objects.create_user(
        username='warnuser', 
        email='warn@example.com', 
        password='warnpass123'
    )
    response = self.client.post(f'/api/admin/warnings/create/{user_to_warn.id}/', {
        'reason': 'Test warning'
    })
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_block_user(self):
    """Тест блокировки пользователя"""
    user_to_block = User.objects.create_user(
        username='blockuser', 
        email='block@example.com', 
        password='blockpass123'
    )
    # Создаем предупреждения
    for _ in range(3):
        UserWarning.objects.create(
            user=user_to_block, 
            admin=Admin.objects.create(user=self.admin_user),
            reason='Test warning',
            is_accepted=True
        )
    
    response = self.client.post(f'/api/admin/users/{user_to_block.id}/block/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    user_to_block.refresh_from_db()
    self.assertTrue(user_to_block.is_blocked)


    