from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def make_unique_slug(instance, value, max_length):
    """Build a slug from `value` that is unique for the instance's model."""
    model = instance.__class__
    base = slugify(value)[:max_length] or model.__name__.lower()
    slug = base
    counter = 2
    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        slug = f"{base[: max_length - len(suffix)]}{suffix}"
        counter += 1
    return slug


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(self, self.name, 110)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=self.model.PUBLISHED)


class Post(models.Model):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PUBLISHED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate the slug once so post URLs stay stable when the title is edited.
        if not self.slug:
            self.slug = make_unique_slug(self, self.title, 220)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == self.PUBLISHED


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
