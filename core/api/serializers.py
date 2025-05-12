from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    User, Post, Comment, Course, Chat, 
    Message, Code, CodeComment, Bookmark, 
    Report, Review, UserWarning, Admin
)

#api/serializers.py
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile_img_url',
            'role', 'total_questions', 'total_answers',
            'is_blocked', 'post_likes_cnt', 'comment_likes_cnt'
        ]
        read_only_fields = ['id', 'is_blocked']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'title', 'content', 
            'image_url', 'code', 'likes_count', 
            'created_at', 'is_resolved'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'content', 
            'code', 'image_url', 'likes_count', 
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
class CourseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'user', 'title', 'image_url', 
            'content', 'code', 'likes_count', 
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
class ChatSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user1', 'user2', 'chat_likes_cnt', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'chat', 'sender', 'receiver', 
            'content', 'image_url', 'is_read', 
            'is_code', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at']

class CodeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Code
        fields = [
            'id', 'post', 'comment', 'user', 
            'code_content', 'message', 'language', 
            'start_line', 'end_line', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class CodeCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CodeComment
        fields = [
            'id', 'code', 'user', 'message', 
            'comm_content', 'start_line', 
            'end_line', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class BookmarkSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post']
        read_only_fields = ['id']

class ReportSerializer(serializers.ModelSerializer):
    reporting_user = UserSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'reporting_user', 'reporting_target_type', 
            'reporting_target_id', 'report_description', 
            'created_at', 'status', 'processed_by', 
            'resolved_at'
        ]
        read_only_fields = ['id', 'created_at', 'status', 'processed_by', 'resolved_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    target_user = UserSerializer(read_only=True)
        
    class Meta:
        model = Review
        fields = ['id', 'user', 'target_user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class UserWarningSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    admin = serializers.SerializerMethodField()

    class Meta:
        model = UserWarning
        fields = ['id', 'user', 'admin', 'reason', 'created_at', 'is_accepted']
        read_only_fields = ['id', 'created_at']

    def get_admin(self, obj):
        return {
            'id': obj.admin.id,
            'username': obj.admin.user.username
        }