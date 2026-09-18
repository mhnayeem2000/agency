from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .forms import (
    AcademicRecordForm,
    AgencyStudentCreateForm,
    AgencyStudentForm,
    AgencyTimelineEventForm,
    ApplicationStatusForm,
    DocumentForm,
    StudentApplicationForm,
    StudentProfileForm,
)
from .models import (
    Document,
    StudentApplication,
    StudentProfile,
    AcademicRecord,
    TimelineEvent,
)

@login_required
def profile_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("profile")

    else:

        form = StudentProfileForm(
            instance=profile
        )

    return render(
        request,
        "students/profile.html",
        {
            "form": form,
            "profile": profile,
        }
    )


@login_required
def academic_add_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = AcademicRecordForm(
            request.POST
        )

        if form.is_valid():

            academic = form.save(
                commit=False
            )

            academic.student = profile

            academic.save()

            messages.success(
                request,
                "Academic information added successfully."
            )

            return redirect("profile")

    else:

        form = AcademicRecordForm()

    return render(
        request,
        "students/academic_form.html",
        {
            "form": form,
        }
    )


@login_required
def academic_delete_view(request, pk):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    academic = AcademicRecord.objects.filter(
        id=pk,
        student=profile
    ).first()

    if academic is None:
        return redirect("profile")

    if request.method == "POST":

        academic.delete()

        messages.success(
            request,
            "Academic information removed successfully."
        )

        return redirect("profile")

    return render(
        request,
        "students/academic_confirm_delete.html",
        {
            "academic": academic,
        }
    )

@login_required
def documents_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    documents = profile.documents.all().order_by(
        "-priority",
        "name"
    )

    return render(
        request,
        "students/documents.html",
        {
            "profile": profile,
            "documents": documents,
        }
    )




@login_required
def progress_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    timeline = profile.timeline_events.all()
    journey_steps = [
        {
            "value": value,
            "label": label,
            "is_current": value == profile.current_status,
            "is_complete": index < next(
                (
                    current_index
                    for current_index, (current_value, _) in enumerate(StudentProfile.STATUS_CHOICES)
                    if current_value == profile.current_status
                ),
                0,
            ),
        }
        for index, (value, label) in enumerate(StudentProfile.STATUS_CHOICES)
    ]

    return render(
        request,
        "students/progress.html",
        {
            "profile": profile,
            "timeline": timeline,
            "journey_steps": journey_steps,
        }
    )


@login_required
def notifications_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    notifications = profile.notifications.all()

    return render(
        request,
        "students/notifications.html",
        {
            "notifications": notifications,
        }
    )




@login_required
def notification_read_view(request, pk):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    notification = profile.notifications.filter(
        id=pk
    ).first()

    if notification is None:
        return redirect("notifications")

    notification.is_read = True
    notification.save(
        update_fields=["is_read"]
    )

    return redirect("notifications")





@login_required
def dashboard_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    documents = profile.documents.all()

    urgent_documents = documents.filter(
        required=True,
        received=False,
        priority="urgent"
    )

    missing_documents = documents.filter(
        required=True,
        received=False
    )

    timeline = profile.timeline_events.all()[:5]

    notifications = profile.notifications.filter(
        is_read=False
    )[:5]

    applications = profile.applications.all()

    return render(
        request,
        "students/dashboard.html",
        {
            "profile": profile,
            "urgent_documents": urgent_documents,
            "missing_documents": missing_documents,
            "timeline": timeline,
            "notifications": notifications,
            "applications": applications,
        }
    )


@login_required
def application_detail_view(request, pk):
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )
    application = get_object_or_404(
        profile.applications,
        pk=pk,
    )

    return render(
        request,
        "students/application_detail.html",
        {
            "application": application,
            "documents": application.documents.all(),
            "timeline": application.timeline_events.all(),
        },
    )



def is_staff_user(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == "staff"
    )

@login_required
@user_passes_test(is_staff_user)
def agency_dashboard_view(request):

    students = StudentProfile.objects.select_related(
        "user"
    ).all()

    urgent_documents = Document.objects.filter(
        required=True,
        received=False,
        priority="urgent"
    ).select_related(
        "student",
        "student__user"
    )

    applications = StudentApplication.objects.select_related(
        "student",
        "student__user",
    ).all()

    return render(
        request,
        "students/agency_dashboard.html",
        {
            "students": students,
            "urgent_documents": urgent_documents,
            "applications": applications,
        }
    )


