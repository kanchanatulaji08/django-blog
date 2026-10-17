from django.db.models import Count, Q

from .models import Category, Post


def sidebar_categories(request):
    """Make categories (with published post counts) available in every template."""
    categories = Category.objects.annotate(
        post_count=Count("posts", filter=Q(posts__status=Post.PUBLISHED))
    )
    return {"sidebar_categories": categories}
