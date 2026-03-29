from django.urls import path
from rest_framework.routers import DefaultRouter

from core import views

router = DefaultRouter()
router.register(r"students", views.StudentViewSet, basename="student")
router.register(r"participations", views.StudentActivityViewSet, basename="participation")
router.register(r"activities", views.ActivityViewSet, basename="activity")

urlpatterns = router.urls + [
    path("import/preview/", views.import_preview),
    path("import/confirm/", views.import_confirm),
    path("export/", views.export_excel),
]