@login_required
@user_passes_test(is_staff_user)
def agency_application_create_view(request, student_pk):
    student = get_object_or_404(StudentProfile, pk=student_pk)
    form = StudentApplicationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.student = student
        application.save()
        messages.success(request, "Application file created successfully.")
        return redirect("agency_application_detail", pk=application.id)

    return render(request, "students/agency_application_form.html", {"form": form, "student": student})


@login_required
@user_passes_test(is_staff_user)
def agency_application_detail_view(request, pk):
    application = get_object_or_404(
        StudentApplication.objects.select_related("student", "student__user"),
        pk=pk,
    )
    documents = Paginator(
        application.documents.all().order_by("-priority", "name"),
        5,
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "students/agency_application_detail.html",
        {
            "application": application,
            "student": application.student,
            "documents": documents,
            "timeline": application.timeline_events.all(),
        },
    )


@login_required
@user_passes_test(is_staff_user)
def agency_application_edit_view(request, pk):
    application = get_object_or_404(StudentApplication, pk=pk)
    form = StudentApplicationForm(request.POST or None, instance=application)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Application file updated successfully.")
        return redirect("agency_application_detail", pk=application.id)

    return render(request, "students/agency_application_form.html", {"form": form, "student": application.student, "application": application})


@login_required
@user_passes_test(is_staff_user)
def agency_application_delete_view(request, pk):
    application = get_object_or_404(StudentApplication, pk=pk)

    if request.method == "POST":
        student_id = application.student_id
        application.delete()
        messages.success(request, "Application file removed successfully.")
        return redirect("agency_student_detail", pk=student_id)

    return render(request, "students/agency_delete_confirm.html", {"object": application, "object_type": "application file", "cancel_url": "agency_application_detail", "cancel_pk": application.id})


@login_required
@user_passes_test(is_staff_user)
def agency_application_document_create_view(request, application_pk):
    application = get_object_or_404(StudentApplication, pk=application_pk)
    form = DocumentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.student = application.student
        document.application = application
        document.save()
        messages.success(request, "Application document added successfully.")
        return redirect("agency_application_detail", pk=application.id)

    return render(request, "students/agency_document_form.html", {"form": form, "student": application.student, "application": application})


@login_required
@user_passes_test(is_staff_user)
def agency_application_timeline_create_view(request, application_pk):
    application = get_object_or_404(StudentApplication, pk=application_pk)
    form = AgencyTimelineEventForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.student = application.student
        event.application = application
        event.save()
        messages.success(request, "Application timeline event added successfully.")
        return redirect("agency_application_detail", pk=application.id)

    return render(request, "students/agency_timeline_form.html", {"form": form, "student": application.student, "application": application})


@login_required
@user_passes_test(is_staff_user)
def agency_student_create_view(request):

    if request.method == "POST":
        form = AgencyStudentCreateForm(request.POST)

        if form.is_valid():
            user = form.save()
            StudentProfile.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}".strip(),
            )
            messages.success(request, "Student account created successfully.")
            return redirect("agency_dashboard")
    else:
        form = AgencyStudentCreateForm()

    return render(request, "students/agency_student_form.html", {"form": form})


@login_required
@user_passes_test(is_staff_user)
def agency_student_edit_view(request, pk):

    student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=pk)

    if request.method == "POST":
        form = AgencyStudentForm(request.POST, instance=student)

        if form.is_valid():
            profile = form.save()
            profile.user.phone = form.cleaned_data["phone"]
            profile.user.save(update_fields=["phone"])
            messages.success(request, "Student profile updated successfully.")
            return redirect("agency_student_detail", pk=student.id)
    else:
        form = AgencyStudentForm(instance=student)

    return render(
        request,
        "students/agency_student_form.html",
        {"form": form, "student": student},
    )


@login_required
@user_passes_test(is_staff_user)
def agency_student_delete_view(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=pk)

    if request.method == "POST":
        student.user.delete()
        messages.success(request, "Student account removed successfully.")
        return redirect("agency_dashboard")

    return render(
        request,
        "students/agency_delete_confirm.html",
        {
            "object": student,
            "object_type": "student account",
            "cancel_url": "agency_student_detail",
            "cancel_pk": student.id,
        },
    )


@login_required
@user_passes_test(is_staff_user)
def agency_document_create_view(request, student_pk):
    student = get_object_or_404(StudentProfile, pk=student_pk)
    form = DocumentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.student = student
        document.save()
        messages.success(request, "Document added successfully.")
        return redirect("agency_student_detail", pk=student.id)

    return render(request, "students/agency_document_form.html", {"form": form, "student": student})


