import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from django.core.cache import cache
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.excel_io import (
    apply_import,
    build_conflict_preview,
    export_workbook,
    parse_import_workbook,
)
from core.logging_utils import append_error_log
from core.models import Activity, Student, StudentActivity
from core.querysets import students_with_category_totals
from core.serializers import (
    ActivitySerializer,
    StudentActivitySerializer,
    StudentActivityWriteSerializer,
    StudentDetailSerializer,
    StudentListSerializer,
    StudentWriteSerializer,
)

SORT_FIELDS = {
    "student_id",
    "name",
    "department",
    "grade",
    "class_name",
    "academic_score",
    "mind_total",
    "art_total",
    "labor_total",
    "innovation_total",
    "quality_total",
    "comprehensive_score",
}


def _parse_decimal(val):
    if val is None or val == "":
        return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        return None


def apply_student_filters(qs, request):
    grade = request.query_params.get("grade")
    if grade:
        qs = qs.filter(grade=grade)
    class_name = request.query_params.get("class")
    if class_name:
        qs = qs.filter(class_name=class_name)
    sid_min = request.query_params.get("student_id_min")
    sid_max = request.query_params.get("student_id_max")
    if sid_min:
        qs = qs.filter(student_id__gte=sid_min)
    if sid_max:
        qs = qs.filter(student_id__lte=sid_max)

    pairs = [
        ("mind_min", "mind_max", "mind_total"),
        ("art_min", "art_max", "art_total"),
        ("labor_min", "labor_max", "labor_total"),
        ("innovation_min", "innovation_max", "innovation_total"),
    ]
    for lo_key, hi_key, field in pairs:
        lo = _parse_decimal(request.query_params.get(lo_key))
        hi = _parse_decimal(request.query_params.get(hi_key))
        if lo is not None:
            qs = qs.filter(**{f"{field}__gte": lo})
        if hi is not None:
            qs = qs.filter(**{f"{field}__lte": hi})

    qmin = _parse_decimal(request.query_params.get("quality_min"))
    qmax = _parse_decimal(request.query_params.get("quality_max"))
    if qmin is not None:
        qs = qs.filter(quality_total__gte=qmin)
    if qmax is not None:
        qs = qs.filter(quality_total__lte=qmax)

    cmin = _parse_decimal(request.query_params.get("comprehensive_min"))
    cmax = _parse_decimal(request.query_params.get("comprehensive_max"))
    if cmin is not None:
        qs = qs.filter(comprehensive_score__gte=cmin)
    if cmax is not None:
        qs = qs.filter(comprehensive_score__lte=cmax)
    return qs


def apply_student_sort(qs, request):
    sort = request.query_params.get("sort") or "student_id"
    desc = sort.startswith("-")
    field = sort[1:] if desc else sort
    if field not in SORT_FIELDS:
        field = "student_id"
        desc = False
    prefix = "-" if desc else ""
    return qs.order_by(f"{prefix}{field}", "student_id")


class StudentViewSet(viewsets.ModelViewSet):
    lookup_field = "student_id"
    lookup_value_regex = "[^/]+"

    def get_queryset(self):
        base = Student.objects.all()
        if self.action == "list":
            qs = students_with_category_totals(base)
            qs = apply_student_filters(qs, self.request)
            return apply_student_sort(qs, self.request)
        return base.prefetch_related("participations__activity")

    def get_serializer_class(self):
        if self.action == "list":
            return StudentListSerializer
        if self.action in ("create", "update", "partial_update"):
            return StudentWriteSerializer
        return StudentDetailSerializer


class StudentActivityViewSet(viewsets.ModelViewSet):
    queryset = StudentActivity.objects.select_related("student", "activity").all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return StudentActivityWriteSerializer
        return StudentActivitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        sid = self.request.query_params.get("student_id")
        if sid:
            qs = qs.filter(student_id=sid)
        cat = self.request.query_params.get("category")
        if cat:
            qs = qs.filter(activity__category=cat)
        return qs.order_by("id")


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    lookup_field = "activity_id"
    lookup_value_regex = "[^/]+"

    def destroy(self, request, *args, **kwargs):
        cascade = request.query_params.get("cascade") == "1"
        instance = self.get_object()
        if cascade:
            StudentActivity.objects.filter(activity=instance).delete()
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": "存在学生参与记录，已阻止删除。可在请求中附加查询参数 cascade=1 以级联删除相关记录后再删除活动。"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["POST"])
@parser_classes([MultiPartParser])
def import_preview(request):
    f = request.FILES.get("file")
    if not f:
        return Response({"detail": "请选择文件"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        raw = f.read()
        rows, row_errors = parse_import_workbook(raw)
        if row_errors:
            append_error_log(f"导入解析行错误: {row_errors[:20]}")
            return Response(
                {"detail": "部分行解析失败", "row_errors": row_errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = str(uuid.uuid4())
        cache.set(f"import_preview:{token}", rows, timeout=3600)
        conflicts = build_conflict_preview(rows)
        return Response({"token": token, "conflicts": conflicts, "row_count": len(rows)})
    except Exception as exc:
        append_error_log("导入预览失败", exc)
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def import_confirm(request):
    token = request.data.get("token")
    resolutions = request.data.get("resolutions") or {}
    if not token:
        return Response({"detail": "缺少 token"}, status=status.HTTP_400_BAD_REQUEST)
    rows = cache.get(f"import_preview:{token}")
    if not rows:
        return Response(
            {"detail": "预览已过期，请重新上传"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(resolutions, dict):
        return Response({"detail": "resolutions 格式错误"}, status=status.HTTP_400_BAD_REQUEST)
    cache_key = f"import_preview:{token}"
    try:
        imported, skipped, errors = apply_import(rows, resolutions)
        return Response(
            {"imported": imported, "skipped": skipped, "errors": errors},
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        append_error_log("导入执行失败", exc)
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    finally:
        cache.delete(cache_key)


@api_view(["GET"])
def export_excel(request):
    qs = students_with_category_totals(Student.objects.all())
    qs = apply_student_filters(qs, request)
    qs = apply_student_sort(qs, request)
    ids = list(qs.values_list("student_id", flat=True))
    parts = (
        StudentActivity.objects.filter(student_id__in=ids)
        .select_related("student", "activity")
        .order_by("student_id", "id")
    )
    try:
        data = export_workbook(qs, parts)
    except Exception as exc:
        append_error_log("导出失败", exc)
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    name = f"学生综测导出_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    resp = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = (
        "attachment; filename*=UTF-8''" + quote(name, safe="")
    )
    return resp
