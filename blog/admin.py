from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .forms import RichTextWidget
from .models import BlogCategory, BlogPost, BlogTag


class BlogPostAdminWidget(RichTextWidget):
    class Media:
        js = (
            "https://cdn.ckeditor.com/ckeditor5/41.4.2/classic/ckeditor.js",
            "blog/editor.js",
        )


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = "__all__"
        widgets = {"content": BlogPostAdminWidget(attrs={"rows": 20})}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm
    list_display = ("title", "category", "publication_status", "published_at", "updated_at")
    list_filter = ("is_published", "category", "tags")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    readonly_fields = ("author", "created_at", "updated_at")
    fieldsets = (
        ("Post", {"fields": ("title", "slug", "category", "tags", "excerpt", "content")}),
        ("Featured image", {"fields": ("featured_image", "image_alt")}),
        ("Search and social preview", {"fields": ("seo_title", "seo_description")}),
        ("Publishing", {"fields": ("is_published", "published_at", "author", "created_at", "updated_at")}),
    )

    @admin.display(description="Status")
    def publication_status(self, obj):
        if obj.is_published:
            return format_html(
                '<span style="color:#16805b;font-weight:700">{}</span>',
                "Published",
            )
        return "Draft"

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