@login_required
@user_passes_test(is_staff_user)
def agency_document_edit_view(request, pk):
    document = get_object_or_404(Document.objects.select_related("student"), pk=pk)
    form = DocumentForm(request.POST or None, instance=document)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Document updated successfully.")
        return redirect("agency_student_detail", pk=document.student.id)

    return render(request, "students/agency_document_form.html", {"form": form, "student": document.student, "document": document})


@login_required
@user_passes_test(is_staff_user)
def agency_document_delete_view(request, pk):
    document = get_object_or_404(Document.objects.select_related("student"), pk=pk)
    student_id = document.student_id

    if request.method == "POST":
        document.delete()
        messages.success(request, "Document removed successfully.")
        return redirect("agency_student_detail", pk=student_id)

    return render(request, "students/agency_delete_confirm.html", {"object": document, "object_type": "document", "cancel_url": "agency_student_detail", "cancel_pk": student_id})


@login_required
@user_passes_test(is_staff_user)
def agency_timeline_create_view(request, student_pk):
    student = get_object_or_404(StudentProfile, pk=student_pk)
    form = AgencyTimelineEventForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.student = student
        event.save()
        messages.success(request, "Timeline event added successfully.")
        return redirect("agency_student_detail", pk=student.id)

    return render(request, "students/agency_timeline_form.html", {"form": form, "student": student})


@login_required
@user_passes_test(is_staff_user)
def agency_timeline_edit_view(request, pk):
    event = get_object_or_404(TimelineEvent.objects.select_related("student"), pk=pk)
    form = AgencyTimelineEventForm(request.POST or None, instance=event)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Timeline event updated successfully.")
        return redirect("agency_student_detail", pk=event.student.id)

    return render(request, "students/agency_timeline_form.html", {"form": form, "student": event.student, "event": event})


@login_required
@user_passes_test(is_staff_user)
def agency_timeline_delete_view(request, pk):
    event = get_object_or_404(TimelineEvent.objects.select_related("student"), pk=pk)
    student_id = event.student_id

    if request.method == "POST":
        event.delete()
        messages.success(request, "Timeline event removed successfully.")
        return redirect("agency_student_detail", pk=student_id)

    return render(request, "students/agency_delete_confirm.html", {"object": event, "object_type": "timeline event", "cancel_url": "agency_student_detail", "cancel_pk": student_id})


@login_required
@user_passes_test(is_staff_user)
def agency_academic_create_view(request, student_pk):
    student = get_object_or_404(StudentProfile, pk=student_pk)
    form = AcademicRecordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        academic = form.save(commit=False)
        academic.student = student
        academic.save()
        messages.success(request, "Academic record added successfully.")
        return redirect("agency_student_detail", pk=student.id)

    return render(request, "students/agency_academic_form.html", {"form": form, "student": student})


@login_required
@user_passes_test(is_staff_user)
def agency_academic_edit_view(request, pk):
    academic = get_object_or_404(AcademicRecord.objects.select_related("student"), pk=pk)
    form = AcademicRecordForm(request.POST or None, instance=academic)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Academic record updated successfully.")
        return redirect("agency_student_detail", pk=academic.student.id)

    return render(request, "students/agency_academic_form.html", {"form": form, "student": academic.student, "academic": academic})


@login_required
@user_passes_test(is_staff_user)
def agency_academic_delete_view(request, pk):
    academic = get_object_or_404(AcademicRecord.objects.select_related("student"), pk=pk)
    student_id = academic.student_id

    if request.method == "POST":
        academic.delete()
        messages.success(request, "Academic record removed successfully.")
        return redirect("agency_student_detail", pk=student_id)

    return render(request, "students/agency_delete_confirm.html", {"object": academic, "object_type": "academic record", "cancel_url": "agency_student_detail", "cancel_pk": student_id})





@login_required
@user_passes_test(is_staff_user)
def agency_student_detail_view(request, pk):

    student = get_object_or_404(
        StudentProfile.objects.select_related("user"),
        pk=pk
    )

    if request.method == "POST":

        form = ApplicationStatusForm(
            request.POST,
            instance=student
        )

        if form.is_valid():

            form.save()
            messages.success(
                request,
                "Application updated successfully. Your changes have been saved."
            )
            return redirect(
                "agency_student_detail",
                pk=student.id
            )

    else:

        form = ApplicationStatusForm(
            instance=student
        )


    documents = Paginator(
        student.documents.all().order_by("-priority", "name"),
        5,
    ).get_page(request.GET.get("page"))

    timeline = student.timeline_events.all()

    return render(
        request,
        "students/agency_student_detail.html",
        {
            "student": student,
            "documents": documents,
            "timeline": timeline,
            "form": form,
        }
    )


