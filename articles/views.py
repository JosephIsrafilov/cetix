from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.mixins import RoleRequiredMixin
from .forms import ArticleForm, CommentForm
from .models import Article, ArticleComment, ArticleReaction, Bookmark, Category

User = get_user_model()


class ArticleListView(ListView):
    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return (
            Article.published.select_related("author", "category")
            .annotate(
                total_likes=Count(
                    "reactions",
                    filter=Q(reactions__value=ArticleReaction.VALUE_LIKE),
                    distinct=True,
                ),
                total_dislikes=Count(
                    "reactions",
                    filter=Q(reactions__value=ArticleReaction.VALUE_DISLIKE),
                    distinct=True,
                ),
                comment_count=Count("comments", distinct=True),
            )
            .annotate(net_score=F("total_likes") - F("total_dislikes"))
            .order_by("-net_score", "-published_at", "-created_at")
        )


class PopularArticleListView(ArticleListView):
    template_name = "articles/popular_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(net_score__gte=5)
        )


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Article.objects.select_related(
                "author", "category", "last_moderated_by"
            )
            .prefetch_related(
                "reactions",
                "bookmarks",
                "comments",
                "comments__user",
                "comments__replies",
                "comments__replies__user",
            )
        )

    def get_object(self, queryset=None):
        article = super().get_object(queryset)
        user = self.request.user
        if article.status != Article.STATUS_PUBLISHED and not article.can_edit(user):
            raise Http404
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context["article"]
        user = self.request.user
        user_reaction = None
        is_bookmarked = False
        if user.is_authenticated:
            user_reaction = article.reactions.filter(user=user).first()
            is_bookmarked = article.bookmarks.filter(user=user).exists()

        top_level_comments = (
            article.comments.filter(parent__isnull=True)
            .select_related("user")
            .prefetch_related("replies__user")
        )

        context.update(
            {
                "user_reaction": user_reaction,
                "is_bookmarked": is_bookmarked,
                "can_edit": article.can_edit(user),
                "comment_form": CommentForm(),
                "top_level_comments": top_level_comments,
                "comments_count": article.comments.count(),
            }
        )
        return context


class ArticleAuthorMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        article = super().get_object(queryset)
        if not article.can_edit(self.request.user):
            raise Http404("You do not have permission to modify this article.")
        if getattr(self.request.user, "is_banned", False):
            raise Http404("Account banned.")
        return article


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        article = self.object
        if article.requires_moderation_for(self.request.user):
            article.status = Article.STATUS_PENDING
            article.last_moderated_by = None
            article.last_moderated_at = None
            article.save()
            messages.info(
                self.request,
                "Article submitted for review. An admin will publish it soon.",
            )
        else:
            messages.success(self.request, "Article published.")
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class ArticleUpdateView(ArticleAuthorMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        article = self.object
        if article.requires_moderation_for(self.request.user):
            article.status = Article.STATUS_PENDING
            article.last_moderated_by = None
            article.last_moderated_at = None
            article.save()
            messages.info(
                self.request,
                "Changes saved and sent for moderation.",
            )
        else:
            messages.success(self.request, "Article updated.")
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class ArticleDeleteView(ArticleAuthorMixin, DeleteView):
    model = Article
    template_name = "articles/article_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("articles:article_list")

    def delete(self, request, *args, **kwargs):
        messages.info(request, "Article deleted.")
        return super().delete(request, *args, **kwargs)


class PendingArticleListView(RoleRequiredMixin, ListView):
    model = Article
    template_name = "articles/moderation_queue.html"
    context_object_name = "articles"
    allowed_roles = ("is_admin",)

    def get_queryset(self):
        return (
            Article.objects.filter(status=Article.STATUS_PENDING)
            .select_related("author", "category")
            .order_by("created_at")
        )


class ArticleModerateView(RoleRequiredMixin, View):
    allowed_roles = ("is_admin",)

    def post(self, request, slug, action):
        article = get_object_or_404(Article, slug=slug)
        if action not in {"publish", "reject"}:
            raise Http404("Unknown moderation action.")
        if action == "publish":
            article.status = Article.STATUS_PUBLISHED
            article.last_moderated_by = request.user
            article.last_moderated_at = timezone.now()
            article.save()
            messages.success(request, f"Published '{article.title}'.")
        else:
            article.status = Article.STATUS_REJECTED
            article.last_moderated_by = request.user
            article.last_moderated_at = timezone.now()
            article.save()
            messages.warning(request, f"Rejected '{article.title}'.")
        return HttpResponseRedirect(reverse("articles:moderation_queue"))


class CategoryListView(ListView):
    model = Category
    template_name = "articles/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return (
            Category.objects.annotate(
                published_count=Count(
                    "articles",
                    filter=Q(articles__status=Article.STATUS_PUBLISHED),
                )
            )
            .order_by("name")
        )


