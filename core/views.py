from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import User, Post, Comment, Course, Chat, Message, Code, CodeComment, Like, Bookmark, Report, Review, UserWarning, Admin, AdminAction
from core.api.serializers import PostSerializer, CourseSerializer, ChatSerializer, MessageSerializer, CodeSerializer, CodeCommentSerializer, ReportSerializer, ReviewSerializer, UserWarningSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# Главная страница
def index(request):
    """Главная страница с лентой постов"""
    posts = Post.objects.all().order_by('-created_at')[:10]  # Первые 10 постов
    return render(request, 'core/index.html', {'posts': posts})

# Аутентификация
def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email.endswith('@urfu.me'):  # Проверка почты УрФУ
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            return redirect('core:index')
        else:
            return render(request, 'core/register.html', {'error': 'Use @urfu.me email'})
    return render(request, 'core/register.html')

def login_view(request):
    """Страница входа"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:index')
        return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/login.html')

def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    return redirect('core:index')

# Профиль
@login_required
def profile_view(request, user_id):
    """Просмотр профиля пользователя"""
    user = get_object_or_404(User, id=user_id)
    if user.is_blocked and request.user != user:
        return render(request, 'core/profile.html', {'error': 'Profile is blocked'})
    
    posts = Post.objects.filter(user=user)
    courses = Course.objects.filter(user=user)
    reviews = Review.objects.filter(target_user=user)
    return render(request, 'core/profile.html', {
        'profile_user': user,
        'posts': posts,
        'courses': courses,
        'reviews': reviews
    })

@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user = request.user
        user.profile_img_url = request.POST.get('profile_img_url', user.profile_img_url)
        user.save()
        return redirect('core:profile', user_id=user.id)
    return render(request, 'core/edit_profile.html')

# Посты
def post_list(request):
    """Список постов"""
    search_query = request.GET.get('search', '')
    resolved = request.GET.get('resolved', None)
    posts = Post.objects.all()
    
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    if resolved is not None:
        posts = posts.filter(is_resolved=(resolved.lower() == 'true'))
    
    posts = posts.order_by('-created_at')
    return render(request, 'core/post_list.html', {'posts': posts})

@login_required
def create_post(request):
    """Создание нового поста"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image_url = request.POST.get('image_url', '')
        code = request.POST.get('code', '')
        post = Post.objects.create(
            user=request.user,
            title=title,
            content=content,
            image_url=image_url,
            code=code,
            is_resolved=False
        )
        return redirect('core:post_detail', post_id=post.id)
    return render(request, 'core/create_post.html')

def post_detail(request, post_id):
    """Детальный просмотр поста"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')
    return render(request, 'core/post_detail.html', {'post': post, 'comments': comments})

@login_required
def edit_post(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.image_url = request.POST.get('image_url', post.image_url)
        post.code = request.POST.get('code', post.code)
        post.save()
        return redirect('core:post_detail', post_id=post.id)
    return render(request, 'core/edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    """Удаление поста"""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('core:post_list')
    return render(request, 'core/delete_post.html', {'post': post})

@login_required
def mark_post_resolved(request, post_id):
    """Отметить пост как решённый"""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.is_resolved = True
        post.save()
        return redirect('core:post_detail', post_id=post.id)
    return render(request, 'core/mark_resolved.html', {'post': post})

@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту"""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        code = request.POST.get('code', '')
        image_url = request.POST.get('image_url', '')
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content,
            code=code,
            image_url=image_url
        )
        return redirect('core:post_detail', post_id=post.id)
    return render(request, 'core/add_comment.html', {'post': post})

@login_required
def edit_comment(request, comment_id):
    """Редактирование комментария"""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        comment.content = request.POST.get('content', comment.content)
        comment.code = request.POST.get('code', comment.code)
        comment.image_url = request.POST.get('image_url', comment.image_url)
        comment.save()
        return redirect('core:post_detail', post_id=comment.post.id)
    return render(request, 'core/edit_comment.html', {'comment': comment})

@login_required
def delete_comment(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    comment.delete()
    return redirect('core:post_detail', post_id=post_id)

# Курсы
def course_list(request):
    """Список курсов"""
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'core/course_list.html', {'courses': courses})

