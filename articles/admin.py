from django.contrib import admin

from .models import Article, ArticleComment, ArticleReaction, Bookmark, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "category",
        "created_at",
        "published_at",
    )
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "author__username", "author__email")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category", "last_moderated_by")
    ordering = ("-created_at",)


@admin.register(ArticleReaction)
class ArticleReactionAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "value", "created_at")
    list_filter = ("value", "created_at")
    search_fields = ("article__title", "user__username")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "created_at")
    search_fields = ("article__title", "user__username")


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "parent", "created_at")
    search_fields = ("article__title", "user__username", "body")
    autocomplete_fields = ("article", "user", "parent")
