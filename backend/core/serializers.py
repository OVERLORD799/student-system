from rest_framework import serializers

from core.models import Activity, Student, StudentActivity


class ActivityBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("activity_id", "name", "category", "score", "is_advanced")


class StudentActivitySerializer(serializers.ModelSerializer):
    activity = ActivityBriefSerializer(read_only=True)

    class Meta:
        model = StudentActivity
        fields = (
            "id",
            "activity",
            "actual_score",
            "participate_date",
        )
        read_only_fields = ("id",)


class StudentActivityWriteSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True)
    activity_id = serializers.CharField(write_only=True)

    class Meta:
        model = StudentActivity
        fields = (
            "student_id",
            "activity_id",
            "actual_score",
            "participate_date",
        )

    def validate_actual_score(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("实际得分不能为负数")
        return value

    def create(self, validated_data):
        sid = validated_data.pop("student_id")
        aid = validated_data.pop("activity_id")
        student = Student.objects.get(student_id=sid)
        activity = Activity.objects.get(activity_id=aid)
        return StudentActivity.objects.create(
            student=student, activity=activity, **validated_data
        )

    def update(self, instance, validated_data):
        validated_data.pop("student_id", None)
        aid = validated_data.pop("activity_id", None)
        if aid is not None:
            validated_data["activity"] = Activity.objects.get(activity_id=aid)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return StudentActivitySerializer(instance, context=self.context).data


class StudentListSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=False, allow_blank=True)
    mind_total = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True, coerce_to_string=False
    )
    art_total = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True, coerce_to_string=False
    )
    labor_total = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True, coerce_to_string=False
    )
    innovation_total = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True, coerce_to_string=False
    )

    class Meta:
        model = Student
        fields = (
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
            "remark",
        )


class StudentDetailSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=False, allow_blank=True)
    participations = StudentActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = (
            "student_id",
            "name",
            "department",
            "grade",
            "class_name",
            "academic_score",
            "quality_total",
            "comprehensive_score",
            "remark",
            "participations",
        )
        read_only_fields = ("quality_total", "comprehensive_score")


class StudentWriteSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = (
            "student_id",
            "name",
            "department",
            "grade",
            "class_name",
            "academic_score",
            "remark",
        )

    def validate_academic_score(self, value):
        if value < 0:
            raise serializers.ValidationError("学业水平成绩不能为负数")
        return value


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("activity_id", "name", "category", "score", "is_advanced")

    def validate_score(self, value):
        if value < 0:
            raise serializers.ValidationError("标准分值不能为负数")
        return value
