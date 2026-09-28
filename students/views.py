from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.text import slugify
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
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
    StudentAgreement,
)


AGREEMENT_REQUIRED_FIELDS = (
    "full_name",
    "date_of_birth",
    "gender",
    "passport_number",
    "passport_expiry",
    "address",
    "city",
    "country",
    "emergency_contact_name",
    "emergency_contact_phone",
)


def _agreement_profile_complete(profile):
    return all(getattr(profile, field) for field in AGREEMENT_REQUIRED_FIELDS)


def _agreement_value(value):
    if value in (None, ""):
        return "Not provided"
    if hasattr(value, "strftime"):
        return value.strftime("%d %B %Y")
    return str(value)


def _build_agreement_pdf(profile):
    root = Path(__file__).resolve().parent.parent
    logo_path = root / "static" / "images" / "LogoH.png"
    watermark_path = root / "static" / "images" / "Logo.png"
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=32 * mm,
        bottomMargin=47 * mm,
        title="Student Service Agreement",
        author="Global H",
    )

    navy = colors.HexColor("#12304A")
    teal = colors.HexColor("#168C82")
    muted = colors.HexColor("#526575")
    rule = colors.HexColor("#D9E2E8")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="AgreementTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=17, leading=20, textColor=navy, alignment=TA_LEFT, spaceAfter=1.5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="AgreementMeta", parent=styles["Normal"], fontSize=7.5, leading=9,
        textColor=muted, spaceAfter=3 * mm,
    ))
    styles.add(ParagraphStyle(
        name="AgreementSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=9, leading=11, textColor=navy, spaceBefore=1.5 * mm, spaceAfter=1.5 * mm,
    ))
    styles.add(ParagraphStyle(
        name="AgreementBody", parent=styles["BodyText"], fontSize=8, leading=11,
        textColor=colors.HexColor("#283746"), alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="AgreementLabel", parent=styles["Normal"], fontSize=6.4, leading=7.5,
        textColor=muted, spaceAfter=.5,
    ))
    styles.add(ParagraphStyle(
        name="AgreementValue", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=7.8, leading=9.3, textColor=navy,
    ))

    def header_footer(canvas, document):
        canvas.saveState()
        # Main brand logo in the header, separate from the pale page watermark.
        canvas.drawImage(
            logo_path,
            17 * mm,
            A4[1] - 27 * mm,
            width=47 * mm,
            height=18 * mm,
            preserveAspectRatio=True,
            anchor="sw",
            mask="auto",
        )

        # Restore the simple yellow page frame.
        canvas.setStrokeColor(colors.HexColor("#D7A92B"))
        canvas.setLineWidth(.55)
        canvas.rect(8 * mm, 8 * mm, A4[0] - 16 * mm, A4[1] - 16 * mm,
                    stroke=1, fill=0)

        # Large pale watermark behind all document content.
        canvas.saveState()
        canvas.translate(A4[0] / 2, A4[1] / 2)
        canvas.rotate(28)
        canvas.setFillAlpha(.09)
        canvas.drawImage(watermark_path, -55 * mm, -55 * mm, width=110 * mm, height=110 * mm,
                         preserveAspectRatio=True, anchor="c", mask="auto")
        canvas.restoreState()

        canvas.setFillColor(navy)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18 * mm, 42 * mm, "ACKNOWLEDGEMENT AND SIGNATURES")
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(18 * mm, 37 * mm,
                         "Both parties accept the information and terms stated in this agreement.")
        left_x, right_x = 18 * mm, A4[0] / 2 + 4 * mm
        line_width = A4[0] / 2 - 24 * mm
        canvas.setStrokeColor(navy)
        canvas.setLineWidth(.65)
        canvas.line(left_x, 28 * mm, left_x + line_width, 28 * mm)
        canvas.line(right_x, 28 * mm, right_x + line_width, 28 * mm)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica-Bold", 6.8)
        canvas.drawString(left_x, 23 * mm, "STUDENT SIGNATURE")
        canvas.drawString(right_x, 23 * mm, "AUTHORIZED REPRESENTATIVE")
        canvas.setFont("Helvetica", 6.5)
        canvas.drawString(left_x, 18 * mm, f"Name: {profile.full_name[:32]}")
        canvas.drawString(left_x, 14 * mm, f"Date: {timezone.localdate():%d %B %Y}")
        canvas.drawString(right_x, 18 * mm, "Name: ______________________________")
        canvas.drawString(right_x, 14 * mm, "Date: ______________________________")
        canvas.restoreState()

    story = [
        Paragraph("Student Service Agreement", styles["AgreementTitle"]),
        Paragraph(
            f"AGREEMENT REF. STU-{(profile.pk or 0):05d} &nbsp;&nbsp; | &nbsp;&nbsp; "
            f"ISSUED {timezone.localdate():%d %B %Y} &nbsp;&nbsp; | &nbsp;&nbsp; "
            "Please review all information before signing.", styles["AgreementMeta"]
        ),
        Paragraph("STUDENT INFORMATION", styles["AgreementSection"]),
    ]

    def field(label, value):
        return [
            Paragraph(escape(label.upper()), styles["AgreementLabel"]),
            Paragraph(escape(_agreement_value(value)), styles["AgreementValue"]),
        ]

    identity = [
        ("Full name", profile.full_name),
        ("Date of birth", profile.date_of_birth),
        ("Gender", profile.get_gender_display() if profile.gender else ""),
        ("Email", profile.user.email),
        ("Phone", profile.user.phone),
        ("Passport number", profile.passport_number),
        ("Passport expiry", profile.passport_expiry),
        ("Address", profile.address),
        ("City", profile.city),
        ("Country", profile.country),
        ("Emergency contact", profile.emergency_contact_name),
        ("Emergency phone", profile.emergency_contact_phone),
        ("Relationship", profile.emergency_contact_relation),
        ("Destination country", profile.destination_country),
        ("University", profile.university),
        ("Course / program", profile.course),
        ("Intake", profile.intake),
    ]
    table_rows = []
    for offset in range(0, len(identity), 2):
        first = identity[offset]
        second = identity[offset + 1] if offset + 1 < len(identity) else ("", "")
        table_rows.append([field(*first), field(*second)])
    identity_table = Table(
        table_rows,
        colWidths=[(A4[0] - 28 * mm) / 2] * 2,
        hAlign="LEFT",
    )
    identity_table.setStyle(TableStyle([
        # Cells remain unfilled so the pale watermark is visible underneath.
        ("BOX", (0, 0), (-1, -1), .45, rule),
        ("INNERGRID", (0, 0), (-1, -1), .35, rule),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
    ]))
    story.extend([
        identity_table,
        Spacer(1, 2 * mm),
        Paragraph("TERMS AND CONDITIONS", styles["AgreementSection"]),
        Paragraph(
            "The student agrees to pay <b>BDT 10,000 (Ten Thousand Taka)</b> as a file opening fee. "
            "This fee is <b>non-refundable</b>. After successfully obtaining a visa, the student "
            "agrees to pay the agency <b>BDT 100,000 (One Lakh Taka)</b>. All university and other "
            "application fees are the student's responsibility and must be paid by the student; "
            "the agency does not pay these fees. The student confirms that the information in this "
            "agreement is accurate to the best of their knowledge and has had the opportunity to "
            "read and understand these terms.",
            styles["AgreementBody"],
        ),
    ])
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return buffer.getvalue()

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
            "agreement_ready": _agreement_profile_complete(profile),
        }
    )


@login_required
def student_agreement_download_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if not _agreement_profile_complete(profile):
        messages.error(
            request,
            "Complete and save your name, date of birth, gender, passport details, address, and emergency contact before downloading the agreement.",
        )
        return redirect("profile")

    return _create_agreement_download_response(profile)


def _create_agreement_download_response(profile):
    pdf_bytes = _build_agreement_pdf(profile)
    base_name = slugify(profile.full_name) or "student"
    file_name = f"student-service-agreement-{base_name}-{timezone.localdate():%Y%m%d}.pdf"
    agreement = StudentAgreement.objects.create(
        student=profile,
        pdf_file=pdf_bytes,
        file_name=file_name,
    )
    response = HttpResponse(bytes(agreement.pdf_file), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{agreement.file_name}"'
    response["Content-Length"] = len(agreement.pdf_file)
    return response


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
def agency_student_agreement_download_view(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=pk)
    return _create_agreement_download_response(student)

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


