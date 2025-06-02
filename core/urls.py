from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    # HTML routes
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/mark-resolved/', views.mark_post_resolved, name='mark_post_resolved'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chats/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('like/<str:target_type>/<int:target_id>/', views.add_like, name='add_like'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('bookmarks/add/<int:post_id>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/remove/<int:post_id>/', views.remove_bookmark, name='remove_bookmark'),
    path('reviews/add/<int:user_id>/', views.add_review, name='add_review'),
    path('report/<str:target_type>/<int:target_id>/', views.create_report, name='create_report'),
    path('admin/reports/', views.admin_report_list, name='admin_report_list'),
    path('admin/reports/<int:report_id>/process/', views.process_report, name='process_report'),
    path('admin/warnings/create/<int:user_id>/', views.create_warning, name='create_warning'),
    path('warnings/<int:warning_id>/respond/', views.respond_to_warning, name='respond_to_warning'),
    path('admin/users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('admin/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('search/posts/', views.search_posts, name='search_posts'),
    path('search/courses/', views.search_courses, name='search_courses'),
    # API routes
    path('api/', include('core.api.urls')),
]