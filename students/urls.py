from django.urls import path

from .views import (
    agency_dashboard_view,
    agency_student_detail_view,
    agency_student_create_view,
    agency_student_edit_view,
    agency_student_delete_view,
    agency_document_create_view,
    agency_document_edit_view,
    agency_document_delete_view,
    agency_timeline_create_view,
    agency_timeline_edit_view,
    agency_timeline_delete_view,
    agency_academic_create_view,
    agency_academic_edit_view,
    agency_academic_delete_view,
    agency_application_create_view,
    agency_application_detail_view,
    agency_application_edit_view,
    agency_application_delete_view,
    agency_application_document_create_view,
    agency_application_timeline_create_view,
    profile_view,
    academic_add_view,
    academic_delete_view,
    documents_view,
    progress_view,
    notifications_view,
    notification_read_view,
    dashboard_view,
    application_detail_view,

)


urlpatterns = [

    path(
        "profile/",
        profile_view,
        name="profile"
    ),

    path(
        "academic/add/",
        academic_add_view,
        name="academic_add"
    ),

    path(
        "academic/<int:pk>/delete/",
        academic_delete_view,
        name="academic_delete"
    ),

        path(
        "documents/",
        documents_view,
        name="documents"
    ),

    path(
    "progress/",
    progress_view,
    name="progress"
),

path(
    "notifications/",
    notifications_view,
    name="notifications"
),

path(
    "notifications/<int:pk>/read/",
    notification_read_view,
    name="notification_read"
),

    path(
        "dashboard/",
        dashboard_view,
        name="dashboard"
    ),

    path("application/<int:pk>/", application_detail_view, name="application_detail"),

    path(
    "agency/",
    agency_dashboard_view,
    name="agency_dashboard"
),

    path("agency/student/add/", agency_student_create_view, name="agency_student_create"),
    path("agency/student/<int:pk>/edit/", agency_student_edit_view, name="agency_student_edit"),
    path("agency/student/<int:pk>/delete/", agency_student_delete_view, name="agency_student_delete"),
    path("agency/student/<int:student_pk>/document/add/", agency_document_create_view, name="agency_document_create"),
    path("agency/document/<int:pk>/edit/", agency_document_edit_view, name="agency_document_edit"),
    path("agency/document/<int:pk>/delete/", agency_document_delete_view, name="agency_document_delete"),
    path("agency/student/<int:student_pk>/timeline/add/", agency_timeline_create_view, name="agency_timeline_create"),
    path("agency/timeline/<int:pk>/edit/", agency_timeline_edit_view, name="agency_timeline_edit"),
    path("agency/timeline/<int:pk>/delete/", agency_timeline_delete_view, name="agency_timeline_delete"),
    path("agency/student/<int:student_pk>/academic/add/", agency_academic_create_view, name="agency_academic_create"),
    path("agency/academic/<int:pk>/edit/", agency_academic_edit_view, name="agency_academic_edit"),
    path("agency/academic/<int:pk>/delete/", agency_academic_delete_view, name="agency_academic_delete"),
    path("agency/student/<int:student_pk>/application/add/", agency_application_create_view, name="agency_application_create"),
    path("agency/application/<int:pk>/", agency_application_detail_view, name="agency_application_detail"),
    path("agency/application/<int:pk>/edit/", agency_application_edit_view, name="agency_application_edit"),
    path("agency/application/<int:pk>/delete/", agency_application_delete_view, name="agency_application_delete"),
    path("agency/application/<int:application_pk>/document/add/", agency_application_document_create_view, name="agency_application_document_create"),
    path("agency/application/<int:application_pk>/timeline/add/", agency_application_timeline_create_view, name="agency_application_timeline_create"),

path(
    "agency/student/<int:pk>/",
    agency_student_detail_view,
    name="agency_student_detail"
),

]
