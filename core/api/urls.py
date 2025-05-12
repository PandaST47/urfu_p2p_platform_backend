from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views
#api/urls.py
# Создаем роутеры для ViewSet
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'reports', views.ReportViewSet, basename='report')

urlpatterns = [
    # Административная панель Django
    path('admin/', admin.site.urls),

    # Корневой роутер DRF 
     path('', include(router.urls)),

    # Аутентификация
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),

    # Профиль
    path('api/profile/<int:user_id>/', views.profile_view, name='profile'),
    path('api/profile/edit/', views.edit_profile, name='edit_profile'),

    # Посты
    path('api/posts/<int:post_id>/mark-resolved/', views.mark_post_resolved, name='mark_post_resolved'),

    # Закладки
    path('api/bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('api/bookmarks/add/<int:post_id>/', views.add_bookmark, name='add_bookmark'),
    path('api/bookmarks/remove/<int:post_id>/', views.remove_bookmark, name='remove_bookmark'),

    # Лайки
    path('api/like/<str:target_type>/<int:target_id>/', views.add_like, name='add_like'),

    # Отзывы
    path('api/reviews/add/<int:user_id>/', views.add_review, name='add_review'),

    # Административные функции
    path('api/admin/reports/', views.admin_report_list, name='admin_report_list'),
    path('api/admin/reports/<int:report_id>/process/', views.process_report, name='process_report'),
    path('api/admin/warnings/create/<int:user_id>/', views.create_warning, name='create_warning'),
    path('api/admin/users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('api/admin/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
]