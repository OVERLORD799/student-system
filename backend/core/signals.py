from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.models import Student, StudentActivity
from core.scoring import recalculate_student


@receiver(post_save, sender=StudentActivity)
@receiver(post_delete, sender=StudentActivity)
def participation_changed(sender, instance, **kwargs):
    recalculate_student(instance.student)


@receiver(post_save, sender=Student)
def student_saved(sender, instance, **kwargs):
    recalculate_student(instance)
