from django.contrib import admin

from .models import Category, Comment, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "author__username")
