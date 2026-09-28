from .models import StudentProfile


def notification_context(request):
    unread_notification_count = 0
    recent_notifications = []
    user = getattr(request, "user", None)

    if user is not None and user.is_authenticated:
        profile = StudentProfile.objects.filter(
            user=user
        ).first()

        if profile is not None:
            recent_notifications = list(profile.notifications.all()[:5])
            unread_notification_count = profile.notifications.filter(
                is_read=False
            ).count()

    return {
        "unread_notification_count": unread_notification_count,
        "recent_notifications": recent_notifications,
    }
