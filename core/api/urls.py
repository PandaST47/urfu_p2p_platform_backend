from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'codes', views.CodeViewSet, basename='code')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('posts/<int:post_id>/mark-resolved/', views.mark_post_resolved, name='mark_post_resolved'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('bookmarks/add/<int:post_id>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/remove/<int:post_id>/', views.remove_bookmark, name='remove_bookmark'),
    path('like/<str:target_type>/<int:target_id>/', views.add_like, name='add_like'),
    path('reviews/add/<int:user_id>/', views.add_review, name='add_review'),
    path('admin/reports/', views.admin_report_list, name='admin_report_list'),
    path('admin/reports/<int:report_id>/process/', views.process_report, name='process_report'),
    path('admin/warnings/create/<int:user_id>/', views.create_warning, name='create_warning'),
    path('admin/users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('admin/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('messages/unread/count/', views.unread_messages_count, name='unread_messages_count'),
]