from django.urls import path

from .views import (
    ArticleCreateView,
    ArticleDeleteView,
    ArticleDetailView,
    ArticleListView,
    ArticleModerateView,
    ArticleUpdateView,
    AuthorDetailView,
    AuthorListView,
    BookmarkListView,
    CategoryArticleListView,
    CategoryListView,
    PendingArticleListView,
    PopularArticleListView,
    ArticleCommentCreateView,
    ToggleBookmarkView,
    ToggleReactionView,
)

app_name = "articles"

urlpatterns = [
    path("", ArticleListView.as_view(), name="article_list"),
    path("popular/", PopularArticleListView.as_view(), name="popular_list"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path(
        "categories/<slug:slug>/",
        CategoryArticleListView.as_view(),
        name="category_detail",
    ),
    path("authors/", AuthorListView.as_view(), name="author_list"),
    path("authors/<str:username>/", AuthorDetailView.as_view(), name="author_detail"),
    path("bookmarks/", BookmarkListView.as_view(), name="bookmark_list"),
    path("create/", ArticleCreateView.as_view(), name="article_create"),
    path("moderation/", PendingArticleListView.as_view(), name="moderation_queue"),
    path(
        "moderation/<slug:slug>/<str:action>/",
        ArticleModerateView.as_view(),
        name="article_moderate",
    ),
    path("<slug:slug>/edit/", ArticleUpdateView.as_view(), name="article_update"),
    path("<slug:slug>/delete/", ArticleDeleteView.as_view(), name="article_delete"),
    path("<slug:slug>/bookmark/", ToggleBookmarkView.as_view(), name="toggle_bookmark"),
    path(
        "<slug:slug>/react/<str:reaction>/",
        ToggleReactionView.as_view(),
        name="toggle_reaction",
    ),
    path("<slug:slug>/comment/", ArticleCommentCreateView.as_view(), name="comment_create"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
]
