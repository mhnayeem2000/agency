import bleach
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(instance, value, queryset):
    base_slug = slugify(value, allow_unicode=True)[:220] or "post"
    candidate = base_slug
    suffix = 2
    while queryset.exclude(pk=instance.pk).filter(slug=candidate).exists():
        candidate = f"{base_slug[:210]}-{suffix}"
        suffix += 1
    return candidate


class BlogPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True,
            published_at__lte=timezone.now(),
        )


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, type(self).objects.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, type(self).objects.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts")
    excerpt = models.CharField(max_length=320)
    content = models.TextField()
    featured_image = models.ImageField(upload_to="blog/covers/", blank=True)
    image_alt = models.CharField(max_length=200, blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BlogPostQuerySet.as_manager()

    class Meta:
        ordering = ("-published_at", "-created_at")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title, type(self).objects.all())
        self.content = bleach.clean(
            self.content,
            tags={
                "a", "blockquote", "br", "caption", "code", "dd", "div", "dl",
                "dt", "em", "figcaption", "figure", "h2", "h3", "h4", "hr",
                "i", "img", "li", "ol", "p", "pre", "s", "strong", "sub",
                "sup", "table", "tbody", "td", "th", "thead", "tr", "u", "ul",
            },
            attributes={
                "a": ["href", "title", "target", "rel"],
                "img": ["src", "alt", "title", "width", "height"],
                "td": ["colspan", "rowspan"],
                "th": ["colspan", "rowspan", "scope"],
            },
            protocols={"http", "https", "mailto"},
            strip=True,
        )
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("blog_detail", kwargs={"slug": self.slug})

    @property
    def seo_page_title(self):
        return self.seo_title or self.title

    @property
    def seo_page_description(self):
        return self.seo_description or self.excerpt
