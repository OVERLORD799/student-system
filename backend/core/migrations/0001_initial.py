import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "activity_id",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(db_index=True, max_length=200)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("身心素养", "身心素养"),
                            ("文艺素养", "文艺素养"),
                            ("劳动素养", "劳动素养"),
                            ("创新素养", "创新素养"),
                        ],
                        max_length=20,
                    ),
                ),
                ("score", models.DecimalField(decimal_places=2, max_digits=5)),
                ("is_advanced", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "activities",
                "ordering": ["activity_id"],
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("student_id", models.CharField(max_length=20, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
                ("department", models.CharField(blank=True, default="", max_length=100)),
                ("grade", models.CharField(blank=True, default="", max_length=20)),
                (
                    "class_name",
                    models.CharField(
                        blank=True,
                        db_column="class",
                        default="",
                        max_length=50,
                        verbose_name="班级",
                    ),
                ),
                (
                    "academic_score",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                ("remark", models.TextField(blank=True, default="")),
                (
                    "quality_total",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                (
                    "comprehensive_score",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
            ],
            options={
                "db_table": "students",
                "ordering": ["student_id"],
            },
        ),
        migrations.CreateModel(
            name="StudentActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "actual_score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                ("participate_date", models.DateField(blank=True, null=True)),
                (
                    "activity",
                    models.ForeignKey(
                        db_column="activity_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.activity",
                        to_field="activity_id",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        db_column="student_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participations",
                        to="core.student",
                        to_field="student_id",
                    ),
                ),
            ],
            options={
                "db_table": "student_activities",
                "ordering": ["id"],
            },
        ),
    ]
