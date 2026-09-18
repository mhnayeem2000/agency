from .models import StudentProfile


def notification_context(request):
    unread_notification_count = 0
    user = getattr(request, "user", None)

    if user is not None and user.is_authenticated:
        profile = StudentProfile.objects.filter(
            user=user
        ).first()

        if profile is not None:
            unread_notification_count = profile.notifications.filter(
                is_read=False
            ).count()

    return {
        "unread_notification_count": unread_notification_count,
    }
