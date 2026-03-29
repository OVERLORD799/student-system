from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve

from config.spa import root_hint, spa_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
]

_frontend_dist = Path(settings.BASE_DIR).parent / "frontend" / "dist"
_index_html = _frontend_dist / "index.html"
if _frontend_dist.is_dir() and _index_html.is_file():
    urlpatterns += [
        re_path(
            r"^assets/(?P<path>.*)$",
            serve,
            {"document_root": _frontend_dist / "assets"},
        ),
        re_path(
            r"^(?!api/|admin/|static/).*$",
            spa_index,
        ),
    ]
else:
    urlpatterns += [
        path("", root_hint),
    ]
