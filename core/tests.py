from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Post, Chat, Message, Code, Report, Admin, UserWarning, Bookmark, Like, ProfileView

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
        # Создаём ProfileView для всех пользователей
        ProfileView.objects.create(user=self.user1, rating=0)
        ProfileView.objects.create(user=self.user2, rating=0)
        ProfileView.objects.create(user=self.admin_user, rating=0)
        self.admin = Admin.objects.create(user=self.admin_user)
        self.post = Post.objects.create(user=self.user1, title='Test Post', content='Content')
        self.chat = Chat.objects.create(user1=self.user1, user2=self.user2)

    def test_register(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@urfu.me',
            'password': 'test123'
        }
        response = self.client.post(reverse('api:api-register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)

    def test_login(self):
        data = {'email': 'user1@example.com', 'password': 'test123'}
        response = self.client.post(reverse('api:api-login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')

    def test_logout(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('api:api-logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'New Post', 'content': 'Content'}
        response = self.client.post(reverse('api:posts-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_mark_post_resolved(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('api:api-mark_post_resolved', args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_resolved)

    def test_create_chat(self):
        self.client.force_authenticate(user=self.user1)
        data = {'user2': self.user2.id}
        response = self.client.post(reverse('api:chats-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Existing chat
        self.assertEqual(Chat.objects.count(), 1)

    def test_send_message(self):
        self.client.force_authenticate(user=self.user1)
        data = {'chat': self.chat.id, 'content': 'Hello'}
        response = self.client.post(reverse('api:messages-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

    def test_unread_messages_count(self):
        Message.objects.create(chat=self.chat, sender=self.user2, receiver=self.user1, content='Hi')
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('api:api-unread_messages_count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_create_code(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'post': self.post.id,
            'code_content': 'print("Hello")',
            'language': 'python',
            'start_line': 1,
            'end_line': 1
        }
        response = self.client.post(reverse('api:codes-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Code.objects.count(), 1)

    def test_profile_view(self):
        response = self.client.get(reverse('api:api-profile', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'user1')

    def test_edit_profile(self):
        self.client.force_authenticate(user=self.user1)
        data = {'profile_img_url': 'https://example.com/image.jpg'}
        response = self.client.put(reverse('api:api-edit_profile'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.profile_img_url, 'https://example.com/image.jpg')

    def test_add_bookmark(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('api:api-add_bookmark', args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)

    def test_add_like(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('api:api-add_like', args=['post', self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 1)

    def test_create_report(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'reporting_target_type': 'post',
            'reporting_target_id': self.post.id,
            'report_description': 'Inappropriate content'
        }
        response = self.client.post(reverse('api:reports-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

    def test_admin_report_list(self):
        Report.objects.create(
            reporting_user=self.user1,
            reporting_target_type='post',
            reporting_target_id=self.post.id,
            report_description='Test report'
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('api:api-admin_report_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_process_report(self):
        report = Report.objects.create(
            reporting_user=self.user1,
            reporting_target_type='post',
            reporting_target_id=self.post.id,
            report_description='Test report'
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse('api:api-process_report', args=[report.id]),
            {'action': 'accept'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.status, 'resolved')

    def test_create_warning(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'reason': 'Inappropriate content'}
        response = self.client.post(
            reverse('api:api-create_warning', args=[self.user1.id]),
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
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('api:api-block_user', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_blocked)

    def test_ban_user(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('api:api-ban_user', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)

    def test_admin_user_list(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('api:api-admin_user_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


    def test_rate_for_help_success(self):
        self.client.force_authenticate(user=self.user1)
        initial_likes = self.user2.chat_help_likes_cnt
        initial_points = self.user2.profileview.total_points
        initial_rating = self.user2.profileview.rating
        
        response = self.client.post(reverse('api:api-rate-for-help', args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User rated for help')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.chat_help_likes_cnt, initial_likes + 1)
        self.user2.profileview.refresh_from_db()
        self.assertEqual(self.user2.profileview.total_points, initial_points + 2)
        self.assertEqual(self.user2.profileview.rating, round((initial_points + 2) * 0.25))

    def test_rate_for_help_self(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse('api:api-rate-for-help', args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Cannot rate yourself')
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.chat_help_likes_cnt, 0)  # Проверяем, что лайки не изменились

    def test_rate_for_help_no_chat(self):
        self.client.force_authenticate(user=self.user1)
        # Создаём нового пользователя без чата
        user3 = User.objects.create_user(username='user3', email='user3@example.com', password='test123', role='user')
        ProfileView.objects.create(user=user3, rating=0)
        response = self.client.post(reverse('api:api-rate-for-help', args=[user3.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'You must have a chat with this user to rate them')
        user3.refresh_from_db()
        self.assertEqual(user3.chat_help_likes_cnt, 0)

    def test_rate_for_help_rating_limit(self):
        self.client.force_authenticate(user=self.user1)
        # Устанавливаем максимальные баллы (60), чтобы проверить лимит
        profile_view = self.user2.profileview
        profile_view.total_points = 60
        profile_view.save()
        initial_rating = profile_view.rating  # Должно быть 15
        
        response = self.client.post(reverse('api:api-rate-for-help', args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user2.profileview.refresh_from_db()
        self.assertEqual(self.user2.profileview.total_points, 60)  # Лимит не превышен
        self.assertEqual(self.user2.profileview.rating, 15)  # Рейтинг не превышает 15