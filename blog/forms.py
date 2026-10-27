from django import forms

from .models import BlogCategory, BlogPost, BlogTag, unique_slug


class RichTextWidget(forms.Textarea):
    def use_required_attribute(self, initial):
        return False


class BlogPostForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=100,
        required=False,
        label="Or create a category",
        help_text="Leave blank to use the selected category.",
    )
    tag_names = forms.CharField(
        max_length=500,
        required=False,
        label="Add tags",
        help_text="Separate new tag names with commas.",
    )

    class Meta:
        model = BlogPost
        fields = (
            "title",
            "slug",
            "category",
            "new_category",
            "tags",
            "tag_names",
            "excerpt",
            "content",
            "featured_image",
            "image_alt",
            "seo_title",
            "seo_description",
            "is_published",
        )
        widgets = {
            "content": RichTextWidget(attrs={"class": "js-ckeditor", "rows": 18}),
            "tags": forms.CheckboxSelectMultiple,
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "seo_description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = BlogCategory.objects.all()
        self.fields["tags"].queryset = BlogTag.objects.all()
        self.fields["slug"].required = False

    def save(self, commit=True):
        post = super().save(commit=False)
        category_name = self.cleaned_data.get("new_category", "").strip()
        if category_name:
            category_slug = unique_slug(
                BlogCategory(),
                category_name,
                BlogCategory.objects.all(),
            )
            post.category, _ = BlogCategory.objects.get_or_create(
                name=category_name,
                defaults={"slug": category_slug},
            )

        if commit:
            post.save()
            self.save_m2m()
            for name in dict.fromkeys(
                tag.strip()
                for tag in self.cleaned_data.get("tag_names", "").split(",")
                if tag.strip()
            ):
                tag_slug = unique_slug(BlogTag(), name, BlogTag.objects.all())
                tag, _ = BlogTag.objects.get_or_create(
                    name=name,
                    defaults={"slug": tag_slug},
                )
                post.tags.add(tag)
        return post
