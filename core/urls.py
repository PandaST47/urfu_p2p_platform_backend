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
    # API routes
    path('api/', include('core.api.urls')),
]