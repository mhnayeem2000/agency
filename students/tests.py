from django.test import TestCase

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
	Document,
	Notification,
	StudentApplication,
	StudentProfile,
	TimelineEvent,
)


class TimelineNotificationTests(TestCase):

	def setUp(self):
		user = get_user_model().objects.create_user(
			username="timeline_student",
			password="test-password",
		)
		self.profile = StudentProfile.objects.create(
			user=user,
			full_name="Timeline Student",
		)

	def test_new_timeline_event_creates_one_notification(self):
		event = TimelineEvent.objects.create(
			student=self.profile,
			title="Passport received",
			description="Passport documents were received.",
			event_date=timezone.now(),
		)

		notification = Notification.objects.get(student=self.profile)

		self.assertEqual(Notification.objects.count(), 1)
		self.assertEqual(notification.title, event.title)
		self.assertEqual(notification.message, event.description)
		self.assertFalse(notification.is_read)

		event.title = "Passport verified"
		event.save()

		update_notification = Notification.objects.latest("created_at")

		self.assertEqual(Notification.objects.count(), 2)
		self.assertEqual(
			update_notification.title,
			"Passport verified updated: Title",
		)
		self.assertIn("Title: Passport received -> Passport verified", update_notification.message)

	def test_profile_update_creates_dynamic_notification(self):
		self.profile.full_name = "Updated Student Name"
		self.profile.save()

		notification = Notification.objects.get(student=self.profile)

		self.assertEqual(notification.title, "Updated Student Name updated: Full Name")
		self.assertIn(
			"Full Name: Timeline Student -> Updated Student Name",
			notification.message,
		)

	def test_document_update_creates_dynamic_notification(self):
		document = Document.objects.create(
			student=self.profile,
			name="Passport",
		)
		document.received = True
		document.save()

		notification = Notification.objects.filter(
		student=self.profile
		).latest("created_at")

		self.assertEqual(
			notification.title,
			"Passport updated: Received",
		)
		self.assertIn("Received: No -> Yes", notification.message)

	def test_student_can_have_isolated_application_files(self):
		first = StudentApplication.objects.create(
			student=self.profile,
			destination_country="Canada",
			university="North University",
			course="Computer Science",
		)
		second = StudentApplication.objects.create(
			student=self.profile,
			destination_country="Germany",
			university="Berlin University",
			course="Business Analytics",
		)

		first_document = Document.objects.create(
			student=self.profile,
			application=first,
			name="Canada passport",
		)
		second_document = Document.objects.create(
			student=self.profile,
			application=second,
			name="Germany passport",
		)

		self.assertEqual(self.profile.applications.count(), 2)
		self.assertEqual(list(first.documents.all()), [first_document])
		self.assertEqual(list(second.documents.all()), [second_document])
