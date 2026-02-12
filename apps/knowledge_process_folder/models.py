from django.db import models
from django.conf import settings
from django.utils import timezone 
import os

User = settings.AUTH_USER_MODEL
class KnowledgeDocument(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    OCR_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to="knowledge/documents/")
    modules = models.JSONField(default=list) 
    expiry_date = models.DateField(null=True, blank=True)

    document_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Auto-detected file type (pdf, png, jpg, etc.)",
    )

    document_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Auto-detected file size in bytes",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    rejection_reason = models.TextField(null=True, blank=True)

    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_rejected_documents",
    )

    rejected_at = models.DateTimeField(null=True, blank=True)
    ocr_status = models.CharField(
        max_length=20,
        choices=OCR_STATUS_CHOICES,
        default="pending",
    )

    ocr_accuracy = models.FloatField(null=True, blank=True)
    extracted_text = models.TextField(blank=True)

    ocr_failure_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Exact reason why OCR failed (system generated)",
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="knowledge_uploaded_documents",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_approved_documents",
    )

    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_deleted_documents",
        help_text="User who soft-deleted the document",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["ocr_status"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["document_type"]),
        ]

    def save(self, *args, **kwargs):
        if self.document_file:
            if not self.document_type:
                self.document_type = (
                    os.path.splitext(self.document_file.name)[1]
                    .replace(".", "")
                    .lower()
                )

            if not self.document_size:
                try:
                    self.document_size = self.document_file.size
                except Exception:
                    pass

        super().save(*args, **kwargs)
    @property
    def is_expired(self):
        return bool(
            self.expiry_date
            and self.expiry_date < timezone.now().date()
        )

    def __str__(self):
        return self.document_name
class KnowledgeWebsite(models.Model):
    SCRAPING_TYPE_CHOICES = [
        ("static", "Static"),
        ("dynamic", "Dynamic"),
    ]

    SCRAPING_FREQUENCY_CHOICES = [
        ("hourly", "Hourly"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    SCRAPING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=255)
    url = models.URLField()

    scraping_type = models.CharField(
        max_length=20,
        choices=SCRAPING_TYPE_CHOICES,
        default="static",
    )

    scraping_frequency = models.CharField(
        max_length=20,
        choices=SCRAPING_FREQUENCY_CHOICES,
        default="daily",
    )

    extracted_text = models.TextField(blank=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )
    scraping_status = models.CharField(
        max_length=20,
        choices=SCRAPING_STATUS_CHOICES,
        default="pending",
        help_text="Tracks background scraping state",
    )

    scraping_failure_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for scraping failure (system generated)",
    )

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="knowledge_websites",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["scraping_status"]),  
        ]

    def __str__(self):
        return self.name

class DocumentModule(models.Model):

    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Document Module"
        verbose_name_plural = "Document Modules"

    def __str__(self):
        return self.name