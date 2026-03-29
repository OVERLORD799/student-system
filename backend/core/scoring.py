from decimal import Decimal

from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from core.models import Student, StudentActivity


def recalculate_student(student: Student) -> None:
    total = StudentActivity.objects.filter(student=student).aggregate(
        s=Sum(Coalesce(F("actual_score"), F("activity__score")))
    )["s"]
    total = total if total is not None else Decimal("0")
    if hasattr(total, "quantize"):
        total = total.quantize(Decimal("0.01"))
    acad = student.academic_score or Decimal("0")
    comp = (acad * Decimal("0.9") + total * Decimal("0.1")).quantize(Decimal("0.01"))
    Student.objects.filter(pk=student.pk).update(
        quality_total=total, comprehensive_score=comp
    )
    student.quality_total = total
    student.comprehensive_score = comp
