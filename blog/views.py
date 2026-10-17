from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class PostListView(ListView):
    """Published posts, with optional category filter and search (?q=)."""

    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        queryset = (
            Post.objects.published()
            .select_related("author", "category")
            .annotate(comment_count=Count("comments"))
        )
        self.category = None
        slug = self.kwargs.get("slug")
        if slug:
            self.category = get_object_or_404(Category, slug=slug)
            queryset = queryset.filter(category=self.category)

        self.query = self.request.GET.get("q", "").strip()
        if self.query:
            queryset = queryset.filter(
                Q(title__icontains=self.query) | Q(body__icontains=self.query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["query"] = self.query
        return context


class MyPostsView(LoginRequiredMixin, ListView):
    """The logged-in user's own posts, including drafts."""

    template_name = "blog/my_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).select_related("category")


class PostDetailView(DetailView):
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.select_related("author", "category")
        if self.request.user.is_authenticated:
            # Drafts are visible only to their author.
            return queryset.filter(
                Q(status=Post.PUBLISHED) | Q(author=self.request.user)
            )
        return queryset.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related("author")
        context["comment_form"] = CommentForm()
        return context


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only the post's author may proceed (others get a 403)."""

    def test_func(self):
        return self.get_object().author_id == self.request.user.id


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Your post was saved.")
        return super().form_valid(form)


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Your post was updated.")
        return super().form_valid(form)


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form):
        messages.success(self.request, "The post was deleted.")
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, slug):
        post = get_object_or_404(Post.objects.published(), slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
        else:
            messages.error(request, "Your comment could not be saved. Please check it and try again.")
        return redirect(post)


class CommentDeleteView(LoginRequiredMixin, View):
    """A comment can be removed by its author or by the post's author."""

    http_method_names = ["post"]

    def post(self, request, pk):
        comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)
        if request.user.id not in (comment.author_id, comment.post.author_id):
            raise PermissionDenied
        post = comment.post
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect(post)
