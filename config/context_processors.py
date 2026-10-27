from django.conf import settings


def site_metadata(request):
    return {"site_url": settings.PUBLIC_SITE_URL}
