from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'  # Добавляем это в начало файла

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='posts')
router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'chats', views.ChatViewSet, basename='chats')
router.register(r'messages', views.MessageViewSet, basename='messages')
router.register(r'reports', views.ReportViewSet, basename='reports')
router.register(r'codes', views.CodeViewSet, basename='codes')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register, name='api-register'),
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('profile/<int:user_id>/', views.profile_view, name='api-profile'),
    path('profile/edit/', views.edit_profile, name='api-edit_profile'),
    path('posts/<int:post_id>/mark-resolved/', views.mark_post_resolved, name='api-mark_post_resolved'),
    path('bookmarks/', views.bookmark_list, name='api-bookmark_list'),
    path('bookmarks/add/<int:post_id>/', views.add_bookmark, name='api-add_bookmark'),
    path('bookmarks/remove/<int:post_id>/', views.remove_bookmark, name='api-remove_bookmark'),
    path('like/<str:target_type>/<int:target_id>/', views.add_like, name='api-add_like'),
    path('reviews/add/<int:user_id>/', views.add_review, name='api-add_review'),
    path('admin/reports/', views.admin_report_list, name='api-admin_report_list'),
    path('admin/reports/<int:report_id>/process/', views.process_report, name='api-process_report'),
    path('admin/warnings/create/<int:user_id>/', views.create_warning, name='api-create_warning'),
    path('admin/users/<int:user_id>/block/', views.block_user, name='api-block_user'),
    path('admin/users/<int:user_id>/ban/', views.ban_user, name='api-ban_user'),
    path('admin/users/', views.admin_user_list, name='api-admin_user_list'),
    path('messages/unread/count/', views.unread_messages_count, name='api-unread_messages_count'),
    path('rate-for-help/<int:user_id>/', views.rate_for_help, name='api-rate-for-help'),  # Убедись, что этот путь есть
]