# core/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CourseViewSet, 
    ChatViewSet, MessageViewSet, 
    ReportViewSet
)
from . import views

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),

    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профиль
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Посты
    path('posts/<int:post_id>/mark-resolved/', views.mark_post_resolved, name='mark_post_resolved'),

    # Закладки
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('bookmarks/add/<int:post_id>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/remove/<int:post_id>/', views.remove_bookmark, name='remove_bookmark'),

    # Лайки
    path('like/<str:target_type>/<int:target_id>/', views.add_like, name='add_like'),

    # Отзывы
    path('reviews/add/<int:user_id>/', views.add_review, name='add_review'),

    # Административные функции
    path('admin/reports/', views.admin_report_list, name='admin_report_list'),
    path('admin/reports/<int:report_id>/process/', views.process_report, name='process_report'),
    path('admin/warnings/create/<int:user_id>/', views.create_warning, name='create_warning'),
    path('admin/users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('admin/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
]