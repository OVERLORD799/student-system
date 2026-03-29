from django.contrib import admin

from core.models import Activity, Student, StudentActivity


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "name",
        "department",
        "grade",
        "class_name",
        "academic_score",
        "quality_total",
        "comprehensive_score",
    )
    search_fields = ("student_id", "name")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("activity_id", "name", "category", "score", "is_advanced")
    list_filter = ("category",)


@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "activity", "actual_score", "participate_date")
    list_filter = ("activity__category",)