@login_required
def create_course(request):
    """Создание курса"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image_url = request.POST.get('image_url', '')
        code = request.POST.get('code', '')
        course = Course.objects.create(
            user=request.user,
            title=title,
            content=content,
            image_url=image_url,
            code=code
        )
        return redirect('core:course_detail', course_id=course.id)
    return render(request, 'core/create_course.html')

def course_detail(request, course_id):
    """Детальный просмотр курса"""
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'core/course_detail.html', {'course': course})

@login_required
def edit_course(request, course_id):
    """Редактирование курса"""
    course = get_object_or_404(Course, id=course_id, user=request.user)
    if request.method == 'POST':
        course.title = request.POST.get('title', course.title)
        course.content = request.POST.get('content', course.content)
        course.image_url = request.POST.get('image_url', course.image_url)
        course.code = request.POST.get('code', course.code)
        course.save()
        return redirect('core:course_detail', course_id=course.id)
    return render(request, 'core/edit_course.html', {'course': course})

@login_required
def delete_course(request, course_id):
    """Удаление курса"""
    course = get_object_or_404(Course, id=course_id, user=request.user)
    course.delete()
    return redirect('core:course_list')

# Чаты
@login_required
def chat_list(request):
    """Список чатов"""
    chats = Chat.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-created_at')
    return render(request, 'core/chat_list.html', {'chats': chats})

@login_required
def start_chat(request, user_id):
    """Начать чат с пользователем"""
    user2 = get_object_or_404(User, id=user_id)
    if request.user.is_blocked or user2.is_blocked:
        return render(request, 'core/start_chat.html', {'error': 'Blocked users cannot create chats'})
    
    existing_chat = Chat.objects.filter(
        (Q(user1=request.user, user2=user2) | Q(user1=user2, user2=request.user))
    ).first()
    
    if existing_chat:
        return redirect('core:chat_detail', chat_id=existing_chat.id)
    
    chat = Chat.objects.create(user1=request.user, user2=user2)
    return redirect('core:chat_detail', chat_id=chat.id)

@login_required
def chat_detail(request, chat_id):
    """Детальный просмотр чата"""
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.user1 != request.user and chat.user2 != request.user:
        return HttpResponse("Access denied", status=403)
    
    messages = chat.messages.all().order_by('created_at')
    return render(request, 'core/chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def send_message(request, chat_id):
    """Отправка сообщения в чат"""
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.user1 != request.user and chat.user2 != request.user:
        return HttpResponse("Access denied", status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image_url = request.POST.get('image_url', '')
        is_code = request.POST.get('is_code', 'false') == 'true'
        receiver = chat.user1 if chat.user2 == request.user else chat.user2
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            receiver=receiver,
            content=content,
            image_url=image_url,
            is_code=is_code
        )
        if is_code:
            code_content = request.POST.get('code_content', content)
            language = request.POST.get('language', 'python')
            Code.objects.create(
                message=message,
                user=request.user,
                code_content=code_content,
                language=language,
                start_line=1,
                end_line=1
            )
        return redirect('core:chat_detail', chat_id=chat.id)
    return render(request, 'core/send_message.html', {'chat': chat})

# Лайки
@login_required
def add_like(request, target_type, target_id):
    """Добавление лайка"""
    valid_types = ['post', 'comment', 'course', 'chat']
    if target_type not in valid_types:
        return JsonResponse({'error': 'Invalid target type'}, status=400)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        target_type=target_type,
        target_id=target_id
    )
    if created:
        if target_type == 'post':
            obj = get_object_or_404(Post, id=target_id)
            obj.likes_count += 1
            obj.save()
        elif target_type == 'comment':
            obj = get_object_or_404(Comment, id=target_id)
            obj.likes_count += 1
            obj.save()
        elif target_type == 'course':
            obj = get_object_or_404(Course, id=target_id)
            obj.likes_count += 1
            obj.save()
        elif target_type == 'chat':
            obj = get_object_or_404(Chat, id=target_id)
            obj.chat_likes_cnt += 1
            obj.save()
    return JsonResponse({'status': 'success'})

# Закладки
@login_required
def bookmark_list(request):
    """Список закладок"""
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'core/bookmark_list.html', {'bookmarks': bookmarks})

@login_required
def add_bookmark(request, post_id):
    """Добавление закладки"""
    post = get_object_or_404(Post, id=post_id)
    Bookmark.objects.get_or_create(user=request.user, post=post)
    return redirect('core:bookmark_list')

@login_required
def remove_bookmark(request, post_id):
    """Удаление закладки"""
    bookmark = get_object_or_404(Bookmark, user=request.user, post_id=post_id)
    bookmark.delete()
    return redirect('core:bookmark_list')

# Отзывы
@login_required
def add_review(request, user_id):
    """Добавление отзыва о пользователе"""
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        Review.objects.create(user=request.user, target_user=target_user, content=content)
        return redirect('core:profile', user_id=user_id)
    return render(request, 'core/add_review.html', {'target_user': target_user})

# Жалобы
@login_required
def create_report(request, target_type, target_id):
    """Создание жалобы"""
    if request.method == 'POST':
        description = request.POST.get('report_description')
        Report.objects.create(
            reporting_user=request.user,
            reporting_target_type=target_type,
            reporting_target_id=target_id,
            report_description=description
        )
        return JsonResponse({'status': 'report created'})
    return render(request, 'core/create_report.html', {'target_type': target_type, 'target_id': target_id})

@login_required
def admin_report_list(request):
    """Список жалоб для администратора"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    reports = Report.objects.filter(status='pending')
    return render(request, 'core/admin_report_list.html', {'reports': reports})

