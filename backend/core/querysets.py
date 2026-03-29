from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce

from core.models import Activity, Student


def _line_score_expr():
    return Coalesce(
        F("participations__actual_score"),
        F("participations__activity__score"),
        output_field=DecimalField(max_digits=5, decimal_places=2),
    )


def students_with_category_totals(queryset=None):
    qs = queryset if queryset is not None else Student.objects.all()
    line = _line_score_expr()
    dec7 = DecimalField(max_digits=7, decimal_places=2)
    return qs.annotate(
        mind_total=Coalesce(
            Sum(
                line,
                filter=Q(participations__activity__category=Activity.CATEGORY_MIND),
            ),
            Value(0),
            output_field=dec7,
        ),
        art_total=Coalesce(
            Sum(
                line,
                filter=Q(participations__activity__category=Activity.CATEGORY_ART),
            ),
            Value(0),
            output_field=dec7,
        ),
        labor_total=Coalesce(
            Sum(
                line,
                filter=Q(participations__activity__category=Activity.CATEGORY_LABOR),
            ),
            Value(0),
            output_field=dec7,
        ),
        innovation_total=Coalesce(
            Sum(
                line,
                filter=Q(participations__activity__category=Activity.CATEGORY_INNOVATION),
            ),
            Value(0),
            output_field=dec7,
        ),
    )
