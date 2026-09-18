from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import (
    AcademicRecord,
    Document,
    Notification,
    StudentApplication,
    StudentProfile,
    TimelineEvent,
)


TRACKED_MODELS = (
    StudentProfile,
    StudentApplication,
    AcademicRecord,
    Document,
    TimelineEvent,
)


def format_field_value(instance, field):
    value = getattr(instance, field.name)

    if field.choices:
        value = dict(field.choices).get(value, value)

    if value is None or value == "":
        return "Not set"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    return str(value)


def get_subject(instance):
    if isinstance(instance, StudentProfile):
        return instance.full_name or instance.user.username

    if isinstance(instance, AcademicRecord):
        return instance.institution

    if isinstance(instance, StudentApplication):
        return f"{instance.university} - {instance.course}"

    if isinstance(instance, Document):
        return instance.name

    return instance.title


def get_student(instance):
    if isinstance(instance, StudentProfile):
        return instance

    if isinstance(instance, StudentApplication):
        return instance.student

    return instance.student


@receiver(pre_save)
def collect_changes(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS or instance._state.adding:
        return

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    changes = []

    for field in sender._meta.concrete_fields:
        if field.primary_key or field.name in {"created_at", "updated_at"}:
            continue

        old_value = format_field_value(previous, field)
        new_value = format_field_value(instance, field)

        if old_value != new_value:
            changes.append((field.verbose_name.title(), old_value, new_value))

    instance._notification_changes = changes


@receiver(post_save)
def create_change_notification(sender, instance, created, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    changes = getattr(instance, "_notification_changes", [])
    student = get_student(instance)
    subject = get_subject(instance)

    if created:
        if isinstance(instance, StudentProfile):
            return

        if isinstance(instance, TimelineEvent):
            title = instance.title
            message = instance.description
        elif isinstance(instance, StudentApplication):
            title = f"New application: {instance.university}"
            message = f"{instance.destination_country} - {instance.course}"
        else:
            title = f"New {sender._meta.verbose_name}: {subject}"
            message = f"A new {sender._meta.verbose_name} was added for {student}."
    elif changes:
        if isinstance(instance, StudentProfile) and any(
            field_name in {"Current Status", "Progress", "Next Step"}
            for field_name, _, _ in changes
        ):
            title = "Application update"
            message_parts = ["Your agency updated your application."]

            for field_name, old_value, new_value in changes:
                if field_name == "Progress":
                    old_value = f"{old_value}%"
                    new_value = f"{new_value}%"

                message_parts.extend(
                    [
                        "",
                        field_name,
                        f"Before: {old_value}",
                        f"Now: {new_value}",
                    ]
                )

            message = "\n".join(message_parts)
        else:
            field_names = ", ".join(change[0] for change in changes)
            title = f"{subject} updated: {field_names}"
            message = "; ".join(
                f"{field_name}: {old_value} -> {new_value}"
                for field_name, old_value, new_value in changes
            )
    else:
        return

    Notification.objects.create(
        student=student,
        title=title[:200],
        message=message,
    )
