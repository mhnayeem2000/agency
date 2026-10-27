from django.contrib.auth import get_user_model
from django.conf import settings
from pathlib import Path
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import BlogPostAdminForm
from .forms import BlogPostForm
from .models import BlogCategory, BlogPost, BlogTag


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class BlogPublicViewsTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username="editor",
            password="editor-password",
            role="staff",
        )
        self.category = BlogCategory.objects.create(name="Study planning")
        self.post = BlogPost.objects.create(
            title="A useful guide",
            excerpt="A short introduction.",
            content="<h2>Plan well</h2><script>alert(1)</script><p>Make a list.</p>",
            category=self.category,
            is_published=True,
            author=self.author,
        )

    def test_only_published_posts_appear_on_home_and_archive(self):
        draft = BlogPost.objects.create(
            title="Private draft",
            excerpt="Not yet public.",
            content="<p>Draft text</p>",
        )

        home_response = self.client.get(reverse("home"))
        archive_response = self.client.get(reverse("blog_archive"))

        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, self.post.title)
        self.assertNotContains(home_response, draft.title)
        self.assertContains(archive_response, self.post.title)
        self.assertNotContains(archive_response, draft.title)

    def test_detail_has_social_preview_metadata_and_safe_rich_content(self):
        response = self.client.get(self.post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'property="og:image"')
        self.assertContains(response, 'name="twitter:card"')
        self.assertContains(response, "application/ld+json")
        self.assertContains(response, "<h2>Plan well</h2>", html=True)
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_featured_image_is_used_for_social_sharing(self):
        self.post.featured_image = "blog/covers/guide.png"
        self.post.save()

        response = self.client.get(self.post.get_absolute_url())

        self.assertContains(
            response,
            'property="og:image" content="http://testserver/media/blog/covers/guide.png"',
        )
        self.assertContains(response, 'name="twitter:image"')

    def test_related_posts_use_the_same_category(self):
        related = BlogPost.objects.create(
            title="Another guide",
            excerpt="More useful advice.",
            content="<p>More advice</p>",
            category=self.category,
            is_published=True,
        )
        BlogPost.objects.create(
            title="Different category",
            excerpt="Other topic.",
            content="<p>Different topic</p>",
            category=BlogCategory.objects.create(name="Applications"),
            is_published=True,
        )

        self.post.featured_image = "blog/covers/guide.png"
        self.post.save()
        tag = BlogTag.objects.create(name="Applications")
        self.post.tags.add(tag)

        response = self.client.get(self.post.get_absolute_url())
        page = response.content.decode()

        self.assertContains(response, related.title)
        self.assertNotContains(response, "Different category")
        self.assertContains(response, tag.name)

        title_position = page.index("<h1>", page.index('class="blog-article-header"'))
        image_position = page.index('class="blog-cover"')
        metadata_position = page.index('class="blog-article-meta"')
        description_position = page.index('class="blog-article-content"')
        share_position = page.index('class="blog-share-footer"')
        related_position = page.index('class="blog-related"')
        self.assertLess(title_position, image_position)
        self.assertLess(image_position, metadata_position)
        self.assertLess(metadata_position, description_position)
        self.assertLess(description_position, share_position)
        self.assertLess(share_position, related_position)

    def test_bengali_post_title_gets_a_resolvable_slug(self):
        post = BlogPost.objects.create(
            title="বিদেশে উচ্চশিক্ষা",
            excerpt="বিদেশে পড়াশোনার পরিকল্পনা।",
            content="<p>পরিকল্পনা শুরু করুন।</p>",
            is_published=True,
        )

        self.assertTrue(any(ord(character) > 127 for character in post.slug))
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 200)

    def test_sitemap_includes_public_posts(self):
        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.get_absolute_url())

    def test_category_and_tag_archive_filter_posts(self):
        tag = BlogTag.objects.create(name="Applications")
        self.post.tags.add(tag)

        category_response = self.client.get(
            reverse("blog_category", kwargs={"slug": self.category.slug})
        )
        tag_response = self.client.get(reverse("blog_tag", kwargs={"slug": tag.slug}))

        self.assertContains(category_response, self.post.title)
        self.assertContains(tag_response, self.post.title)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class BlogManagementTests(TestCase):
    def test_rich_text_is_copied_before_native_form_submit(self):
        editor_script = (
            Path(settings.BASE_DIR) / "blog" / "static" / "blog" / "editor.js"
        ).read_text(encoding="utf-8")

        self.assertIn("editor.updateSourceElement()", editor_script)
        self.assertIn("HTMLFormElement.prototype.submit.call(form)", editor_script)
        self.assertNotIn("form.requestSubmit", editor_script)

    def test_only_agency_staff_can_access_blog_manager(self):
        self.assertRedirects(
            self.client.get(reverse("blog_manage")),
            f"{reverse('login')}?next={reverse('blog_manage')}",
            fetch_redirect_response=False,
        )
        student = get_user_model().objects.create_user(
            username="student",
            password="student-password",
        )
        self.client.force_login(student)
        self.assertEqual(self.client.get(reverse("blog_manage")).status_code, 302)

        staff = get_user_model().objects.create_user(
            username="agency-editor",
            password="staff-password",
            role="staff",
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("blog_manage")).status_code, 200)
        editor_response = self.client.get(reverse("blog_post_create"))
        self.assertEqual(editor_response.status_code, 200)
        self.assertContains(editor_response, "ckeditor5/41.4.2")
        self.assertContains(editor_response, 'name="content"')
        self.assertContains(editor_response, 'enctype="multipart/form-data"')

    def test_rich_text_fields_validate_on_the_server_in_both_editors(self):
        for form_class in (BlogPostForm, BlogPostAdminForm):
            with self.subTest(form=form_class.__name__):
                form = form_class()
                self.assertTrue(form.fields["content"].required)
                self.assertNotIn(" required", form["content"].as_widget())

                bound_form = form_class(
                    data={
                        "title": "A complete title",
                        "excerpt": "A complete introduction.",
                        "content": "",
                    }
                )
                self.assertFalse(bound_form.is_valid())
                self.assertIn("content", bound_form.errors)

    def test_staff_can_create_a_post_with_category_and_tags(self):
        staff = get_user_model().objects.create_user(
            username="agency-editor",
            password="staff-password",
            role="staff",
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("blog_post_create"),
            {
                "title": "Study in Canada",
                "slug": "",
                "new_category": "Destinations",
                "tag_names": "Canada, applications",
                "excerpt": "A Canada application guide.",
                "content": "<p>Prepare early.</p>",
                "seo_title": "",
                "seo_description": "",
                "image_alt": "",
                "is_published": "on",
            },
        )

        self.assertRedirects(response, reverse("blog_manage"))
        post = BlogPost.objects.get(title="Study in Canada")
        self.assertTrue(post.is_published)
        self.assertEqual(post.author, staff)
        self.assertEqual(post.category.name, "Destinations")
        self.assertEqual(set(post.tags.values_list("name", flat=True)), {"Canada", "applications"})

    def test_admin_can_create_a_post(self):
        admin_user = get_user_model().objects.create_superuser(
            username="blog-admin",
            email="blog-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)
        add_url = reverse("admin:blog_blogpost_add")

        editor_response = self.client.get(add_url)
        self.assertEqual(editor_response.status_code, 200)
        self.assertContains(editor_response, "blog/editor.js")
        self.assertContains(editor_response, 'id="id_content"')
        self.assertNotRegex(
            editor_response.content.decode(),
            r'<textarea[^>]*\bid="id_content"[^>]*\brequired\b',
        )

        response = self.client.post(
            add_url,
            {
                "title": "Admin-created article",
                "slug": "",
                "excerpt": "A useful introduction.",
                "content": "<p>Saved through the admin editor.</p>",
                "seo_title": "",
                "seo_description": "",
                "image_alt": "",
                "is_published": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        post = BlogPost.objects.get(title="Admin-created article")
        self.assertEqual(post.author, admin_user)
        self.assertEqual(post.content, "<p>Saved through the admin editor.</p>")
        changelist_response = self.client.get(reverse("admin:blog_blogpost_changelist"))
        self.assertEqual(changelist_response.status_code, 200)
