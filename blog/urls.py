from django.urls import path

from . import views


urlpatterns = [
    path("", views.blog_archive_view, name="blog_archive"),
    path("category/<str:slug>/", views.blog_category_view, name="blog_category"),
    path("tag/<str:slug>/", views.blog_tag_view, name="blog_tag"),
    path("manage/", views.blog_manage_view, name="blog_manage"),
    path("manage/new/", views.blog_post_create_view, name="blog_post_create"),
    path("manage/<str:slug>/edit/", views.blog_post_edit_view, name="blog_post_edit"),
    path("manage/<str:slug>/delete/", views.blog_post_delete_view, name="blog_post_delete"),
    path("<str:slug>/", views.blog_detail_view, name="blog_detail"),
]
