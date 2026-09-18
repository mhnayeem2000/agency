from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User

from .models import (
    StudentApplication,
    StudentProfile,
    AcademicRecord,
    Document,
    TimelineEvent,
)

class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = StudentProfile

        fields = (
            "full_name",
            "date_of_birth",
            "gender",

            "passport_number",
            "passport_expiry",

            "address",
            "city",
            "country",
            "drive_link",


            "destination_country",
            "university",
            "course",
            "intake",

            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
        )

        widgets = {

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "passport_expiry": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "rows": 4
                }
            ),
        }


class AcademicRecordForm(forms.ModelForm):

    class Meta:
        model = AcademicRecord

        fields = (
            "level",
            "institution",
            "subject_or_group",
            "passing_year",
            "result",
            "certificate_note",
        )

        widgets = {

            "certificate_note": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Any additional information..."
                }
            ),
        }




class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document

        fields = (
            "name",
            "required",
            "received",
            "priority",
            "note",
        )

        widgets = {

            "note": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Any note about this document..."
                }
            ),
        }

class ApplicationStatusForm(forms.ModelForm):

    class Meta:
        model = StudentProfile

        fields = (
            "current_status",
            "progress",
            "next_step",
        )

        widgets = {

            "next_step": forms.TextInput(
                attrs={
                    "placeholder": "What should happen next?"
                }
            ),

        }


class AgencyStudentForm(StudentProfileForm):

    class Meta(StudentProfileForm.Meta):
        fields = StudentProfileForm.Meta.fields

    phone = forms.CharField(
        required=False,
        max_length=20,
        label="Phone",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["phone"].initial = self.instance.user.phone


class AgencyStudentCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "student"

        if commit:
            user.save()

        return user


class AgencyTimelineEventForm(forms.ModelForm):

    class Meta:
        model = TimelineEvent
        fields = (
            "title",
            "description",
            "is_completed",
            "event_date",
        )

        widgets = {
            "event_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }


class StudentApplicationForm(forms.ModelForm):

    class Meta:
        model = StudentApplication
        fields = (
            "destination_country",
            "university",
            "course",
            "intake",
            "drive_link",
            "current_status",
            "progress",
            "next_step",
        )

        widgets = {
            "next_step": forms.TextInput(
                attrs={"placeholder": "What should happen next?"}
            ),
        }