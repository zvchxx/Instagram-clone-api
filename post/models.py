from django.db import models
from django.conf import settings
from django.forms import ValidationError
from user.models import UserModel


class PostModel(models.Model):
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children', null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tweets"
    )
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    opisanya = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Media {self.id}"

    def clean(self):
        if not self.image and not self.video:
            raise ValidationError('At least one of image or video must be provided.')
        if self.image and self.video:
            raise ValidationError('Only one of image or video should be provided.')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class StoryModel(models.Model):
    author = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, related_name="user_stories"
    )
    image = models.ImageField(upload_to="stories/images/", blank=True, null=True)
    video = models.FileField(upload_to="stories/media/", blank=True, null=True)
    content = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:15] if self.content else 'No Content'}"

    def clean(self):
        if not self.image and not self.video:
            raise ValidationError('At least one of image or video must be provided.')
        if self.image and self.video:
            raise ValidationError('Only one of image or video should be provided.')

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    @property
    def total_likes(self):
        return self.story_likes.count()

    @property
    def total_comments(self):
        return self.story_comments.count()


class BookMarkModel(models.Model):
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="bookmarks"
    )
    related_post = models.ForeignKey(
        PostModel, on_delete=models.CASCADE, blank=True, null=True, related_name="bookmarked_posts"
    )
    related_story = models.ForeignKey(
        StoryModel, on_delete=models.CASCADE, blank=True, null=True, related_name="bookmarked_stories"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.related_post:
            return f"Bookmark: {self.user.username} -> Post: {self.related_post.opisanya[:10]}"
        return f"Bookmark: {self.user.username} -> Story: {self.related_story.content[:10]}"

    class Meta:
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"


class PostCommentModel(models.Model):
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='children', null=True, blank=True
    )
    text = models.CharField(max_length=300)
    post = models.ForeignKey(
        PostModel, on_delete=models.CASCADE, related_name="post_comments"
    )
    commenter = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="user_comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.commenter.username}: {self.text[:15]}"

    class Meta:
        verbose_name = "Post Comment"
        verbose_name_plural = "Post Comments"

    @property
    def like_count(self):
        return self.comment_likes.count()


class PostLikeModel(models.Model):
    post = models.ForeignKey(
        PostModel, on_delete=models.CASCADE, related_name="post_likes"
    )
    liked_by = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="liked_posts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.liked_by.username} -> Post: {self.post.opisanya[:15]}"

    class Meta:
        verbose_name = "Post Like"
        verbose_name_plural = "Post Likes"
        unique_together = [('liked_by', 'post')]


class StoryLikeModel(models.Model):
    story = models.ForeignKey(
        StoryModel, on_delete=models.CASCADE, related_name="story_likes"
    )
    liked_by = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="liked_stories"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.liked_by.username} -> Story: {self.story.content[:15]}"

    class Meta:
        verbose_name = "Story Like"
        verbose_name_plural = "Story Likes"
        unique_together = [('liked_by', 'story')]


class CommentLikeModel(models.Model):
    comment = models.ForeignKey(
        PostCommentModel, on_delete=models.CASCADE, related_name="comment_likes"
    )
    liked_by = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="liked_comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.liked_by.username} -> Comment: {self.comment.text[:15]}"

    class Meta:
        verbose_name = "Comment Like"
        verbose_name_plural = "Comment Likes"