@login_required
def process_report(request, report_id):
    """Обработка жалобы администратором"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        report.status = 'resolved' if action == 'accept' else 'rejected'
        report.processed_by = request.user
        report.resolved_at = timezone.now()
        report.save()
        
        admin = Admin.objects.filter(user=request.user).first()
        if admin:
            AdminAction.objects.create(
                admin=admin,
                action_type='report_processed',
                target_id=report.id,
                details=f"Report {report.id} {report.status} by {request.user.username}"
            )
        return redirect('core:admin_report_list')
    return render(request, 'core/process_report.html', {'report': report})

@login_required
def create_warning(request, user_id):
    """Создание предупреждения пользователю"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    admin = get_object_or_404(Admin, user=request.user)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        warning = UserWarning.objects.create(
            user=user,
            admin=admin,
            reason=reason,
            is_accepted=True
        )
        AdminAction.objects.create(
            admin=admin,
            action_type='warning_created',
            target_id=user.id,
            details=f"Warning issued to {user.username} by {request.user.username}"
        )
        return redirect('core:profile', user_id=user.id)
    return render(request, 'core/create_warning.html', {'target_user': user})

@login_required
def respond_to_warning(request, warning_id):
    """Ответ на предупреждение"""
    warning = get_object_or_404(UserWarning, id=warning_id, user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            warning.is_accepted = True
            warning.save()
            # Удаляем связанный контент, если это пост или курс
            if warning.reason.startswith('Post'):
                post_id = int(warning.reason.split()[-1])
                post = get_object_or_404(Post, id=post_id)
                post.delete()
            return redirect('core:profile', user_id=request.user.id)
        elif action == 'dispute':
            Report.objects.create(
                reporting_user=request.user,
                reporting_target_type='warning',
                reporting_target_id=warning.id,
                report_description='Disputing warning'
            )
            return redirect('core:profile', user_id=request.user.id)
    return render(request, 'core/respond_to_warning.html', {'warning': warning})

@login_required
def block_user(request, user_id):
    """Блокировка пользователя"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    warnings_count = UserWarning.objects.filter(user=user, is_accepted=True).count()
    if warnings_count >= 3:
        user.is_blocked = True
        user.save()
        admin = Admin.objects.filter(user=request.user).first()
        if admin:
            AdminAction.objects.create(
                admin=admin,
                action_type='user_blocked',
                target_id=user.id,
                details=f"User {user.username} blocked by {request.user.username}"
            )
        return redirect('core:profile', user_id=user.id)
    return render(request, 'core/block_user.html', {'target_user': user, 'warnings_count': warnings_count})

@login_required
def ban_user(request, user_id):
    """Бан пользователя"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    admin = Admin.objects.filter(user=request.user).first()
    if admin:
        AdminAction.objects.create(
            admin=admin,
            action_type='user_banned',
            target_id=user.id,
            details=f"User {user.username} banned by {request.user.username}"
        )
    return redirect('core:profile', user_id=user.id)

# Поиск
def search_posts(request):
    """Поиск постов"""
    query = request.GET.get('query', '')
    posts = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    return render(request, 'core/post_list.html', {'posts': posts})

def search_courses(request):
    """Поиск курсов"""
    query = request.GET.get('query', '')
    courses = Course.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    return render(request, 'core/course_list.html', {'courses': courses})