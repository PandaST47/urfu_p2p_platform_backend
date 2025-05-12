from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.utils import timezone
#api/views.py
from .models import (
    User, Post, Comment, Course, Chat, 
    Message, Code, CodeComment, Bookmark, 
    Report, Review, UserWarning, Like
)
from .serializers import (
    UserSerializer, PostSerializer, CommentSerializer, 
    CourseSerializer, ChatSerializer, MessageSerializer, 
    CodeSerializer, CodeCommentSerializer, BookmarkSerializer, 
    ReportSerializer, ReviewSerializer, UserWarningSerializer
)

# Custom Pagination
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(username=email, password=password)
    
    if user:
        login(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Successfully logged out'})

# Post Views
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Фильтрация постов с возможностью поиска и сортировки
        queryset = Post.objects.all()
        search_query = self.request.query_params.get('search', None)
        resolved = self.request.query_params.get('resolved', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            )
        
        if resolved is not None:
            queryset = queryset.filter(is_resolved=(resolved == 'true'))
        
        return queryset.order_by('-created_at')

@api_view(['POST'])
def mark_post_resolved(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Проверка, что текущий пользователь - автор поста
    if post.user != request.user:
        return Response({'error': 'Only post author can mark as resolved'}, 
                        status=status.HTTP_403_FORBIDDEN)
    
    post.is_resolved = True
    post.save()
    return Response(PostSerializer(post).data)

# Course Views
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Фильтрация курсов с возможностью поиска
        queryset = Course.objects.all()
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')

# Chat Views
class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Показываем только чаты текущего пользователя
        return Chat.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

    def create(self, request):
        # Создание чата между двумя пользователями
        user2_id = request.data.get('user2')
        user2 = get_object_or_404(User, id=user2_id)
        
        # Проверка, что чат еще не существует
        existing_chat = Chat.objects.filter(
            (Q(user1=request.user, user2=user2) | 
             Q(user1=user2, user2=request.user))
        ).first()
        
        if existing_chat:
            serializer = self.get_serializer(existing_chat)
            return Response(serializer.data)
        
        chat = Chat.objects.create(user1=request.user, user2=user2)
        serializer = self.get_serializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Message Views
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat', None)
        if chat_id:
            return Message.objects.filter(chat_id=chat_id).order_by('created_at')
        return Message.objects.none()

    def perform_create(self, serializer):
        chat_id = self.request.data.get('chat')
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Проверка, что пользователь участник чата
        if chat.user1 != self.request.user and chat.user2 != self.request.user:
            raise PermissionDenied()
        
        receiver = chat.user1 if chat.user2 == self.request.user else chat.user2
        
        serializer.save(
            sender=self.request.user, 
            receiver=receiver,
            chat=chat
        )

# Bookmark Views
@api_view(['POST'])
def add_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user, 
        post=post
    )
    return Response(status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def remove_bookmark(request, post_id):
    bookmark = get_object_or_404(Bookmark, user=request.user, post_id=post_id)
    bookmark.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    serializer = BookmarkSerializer(bookmarks, many=True)
    return Response(serializer.data)

# Likes Views
@api_view(['POST'])
def add_like(request, target_type, target_id):
    # Проверка валидности target_type
    valid_types = ['post', 'comment', 'course', 'chat']
    if target_type not in valid_types:
        return Response({'error': 'Invalid target type'}, status=status.HTTP_400_BAD_REQUEST)

    # Создание лайка
    like, created = Like.objects.get_or_create(
        user=request.user,
        target_type=target_type,
        target_id=target_id
    )

    # Обновление счетчика лайков в соответствующей модели
    if created:
        if target_type == 'post':
            post = get_object_or_404(Post, id=target_id)
            post.likes_count += 1
            post.save()
        elif target_type == 'comment':
            comment = get_object_or_404(Comment, id=target_id)
            comment.likes_count += 1
            comment.save()
        elif target_type == 'course':
            course = get_object_or_404(Course, id=target_id)
            course.likes_count += 1
            course.save()
        # для чата особая логика, так как лайки считаются в модели Chat

    return Response(status=status.HTTP_201_CREATED)

# Report Views
class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporting_user=self.request.user)

    def get_queryset(self):
        # Для администраторов - все жалобы, для обычных пользователей - только их собственные
        if self.request.user.role == 'admin':
            return Report.objects.filter(status='pending')
        return Report.objects.filter(reporting_user=self.request.user)

# Review Views
@api_view(['POST'])
def add_review(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            user=request.user, 
            target_user=target_user
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Profile Views
@api_view(['GET'])
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Получаем дополнительную информацию о пользователе
    posts = Post.objects.filter(user=user)
    courses = Course.objects.filter(user=user)
    reviews = Review.objects.filter(target_user=user)

    profile_data = {
        'user': UserSerializer(user).data,
        'posts_count': posts.count(),
        'courses_count': courses.count(),
        'reviews': ReviewSerializer(reviews, many=True).data
    }

    return Response(profile_data)

@api_view(['PUT'])
def edit_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Admin Views
@api_view(['GET'])
def admin_report_list(request):
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    reports = Report.objects.filter(status='pending')
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def process_report(request, report_id):
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    report = get_object_or_404(Report, id=report_id)
    
    # Обработка жалобы
    action = request.data.get('action')  # 'accept' или 'reject'
    
    report.status = 'resolved' if action == 'accept' else 'rejected'
    report.processed_by = request.user
    report.resolved_at = timezone.now()
    report.save()

    return Response(ReportSerializer(report).data)

@api_view(['POST'])
def create_warning(request, user_id):
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user = get_object_or_404(User, id=user_id)
    admin = get_object_or_404(Admin, user=request.user)
    
    warning = UserWarning.objects.create(
        user=user, 
        admin=admin, 
        reason=request.data.get('reason', '')
    )

    return Response(UserWarningSerializer(warning).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def block_user(request, user_id):
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user = get_object_or_404(User, id=user_id)
    
    # Проверяем количество предупреждений
    warnings_count = UserWarning.objects.filter(user=user, is_accepted=True).count()
    
    if warnings_count >= 3:
        user.is_blocked = True
        user.save()
        return Response({'message': 'User blocked'})
    
    return Response({'error': 'Not enough warnings to block'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ban_user(request, user_id):
    if request.user.role != 'admin':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user = get_object_or_404(User, id=user_id)
    
    # Полный бан пользователя
    user.is_active = False
    user.save()

    return Response({'message': 'User banned'})