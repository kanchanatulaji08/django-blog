from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Comment, Post


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user("alice", "alice@example.com", "pass12345")
        cls.other = User.objects.create_user("bob", "bob@example.com", "pass12345")
        cls.category = Category.objects.create(name="Python")
        cls.post = Post.objects.create(
            title="Hello World",
            body="First post body",
            author=cls.author,
            category=cls.category,
        )
        cls.draft = Post.objects.create(
            title="Secret Draft",
            body="Not ready yet",
            author=cls.author,
            status=Post.DRAFT,
        )


class ModelTests(BaseTestCase):
    def test_slug_is_generated_from_title(self):
        self.assertEqual(self.post.slug, "hello-world")
        self.assertEqual(self.category.slug, "python")

    def test_duplicate_titles_get_unique_slugs(self):
        second = Post.objects.create(title="Hello World", body="x", author=self.author)
        self.assertEqual(second.slug, "hello-world-2")

    def test_slug_does_not_change_when_title_is_edited(self):
        self.post.title = "A brand new title"
        self.post.save()
        self.post.refresh_from_db()
        self.assertEqual(self.post.slug, "hello-world")

    def test_published_queryset_excludes_drafts(self):
        self.assertQuerySetEqual(Post.objects.published(), [self.post])


class PostListTests(BaseTestCase):
    def test_list_shows_only_published_posts(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertContains(response, "Hello World")
        self.assertNotContains(response, "Secret Draft")

    def test_search_filters_posts(self):
        Post.objects.create(title="Django tips", body="about ORM", author=self.author)
        response = self.client.get(reverse("blog:post_list"), {"q": "django"})
        self.assertContains(response, "Django tips")
        self.assertNotContains(response, "Hello World")

    def test_category_page_filters_posts(self):
        Post.objects.create(title="No category post", body="x", author=self.author)
        response = self.client.get(reverse("blog:category", args=[self.category.slug]))
        self.assertContains(response, "Hello World")
        self.assertNotContains(response, "No category post")

    def test_pagination(self):
        for i in range(6):
            Post.objects.create(title=f"Extra {i}", body="x", author=self.author)
        response = self.client.get(reverse("blog:post_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["posts"]), 5)


class PostDetailTests(BaseTestCase):
    def test_published_post_is_public(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_draft_hidden_from_anonymous_and_other_users(self):
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.client.login(username="bob", password="pass12345")
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)

    def test_draft_visible_to_author(self):
        self.client.login(username="alice", password="pass12345")
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 200)


class PostCrudTests(BaseTestCase):
    def test_create_requires_login(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_logged_in_user_can_create_post(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.post(
            reverse("blog:post_create"),
            {"title": "Bob's post", "body": "Hi", "status": Post.PUBLISHED},
        )
        post = Post.objects.get(title="Bob's post")
        self.assertRedirects(response, post.get_absolute_url())
        self.assertEqual(post.author, self.other)

    def test_only_author_can_edit(self):
        url = reverse("blog:post_update", args=[self.post.slug])
        self.client.login(username="bob", password="pass12345")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username="alice", password="pass12345")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_author_can_update_post(self):
        self.client.login(username="alice", password="pass12345")
        self.client.post(
            reverse("blog:post_update", args=[self.post.slug]),
            {"title": "Updated", "body": "New body", "status": Post.PUBLISHED},
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated")

    def test_only_author_can_delete(self):
        url = reverse("blog:post_delete", args=[self.post.slug])
        self.client.login(username="bob", password="pass12345")
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
        self.client.login(username="alice", password="pass12345")
        self.client.post(url)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_my_posts_lists_drafts_for_owner(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("blog:my_posts"))
        self.assertContains(response, "Secret Draft")


class CommentTests(BaseTestCase):
    def test_comment_requires_login(self):
        url = reverse("blog:comment_create", args=[self.post.slug])
        response = self.client.post(url, {"body": "Nice"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_logged_in_user_can_comment(self):
        self.client.login(username="bob", password="pass12345")
        self.client.post(reverse("blog:comment_create", args=[self.post.slug]), {"body": "Nice post"})
        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.other)
        self.assertEqual(comment.post, self.post)

    def test_empty_comment_is_rejected(self):
        self.client.login(username="bob", password="pass12345")
        self.client.post(reverse("blog:comment_create", args=[self.post.slug]), {"body": ""})
        self.assertEqual(Comment.objects.count(), 0)

    def test_cannot_comment_on_draft(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(reverse("blog:comment_create", args=[self.draft.slug]), {"body": "x"})
        self.assertEqual(response.status_code, 404)

    def test_comment_delete_permissions(self):
        comment = Comment.objects.create(post=self.post, author=self.other, body="Hi")
        stranger = User.objects.create_user("carol", "carol@example.com", "pass12345")
        url = reverse("blog:comment_delete", args=[comment.pk])

        self.client.login(username="carol", password="pass12345")
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
        self.client.logout()

        # The post's author may remove comments on their post.
        self.client.login(username="alice", password="pass12345")
        self.client.post(url)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.assertIsNotNone(stranger.pk)


class AccountTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "S3cure-pass-987",
                "password2": "S3cure-pass-987",
            },
        )
        self.assertRedirects(response, reverse("blog:post_list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user("existing", "dup@example.com", "pass12345")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "another",
                "email": "DUP@example.com",
                "password1": "S3cure-pass-987",
                "password2": "S3cure-pass-987",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_login_and_logout(self):
        User.objects.create_user("dave", "dave@example.com", "pass12345")
        self.assertTrue(self.client.login(username="dave", password="pass12345"))
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
