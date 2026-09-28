from django.conf import settings
from django.db import models


class StudentProfile(models.Model):

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    full_name = models.CharField(
        max_length=150,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )

    passport_number = models.CharField(
        max_length=50,
        blank=True
    )

    passport_expiry = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )
    drive_link = models.URLField(
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="Bangladesh"
    )


    STATUS_CHOICES = (
        ("registered", "Profile Registered"),
        ("verification", "Profile Verification & File Preparation"),
        ("documents", "Document Collection & Review"),
        ("professor_outreach", "Professor Outreach & Acceptance Process (For Master's/Research Programs)"),
        ("application", "University Application In Progress"),
        ("interview", "Interview Preparation / Interview Scheduled"),
        ("offer", "Admission Offer & Official Documents Received"),
        ("visa_processing", "Visa Application Processing"),
        ("visa_approved", "Visa Approved"),
        ("pre_departure", "Pre-Departure Preparation & Ready to Fly"),
    )

    STATUS_PROGRESS = {
        "registered": 5,
        "verification": 20,
        "documents": 30,
        "professor_outreach": 30,
        "application": 40,
        "interview": 50,
        "offer": 90,
        "visa_processing": 95,
        "visa_approved": 100,
        "pre_departure": 100,
    }

    current_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="registered"
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    next_step = models.CharField(
        max_length=255,
        blank=True
    )

    def save(self, *args, **kwargs):
        self.progress = self.STATUS_PROGRESS.get(self.current_status, 5)
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"progress"}
        super().save(*args, **kwargs)

    destination_country = models.CharField(
        max_length=100,
        blank=True
    )

    university = models.CharField(
        max_length=200,
        blank=True
    )

    course = models.CharField(
        max_length=200,
        blank=True
    )

    intake = models.CharField(
        max_length=100,
        blank=True
    )

    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True
    )

    emergency_contact_phone = models.CharField(
        max_length=30,
        blank=True
    )

    emergency_contact_relation = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.full_name or self.user.username


class StudentAgreement(models.Model):
    """A generated, downloadable snapshot of a student's service agreement."""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="agreements",
    )
    pdf_file = models.BinaryField()
    file_name = models.CharField(max_length=180)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Agreement for {self.student} ({self.created_at:%Y-%m-%d})"


class StudentApplication(models.Model):

    STATUS_CHOICES = StudentProfile.STATUS_CHOICES

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    destination_country = models.CharField(max_length=100)
    university = models.CharField(max_length=200)
    course = models.CharField(max_length=200)
    intake = models.CharField(max_length=100, blank=True)
    drive_link = models.URLField(blank=True)

    current_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="registered"
    )

    progress = models.PositiveIntegerField(default=0)
    next_step = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-created_at")

    def save(self, *args, **kwargs):
        self.progress = StudentProfile.STATUS_PROGRESS.get(self.current_status, 5)
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"progress"}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.university} - {self.course}"


class AcademicRecord(models.Model):

    LEVEL_CHOICES = (
        ("ssc", "SSC"),
        ("hsc", "HSC"),
        ("diploma", "Diploma"),
        ("bachelor", "Bachelor"),
        ("master", "Master"),
        ("other", "Other"),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="academic_records"
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )

    institution = models.CharField(
        max_length=200
    )

    subject_or_group = models.CharField(
        max_length=150,
        blank=True
    )

    passing_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    result = models.CharField(
        max_length=50,
        blank=True
    )

    certificate_note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student} - {self.get_level_display()}"



class Document(models.Model):

    PRIORITY_CHOICES = (
        ("normal", "Normal"),
        ("urgent", "Urgent"),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    application = models.ForeignKey(
        StudentApplication,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=200
    )

    required = models.BooleanField(
        default=True
    )

    received = models.BooleanField(
        default=False
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="normal"
    )

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student} - {self.name}"


class TimelineEvent(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="timeline_events"
    )

    application = models.ForeignKey(
        StudentApplication,
        on_delete=models.CASCADE,
        related_name="timeline_events",
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    is_completed = models.BooleanField(
        default=False
    )

    event_date = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-event_date"]

    def __str__(self):
        return f"{self.student} - {self.title}"




class Notification(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.title}"
