from django.db import models


class Activity(models.Model):
    CATEGORY_MIND = "身心素养"
    CATEGORY_ART = "文艺素养"
    CATEGORY_LABOR = "劳动素养"
    CATEGORY_INNOVATION = "创新素养"
    CATEGORY_CHOICES = [
        (CATEGORY_MIND, CATEGORY_MIND),
        (CATEGORY_ART, CATEGORY_ART),
        (CATEGORY_LABOR, CATEGORY_LABOR),
        (CATEGORY_INNOVATION, CATEGORY_INNOVATION),
    ]

    activity_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    is_advanced = models.BooleanField(default=False)

    class Meta:
        db_table = "activities"
        ordering = ["activity_id"]

    def __str__(self):
        return f"{self.activity_id} {self.name}"


class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=100, blank=True, default="")
    grade = models.CharField(max_length=20, blank=True, default="")
    class_name = models.CharField("班级", max_length=50, db_column="class", blank=True, default="")
    academic_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remark = models.TextField(blank=True, default="")
    quality_total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    comprehensive_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = "students"
        ordering = ["student_id"]

    def __str__(self):
        return f"{self.student_id} {self.name}"


class StudentActivity(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="participations",
        db_column="student_id",
        to_field="student_id",
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.PROTECT,
        db_column="activity_id",
        to_field="activity_id",
    )
    actual_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    participate_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "student_activities"
        ordering = ["id"]
