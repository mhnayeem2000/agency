import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.views.decorators.http import require_POST

from .forms import BlogPostForm
from .models import BlogCategory, BlogPost, BlogTag, unique_slug


def _blog_staff(user):
    return user.is_authenticated and (user.is_superuser or user.role == "staff")


def _post_list(request, queryset, title, description):
    page = Paginator(queryset, 9).get_page(request.GET.get("page"))
    return render(
        request,
        "blog/archive.html",
        {
            "page_obj": page,
            "posts": page.object_list,
            "categories": BlogCategory.objects.annotate(
                post_count=Count(
                    "posts",
                    filter=Q(
                        posts__is_published=True,
                        posts__published_at__lte=timezone.now(),
                    ),
                )
            ).filter(post_count__gt=0),
            "archive_title": title,
            "archive_description": description,
        },
    )


def blog_archive_view(request):
    return _post_list(
        request,
        BlogPost.objects.published().select_related("category").prefetch_related("tags"),
        "Bright Abroad China Journal",
        "Explore practical study-abroad advice, university application tips and visa guidance from Bright Abroad China. Bright Beyond Borders.",
    )


def blog_category_view(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    return _post_list(
        request,
        BlogPost.objects.published()
        .filter(category=category)
        .select_related("category")
        .prefetch_related("tags"),
        category.name,
        f"Study-abroad advice and insights about {category.name}.",
    )


def blog_tag_view(request, slug):
    tag = get_object_or_404(BlogTag, slug=slug)
    return _post_list(
        request,
        BlogPost.objects.published()
        .filter(tags=tag)
        .select_related("category")
        .prefetch_related("tags"),
        f"Articles tagged {tag.name}",
        f"Read our latest articles tagged {tag.name}.",
    )


def blog_detail_view(request, slug):
    post = get_object_or_404(
        BlogPost.objects.published()
        .select_related("category", "author")
        .prefetch_related("tags"),
        slug=slug,
    )
    related_posts = (
        BlogPost.objects.published()
        .filter(category=post.category)
        .exclude(pk=post.pk)
        .select_related("category")
        .prefetch_related("tags")[:3]
        if post.category_id
        else BlogPost.objects.none()
    )
    image_url = (
        request.build_absolute_uri(post.featured_image.url)
        if post.featured_image
        else request.build_absolute_uri("/static/images/Logo.png")
    )
    structured_data = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post.title,
            "description": post.seo_page_description,
            "image": image_url,
            "datePublished": post.published_at.isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": (
                    post.author.get_full_name() or post.author.username
                    if post.author
                    else "Bright Abroad China"
                ),
            },
            "mainEntityOfPage": request.build_absolute_uri(post.get_absolute_url()),
            "articleBody": Truncator(strip_tags(post.content)).chars(500),
        },
        ensure_ascii=False,
    ).replace("<", "\\u003c")
    return render(
        request,
        "blog/detail.html",
        {
            "post": post,
            "related_posts": related_posts,
            "canonical_url": request.build_absolute_uri(post.get_absolute_url()),
            "share_url": request.build_absolute_uri(post.get_absolute_url()),
            "social_image": image_url,
            "structured_data": structured_data,
        },
    )


@login_required(login_url="login")
@user_passes_test(_blog_staff, login_url="login")
def blog_manage_view(request):
    posts = BlogPost.objects.select_related("category").order_by("-updated_at")
    return render(request, "blog/manage.html", {"posts": posts})


@login_required(login_url="login")
@user_passes_test(_blog_staff, login_url="login")
def blog_post_create_view(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        form.save_m2m()
        for name in dict.fromkeys(
            tag.strip()
            for tag in form.cleaned_data.get("tag_names", "").split(",")
            if tag.strip()
        ):
            tag_slug = unique_slug(BlogTag(), name, BlogTag.objects.all())
            tag, _ = BlogTag.objects.get_or_create(
                name=name,
                defaults={"slug": tag_slug},
            )
            post.tags.add(tag)
        messages.success(request, "Your blog post has been saved.")
        return redirect("blog_manage")
    return render(request, "blog/post_form.html", {"form": form, "page_title": "Write a new post"})


@login_required(login_url="login")
@user_passes_test(_blog_staff, login_url="login")
def blog_post_edit_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    form = BlogPostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your blog post has been updated.")
        return redirect("blog_manage")
    return render(
        request,
        "blog/post_form.html",
        {"form": form, "page_title": "Edit post", "post": post},
    )


@login_required(login_url="login")
@user_passes_test(_blog_staff, login_url="login")
@require_POST
def blog_post_delete_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    post.delete()
    messages.success(request, "The blog post has been deleted.")
    return redirect("blog_manage")