class CategoryArticleListView(ListView):
    model = Article
    template_name = "articles/category_detail.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return (
            Article.published.filter(category=self.category)
            .select_related("author", "category")
            .annotate(
                total_likes=Count(
                    "reactions",
                    filter=Q(reactions__value=ArticleReaction.VALUE_LIKE),
                ),
                total_dislikes=Count(
                    "reactions",
                    filter=Q(reactions__value=ArticleReaction.VALUE_DISLIKE),
                ),
                comment_count=Count("comments", distinct=True),
            )
            .annotate(net_score=F("total_likes") - F("total_dislikes"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class AuthorListView(ListView):
    model = User
    template_name = "articles/author_list.html"
    context_object_name = "authors"

    def get_queryset(self):
        return (
            User.objects.filter(articles__status=Article.STATUS_PUBLISHED)
            .annotate(
                published_count=Count(
                    "articles",
                    filter=Q(articles__status=Article.STATUS_PUBLISHED),
                )
            )
            .distinct()
            .order_by("username")
        )


class AuthorDetailView(DetailView):
    model = User
    template_name = "articles/author_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = (
            self.object.articles.filter(status=Article.STATUS_PUBLISHED)
            .select_related("category")
            .annotate(
                total_likes=Count(
                    "reactions",
                    filter=Q(reactions__value=ArticleReaction.VALUE_LIKE),
                    distinct=True,
                ),
                total_dislikes=Count(
                    "reactions",
                    filter=Q(reactions__value=ArticleReaction.VALUE_DISLIKE),
                    distinct=True,
                ),
                comment_count=Count("comments", distinct=True),
            )
            .annotate(net_score=F("total_likes") - F("total_dislikes"))
        )
        return context


class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = "articles/bookmark_list.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return (
            Bookmark.objects.filter(user=self.request.user)
            .select_related("article", "article__author", "article__category")
            .annotate(
                total_likes=Count(
                    "article__reactions",
                    filter=Q(article__reactions__value=ArticleReaction.VALUE_LIKE),
                    distinct=True,
                ),
                total_dislikes=Count(
                    "article__reactions",
                    filter=Q(
                        article__reactions__value=ArticleReaction.VALUE_DISLIKE
                    ),
                    distinct=True,
                ),
                comment_count=Count("article__comments", distinct=True),
            )
            .order_by("-created_at")
        )


class ToggleBookmarkView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, status=Article.STATUS_PUBLISHED)
        bookmark, created = Bookmark.objects.get_or_create(
            article=article, user=request.user
        )
        if not created:
            bookmark.delete()
            messages.info(request, "Removed from bookmarks.")
        else:
            messages.success(request, "Added to bookmarks.")
        return HttpResponseRedirect(article.get_absolute_url())


class ToggleReactionView(LoginRequiredMixin, View):
    def post(self, request, slug, reaction):
        if reaction not in {ArticleReaction.VALUE_LIKE, ArticleReaction.VALUE_DISLIKE}:
            raise Http404("Unknown reaction.")
        article = get_object_or_404(Article, slug=slug, status=Article.STATUS_PUBLISHED)
        obj, created = ArticleReaction.objects.get_or_create(
            article=article, user=request.user, defaults={"value": reaction}
        )
        user_value = reaction
        if not created:
            if obj.value == reaction:
                obj.delete()
                user_value = None
            else:
                obj.value = reaction
                obj.save(update_fields=["value"])
        likes = article.likes_count
        dislikes = article.dislikes_count
        score = likes - dislikes
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            return JsonResponse(
                {
                    "reaction": user_value,
                    "likes": likes,
                    "dislikes": dislikes,
                    "score": score,
                }
            )
        redirect_url = f"{article.get_absolute_url()}#engage"
        return HttpResponseRedirect(redirect_url)


class ArticleCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, status=Article.STATUS_PUBLISHED)
        form = CommentForm(request.POST)
        if form.is_valid():
            parent = None
            parent_id = form.cleaned_data.get("parent_id")
            if parent_id:
                parent = article.comments.filter(pk=parent_id).first()
                if parent and parent.parent_id:
                    parent = parent.parent
            new_comment = ArticleComment.objects.create(
                article=article,
                user=request.user,
                parent=parent,
                body=form.cleaned_data["body"],
            )
            redirect_url = f"{article.get_absolute_url()}#comment-{new_comment.pk}"
        else:
            redirect_url = f"{article.get_absolute_url()}#comments"
        return HttpResponseRedirect(redirect_url)
