from django.contrib import admin

from .models import (
    StudentProfile,
    AcademicRecord,
    Document,
    StudentApplication,
    TimelineEvent,
    Notification,

)


@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "destination_country",
        "university",
        "course",
        "current_status",
        "progress",
    )

    list_filter = (
        "current_status",
        "destination_country",
    )

    search_fields = (
        "student__full_name",
        "student__user__username",
        "university",
        "course",
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "user",
        "gender",
        "passport_number",
        "destination_country",
        "university",
        "course",
        "current_status",
        "progress",
    )
    search_fields = (
        "full_name",
        "user__username",
        "user__email",
        "passport_number",
        "university",
    )


@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "level",
        "institution",
        "subject_or_group",
        "passing_year",
        "result",
    )

    list_filter = (
        "level",
        "passing_year",
    )

    search_fields = (
        "student__full_name",
        "institution",
        "subject_or_group",
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "student",
        "required",
        "received",
        "priority",
        "updated_at",
    )

    list_filter = (
        "required",
        "received",
        "priority",
    )

    search_fields = (
        "name",
        "student__full_name",
        "student__user__username",
    )

    list_editable = (
        "received",
        "priority",
    )

@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "title",
        "is_completed",
        "event_date",
    )

    list_filter = (
        "is_completed",
        "event_date",
    )

    search_fields = (
        "student__full_name",
        "title",
    )

    list_editable = (
        "is_completed",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "student__full_name",
        "student__user__username",
        "title",
        "message",
    )

    list_editable = (
        "is_read",
    )    