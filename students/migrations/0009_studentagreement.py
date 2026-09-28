from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0008_alter_studentapplication_current_status_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentAgreement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pdf_file", models.BinaryField()),
                ("file_name", models.CharField(max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="agreements", to="students.studentprofile")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
