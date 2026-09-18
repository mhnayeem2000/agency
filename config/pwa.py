from pathlib import Path

from django.conf import settings
from django.http import HttpResponse


def service_worker_view(request):
    service_worker_path = Path(settings.BASE_DIR) / "static" / "pwa" / "service-worker.js"
    service_worker = service_worker_path.read_text(encoding="utf-8")

    return HttpResponse(
        service_worker,
        content_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


def manifest_view(request):
    manifest_path = Path(settings.BASE_DIR) / "static" / "pwa" / "manifest.json"
    manifest = manifest_path.read_text(encoding="utf-8")

    return HttpResponse(
        manifest,
        content_type="application/manifest+json",
    )
