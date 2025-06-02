# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    profile_img_url = models.TextField(default='')
    role = models.TextField(default='user')
    total_questions = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    post_likes_cnt = models.IntegerField(default=0)
    comment_likes_cnt = models.IntegerField(default=0)
    course_likes_cnt = models.IntegerField(default=0)
    chat_help_likes_cnt = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_deop = models.BooleanField(default=False)
    problems_resolved_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Admin: {self.user.username}"

class AdminAction(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    action_type = models.TextField()
    target_id = models.IntegerField()
    details = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action_type} by {self.admin.user.username}"

class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    reporting_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_submitted')
    reporting_target_type = models.TextField()
    reporting_target_id = models.IntegerField()
    report_description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_processed')
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report by {self.reporting_user.username} on {self.reporting_target_type}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    content = models.TextField()
    image_url = models.TextField(blank=True)
    code = models.TextField(blank=True)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    code = models.TextField(blank=True)
    image_url = models.TextField(blank=True)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"

class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    image_url = models.TextField(blank=True)
    content = models.TextField()
    code = models.TextField(blank=True)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user2')
    chat_likes_cnt = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    image_url = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    is_code = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class Code(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='code_snippets')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='code_snippets')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code_content = models.TextField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    language = models.TextField()
    start_line = models.IntegerField()
    end_line = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Code by {self.user.username} in {self.language}"

class CodeComment(models.Model):
    code = models.ForeignKey(Code, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    comm_content = models.TextField()
    start_line = models.IntegerField()
    end_line = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Code Comment by {self.user.username}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rating for {self.user.username}: {self.score}"

class ProfileView(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)  # Рейтинг в брс (0–15)
    total_points = models.IntegerField(default=0)  # Сырые баллы (до 60)

    def __str__(self):
        return f"Profile for {self.user.username}"

    def update_rating(self):
        # Ограничиваем сырые баллы до 60
        self.total_points = min(self.total_points, 60)
        # Пересчитываем рейтинг в брс: баллы * 0.25, округление
        self.rating = round(self.total_points * 0.25)
        self.save()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_type = models.TextField()
    target_id = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} liked {self.target_type} {self.target_id}"

class Call(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    call_url = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Call in chat {self.chat.id}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.user.username} for {self.target_user.username}"

class UserWarning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(null=True)
    
    def __str__(self):
        return f"Warning to {self.user.username} by {self.admin.user.username}"