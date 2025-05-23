from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Post, Chat, Message, Code, Report, Admin, UserWarning, Bookmark, Like

User = get_user_model()

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='test123', role='user'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='test123', role='user'
        )
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@example.com', password='test123', role='admin'
        )
        self.admin = Admin.objects.create(user=self.admin_user)
        self.post = Post.objects.create(user=self.user1, title='Test Post', content='Content')
        self.chat = Chat.objects.create(user1=self.user1, user2=self.user2)

    def test_register(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'test123'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)

    def test_login(self):
        data = {'email': 'user1@example.com', 'password': 'test123'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')

    def test_logout(self):
        self.client.login(email='user1@example.com', password='test123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        self.client.login(email='user1@example.com', password='test123')
        data = {'title': 'New Post', 'content': 'Content'}
        response = self.client.post(reverse('post-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_mark_post_resolved(self):
        self.client.login(email='user1@example.com', password='test123')
        response = self.client.post(reverse('mark_post_resolved', args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_resolved)

    def test_create_chat(self):
        self.client.login(email='user1@example.com', password='test123')
        data = {'user2': self.user2.id}
        response = self.client.post(reverse('chat-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Existing chat
        self.assertEqual(Chat.objects.count(), 1)

    def test_send_message(self):
        self.client.login(email='user1@example.com', password='test123')
        data = {'chat': self.chat.id, 'content': 'Hello'}
        response = self.client.post(reverse('message-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

    def test_unread_messages_count(self):
        Message.objects.create(chat=self.chat, sender=self.user2, receiver=self.user1, content='Hi')
        self.client.login(email='user1@example.com', password='test123')
        response = self.client.get(reverse('unread_messages_count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_create_code(self):
        self.client.login(email='user1@example.com', password='test123')
        data = {
            'post': self.post.id,
            'code_content': 'print("Hello")',
            'language': 'python',
            'start_line': 1,
            'end_line': 1
        }
        response = self.client.post(reverse('code-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Code.objects.count(), 1)

    def test_profile_view(self):
        response = self.client.get(reverse('profile', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'user1')

    def test_edit_profile(self):
        self.client.login(email='user1@example.com', password='test123')
        data = {'profile_img_url': 'https://example.com/image.jpg'}
        response = self.client.put(reverse('edit_profile'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.profile_img_url, 'https://example.com/image.jpg')

    def test_add_bookmark(self):
        self.client.login(email='user1@example.com', password='test123')
        response = self.client.post(reverse('add_bookmark', args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)

    def test_add_like(self):
        self.client.login(email='user1@example.com', password='test123')
        response = self.client.post(reverse('add_like', args=['post', self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 1)

    def test_create_report(self):
        self.client.login(email='user1@example.com', password='test123')
        data = {
            'reporting_target_type': 'post',
            'reporting_target_id': self.post.id,
            'report_description': 'Inappropriate content'
        }
        response = self.client.post(reverse('report-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

    def test_admin_report_list(self):
        Report.objects.create(
            reporting_user=self.user1,
            reporting_target_type='post',
            reporting_target_id=self.post.id,
            report_description='Test report'
        )
        self.client.login(email='admin@example.com', password='test123')
        response = self.client.get(reverse('admin_report_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_process_report(self):
        report = Report.objects.create(
            reporting_user=self.user1,
            reporting_target_type='post',
            reporting_target_id=self.post.id,
            report_description='Test report'
        )
        self.client.login(email='admin@example.com', password='test123')
        response = self.client.post(
            reverse('process_report', args=[report.id]),
            {'action': 'accept'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.status, 'resolved')

    def test_create_warning(self):
        self.client.login(email='admin@example.com', password='test123')
        data = {'reason': 'Inappropriate content'}
        response = self.client.post(
            reverse('create_warning', args=[self.user1.id]),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserWarning.objects.count(), 1)

    def test_block_user(self):
        for _ in range(3):
            UserWarning.objects.create(
                user=self.user1,
                admin=self.admin,
                reason='Test warning',
                is_accepted=True
            )
        self.client.login(email='admin@example.com', password='test123')
        response = self.client.post(reverse('block_user', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_blocked)

    def test_ban_user(self):
        self.client.login(email='admin@example.com', password='test123')
        response = self.client.post(reverse('ban_user', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)

    def test_admin_user_list(self):
        self.client.login(email='admin@example.com', password='test123')
        response = self.client.get(reverse('admin_user_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)