from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PublishedArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Article.STATUS_PUBLISHED)


class Article(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_PUBLISHED = "published"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending Review"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_REJECTED, "Rejected"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="articles"
    )
    cover_image = models.ImageField(upload_to="covers/")
    content = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_articles",
    )
    last_moderated_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    published = PublishedArticleManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["-published_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            suffix = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix += 1
                slug = f"{base_slug}-{suffix}"
            self.slug = slug
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        if self.status != self.STATUS_PUBLISHED:
            self.published_at = None
        super().save(*args, **kwargs)

    @property
    def likes_count(self) -> int:
        if hasattr(self, "total_likes") and self.total_likes is not None:
            return self.total_likes
        return self.reactions.filter(value=ArticleReaction.VALUE_LIKE).count()

    @property
    def dislikes_count(self) -> int:
        if hasattr(self, "total_dislikes") and self.total_dislikes is not None:
            return self.total_dislikes
        return self.reactions.filter(value=ArticleReaction.VALUE_DISLIKE).count()

    def can_edit(self, user) -> bool:
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if getattr(user, "is_super_admin", False) or getattr(user, "is_admin", False):
            return True
        return self.author_id == user.id

    def can_delete(self, user) -> bool:
        return self.can_edit(user)

    def requires_moderation_for(self, user) -> bool:
        if not user or not getattr(user, "is_authenticated", False):
            return True
        return not (
            getattr(user, "is_super_admin", False)
            or getattr(user, "is_admin", False)
        )

    def get_absolute_url(self):
        return reverse("articles:article_detail", args=[self.slug])

    @property
    def score(self) -> int:
        return self.likes_count - self.dislikes_count


class ArticleReaction(models.Model):
    VALUE_LIKE = "like"
    VALUE_DISLIKE = "dislike"

    VALUE_CHOICES = [
        (VALUE_LIKE, "Like"),
        (VALUE_DISLIKE, "Dislike"),
    ]

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="article_reactions"
    )
    value = models.CharField(max_length=10, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "user")

    def __str__(self) -> str:
        return f"{self.user} -> {self.article} ({self.value})"


class Bookmark(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="bookmarks"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookmarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "user")

    def __str__(self) -> str:
        return f"{self.user} bookmarked {self.article}"


class ArticleComment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="article_comments"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.user} on {self.article}: {self.body[:40]}"
