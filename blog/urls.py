from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("category/<slug:slug>/", views.PostListView.as_view(), name="category"),
    path("my-posts/", views.MyPostsView.as_view(), name="my_posts"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("post/<slug:slug>/comment/", views.CommentCreateView.as_view(), name="comment_create"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
]
